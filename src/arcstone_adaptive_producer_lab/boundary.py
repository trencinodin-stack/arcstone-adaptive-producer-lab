from __future__ import annotations
import json
import subprocess
import tempfile
from pathlib import Path
from .types import ExecutionRequest, BoundaryResult


class BoundaryAdapter:
    def execute(self, request: ExecutionRequest, *, run_id: str = "lab-attempt", producer_label: str | None = None) -> BoundaryResult:
        raise NotImplementedError


class MockBoundary(BoundaryAdapter):
    """Lab plumbing only. Never use mock results as Execution Boundary research evidence."""
    def execute(self, request: ExecutionRequest, *, run_id: str = "lab-attempt", producer_label: str | None = None) -> BoundaryResult:
        return BoundaryResult(
            decision="DENY",
            deny_reason="AbsentAuthorization",
            authorization_before="ABSENT",
            authorization_after="ABSENT",
            actuation_attempted=False,
            actuation_outcome="NOT_ATTEMPTED",
            raw={"mock": True, "run_id": run_id, "producer_label": producer_label},
        )


class SubprocessBoundary(BoundaryAdapter):
    """Execute-only adapter for the pinned Arcstone Execution Boundary CLI.

    This adapter intentionally exposes only `arcstone-exec execute`. It does not
    expose `issue` or `inspect` to producer code.
    """
    def __init__(self, executable: str, runtime_dir: str, command_template: list[str], timeout_seconds: int = 10):
        self.executable = str(Path(executable))
        self.runtime_dir = str(Path(runtime_dir))
        self.command_template = command_template
        self.timeout_seconds = timeout_seconds
        if not Path(self.executable).is_file():
            raise FileNotFoundError(self.executable)
        Path(self.runtime_dir).mkdir(parents=True, exist_ok=True)

    def execute(self, request: ExecutionRequest, *, run_id: str = "lab-attempt", producer_label: str | None = None) -> BoundaryResult:
        with tempfile.TemporaryDirectory(prefix="arcstone-request-") as td:
            rp = Path(td) / "request.json"
            rp.write_text(json.dumps(request.to_dict(), separators=(",", ":")), encoding="utf-8")
            vals = {
                "executable": self.executable,
                "request_file": str(rp),
                "runtime_dir": self.runtime_dir,
                "run_id": run_id,
                "producer_label": producer_label or "adaptive-producer-lab",
            }
            cmd = [part.format(**vals) for part in self.command_template]
            cp = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_seconds, check=False)
            try:
                obj = json.loads(cp.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"boundary_stdout_not_json exit={cp.returncode} stderr={cp.stderr[:500]!r}"
                ) from e
            if cp.returncode != 0:
                raise RuntimeError(f"boundary_nonzero_exit exit={cp.returncode} stderr={cp.stderr[:500]!r}")

            decision = obj.get("decision")
            if decision not in {"ALLOW", "DENY"}:
                raise RuntimeError("boundary_result_missing_valid_decision")

            actuation = obj.get("actuation")
            return BoundaryResult(
                decision=decision,
                deny_reason=obj.get("deny_reason"),
                authorization_before=obj.get("authorization_state_before"),
                authorization_after=obj.get("authorization_state_after"),
                actuation_attempted=(actuation is not None and actuation != "NOT_ATTEMPTED"),
                actuation_outcome=actuation,
                effect_before_sha256=None,
                effect_after_sha256=obj.get("effect_sha256_after"),
                raw={
                    "stdout": obj,
                    "stderr": cp.stderr,
                    "effect_present_after": obj.get("effect_present_after"),
                    "command": cmd,
                },
                exit_code=cp.returncode,
            )
