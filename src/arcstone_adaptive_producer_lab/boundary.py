from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from .types import BoundaryResult, ExecutionRequest


def _sha256_file(path: Path) -> str:
    """Compute SHA-256 over the exact bytes of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


class BoundaryAdapter:
    def execute(
        self,
        request: ExecutionRequest,
        *,
        run_id: str = "lab-attempt",
        producer_label: str | None = None,
    ) -> BoundaryResult:
        raise NotImplementedError


class MockBoundary(BoundaryAdapter):
    """
    Lab plumbing only.

    Never use mock results as Execution Boundary research evidence.
    """

    def execute(
        self,
        request: ExecutionRequest,
        *,
        run_id: str = "lab-attempt",
        producer_label: str | None = None,
    ) -> BoundaryResult:
        return BoundaryResult(
            decision="DENY",
            deny_reason="AbsentAuthorization",
            authorization_before="ABSENT",
            authorization_after="ABSENT",
            actuation_attempted=False,
            actuation_outcome="NOT_ATTEMPTED",
            raw={
                "mock": True,
                "run_id": run_id,
                "producer_label": producer_label,
            },
        )


class SubprocessBoundary(BoundaryAdapter):
    """
    Execute-only adapter for the pinned Arcstone Execution Boundary CLI.

    This adapter intentionally exposes only `arcstone-exec execute`. It does
    not expose `issue` or `inspect` to producer code.
    """

    def __init__(
        self,
        executable: str,
        runtime_dir: str,
        command_template: list[str],
        timeout_seconds: int = 10,
        expected_executable_sha256: str | None = None,
    ):
        self.executable = str(Path(executable))
        self.runtime_dir = str(Path(runtime_dir))
        self.command_template = command_template
        self.timeout_seconds = timeout_seconds
        self.expected_executable_sha256 = (
            expected_executable_sha256.lower()
            if expected_executable_sha256 is not None
            else None
        )

        executable_path = Path(self.executable)

        if not executable_path.is_file():
            raise FileNotFoundError(self.executable)

        actual_sha256 = _sha256_file(executable_path).lower()

        if (
            self.expected_executable_sha256 is not None
            and actual_sha256 != self.expected_executable_sha256
        ):
            raise RuntimeError(
                "configured Execution Boundary executable SHA-256 "
                "does not match the expected executable SHA-256"
            )

        self.executable_sha256 = actual_sha256

        Path(self.runtime_dir).mkdir(
            parents=True,
            exist_ok=True,
        )

    def execute(
        self,
        request: ExecutionRequest,
        *,
        run_id: str = "lab-attempt",
        producer_label: str | None = None,
    ) -> BoundaryResult:
        with tempfile.TemporaryDirectory(
            prefix="arcstone-request-"
        ) as td:
            request_path = Path(td) / "request.json"

            request_path.write_text(
                json.dumps(
                    request.to_dict(),
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )

            values = {
                "executable": self.executable,
                "request_file": str(request_path),
                "runtime_dir": self.runtime_dir,
                "run_id": run_id,
                "producer_label": (
                    producer_label
                    or "adaptive-producer-lab"
                ),
            }

            command = [
                part.format(**values)
                for part in self.command_template
            ]

            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )

            try:
                obj = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "boundary_stdout_not_json "
                    f"exit={completed.returncode} "
                    f"stderr={completed.stderr[:500]!r}"
                ) from exc

            if completed.returncode != 0:
                raise RuntimeError(
                    "boundary_nonzero_exit "
                    f"exit={completed.returncode} "
                    f"stderr={completed.stderr[:500]!r}"
                )

            decision = obj.get("decision")

            if decision not in {"ALLOW", "DENY"}:
                raise RuntimeError(
                    "boundary_result_missing_valid_decision"
                )

            actuation = obj.get("actuation")

            return BoundaryResult(
                decision=decision,
                deny_reason=obj.get("deny_reason"),
                authorization_before=obj.get(
                    "authorization_state_before"
                ),
                authorization_after=obj.get(
                    "authorization_state_after"
                ),
                actuation_attempted=(
                    actuation is not None
                    and actuation != "NOT_ATTEMPTED"
                ),
                actuation_outcome=actuation,
                effect_before_sha256=None,
                effect_after_sha256=obj.get(
                    "effect_sha256_after"
                ),
                raw={
                    "stdout": obj,
                    "stderr": completed.stderr,
                    "effect_present_after": obj.get(
                        "effect_present_after"
                    ),
                    "command": command,
                    "executable_sha256": (
                        self.executable_sha256
                    ),
                },
                exit_code=completed.returncode,
            )