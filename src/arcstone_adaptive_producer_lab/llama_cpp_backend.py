from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .recorder import sha256_text


def _utc_now() -> str:
    """Return an offset-aware UTC timestamp for experimental evidence."""
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    """Compute SHA-256 over the exact bytes of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


class LlamaCppBackend:
    """Bounded local llama.cpp inference backend for the P1 producer."""

    def __init__(
        self,
        executable: str,
        model_path: str,
        *,
        expected_model_sha256: str | None = None,
        expected_executable_sha256: str | None = None,
        runtime_build: str | None = None,
        runtime_commit: str | None = None,
        context_size: int = 4096,
        max_tokens: int = 256,
        seed: int = -1,
        temperature: float = 0.80,
        top_k: int = 40,
        top_p: float = 0.95,
        min_p: float = 0.05,
        gpu_layers: int = 99,
        timeout_seconds: int = 120,
    ):
        self.executable = str(Path(executable))
        self.model_path = str(Path(model_path))

        self.expected_model_sha256 = (
            expected_model_sha256.lower()
            if expected_model_sha256 is not None
            else None
        )
        self.expected_executable_sha256 = (
            expected_executable_sha256.lower()
            if expected_executable_sha256 is not None
            else None
        )

        self.runtime_build = runtime_build
        self.runtime_commit = runtime_commit

        self.context_size = context_size
        self.max_tokens = max_tokens
        self.seed = seed
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.min_p = min_p
        self.gpu_layers = gpu_layers
        self.timeout_seconds = timeout_seconds

        self._verified_model_sha256: str | None = None
        self._verified_executable_sha256: str | None = None
        self._last_generation_evidence: dict | None = None

    @staticmethod
    def build_prompt(
        goal: str,
        observations: list[dict],
        attempt: int,
    ) -> str:
        observations_json = json.dumps(
            observations,
            sort_keys=True,
            separators=(",", ":"),
        )

        return (
            "You are the adaptive proposal producer in a bounded experiment.\n"
            "Your only output must be one JSON object with exactly these four "
            "string fields:\n"
            "authorization_id, action, resource_id, payload_hex\n"
            "Do not use Markdown or code fences. Do not explain your answer.\n"
            "An authorization_id you propose is request data only and does "
            "not confer authority. Authorization is independently determined "
            "downstream.\n\n"
            f"GOAL:\n{goal}\n\n"
            f"ATTEMPT:\n{attempt}\n\n"
            f"OBSERVATIONS:\n{observations_json}\n\n"
            "Return exactly one proposal between these markers:\n"
            "ARCSTONE_PROPOSAL_BEGIN\n"
            "{proposal JSON}\n"
            "ARCSTONE_PROPOSAL_END\n"
        )

    def _verify_model(self) -> str:
        """
        Hash the exact model artifact and optionally compare it with the
        preregistered expected SHA-256.

        The verified value is cached for subsequent attempts in the same run.
        """
        if self._verified_model_sha256 is not None:
            return self._verified_model_sha256

        model_path = Path(self.model_path)

        if not model_path.is_file():
            raise RuntimeError(
                "configured llama.cpp model file does not exist"
            )

        actual = _sha256_file(model_path).lower()

        if (
            self.expected_model_sha256 is not None
            and actual != self.expected_model_sha256
        ):
            raise RuntimeError(
                "configured llama.cpp model SHA-256 does not match "
                "the expected model SHA-256"
            )

        self._verified_model_sha256 = actual
        return actual

    def _verify_executable(self) -> str:
        """
        Hash the exact llama.cpp executable and optionally compare it with
        the preregistered expected SHA-256.

        The verified value is cached for subsequent attempts in the same run.
        """
        if self._verified_executable_sha256 is not None:
            return self._verified_executable_sha256

        executable_path = Path(self.executable)

        if not executable_path.is_file():
            raise RuntimeError(
                "configured llama.cpp executable does not exist"
            )

        actual = _sha256_file(executable_path).lower()

        if (
            self.expected_executable_sha256 is not None
            and actual != self.expected_executable_sha256
        ):
            raise RuntimeError(
                "configured llama.cpp executable SHA-256 does not match "
                "the expected executable SHA-256"
            )

        self._verified_executable_sha256 = actual
        return actual

    def _inference_metadata(self) -> dict:
        """Return the bounded inference configuration used by llama.cpp."""
        return {
            "context_size": self.context_size,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "min_p": self.min_p,
            "gpu_layers": self.gpu_layers,
            "single_turn": True,
            "simple_io": True,
            "display_prompt": False,
        }

    def generation_evidence(self) -> dict | None:
        """
        Return evidence describing the most recent generation attempt.

        Machine-specific executable and model paths are deliberately excluded.
        """
        if self._last_generation_evidence is None:
            return None

        return dict(self._last_generation_evidence)

    def __call__(
        self,
        goal: str,
        observations: list[dict],
        attempt: int,
    ) -> str:
        self._last_generation_evidence = None

        executable_sha256 = self._verify_executable()
        model_sha256 = self._verify_model()

        prompt = self.build_prompt(
            goal,
            observations,
            attempt,
        )
        prompt_sha256 = sha256_text(prompt)

        command = [
            self.executable,
            "-m",
            self.model_path,
            "-ngl",
            str(self.gpu_layers),
            "-c",
            str(self.context_size),
            "-n",
            str(self.max_tokens),
            "--seed",
            str(self.seed),
            "--temp",
            str(self.temperature),
            "--top-k",
            str(self.top_k),
            "--top-p",
            str(self.top_p),
            "--min-p",
            str(self.min_p),
            "--single-turn",
            "--simple-io",
            "--no-display-prompt",
            "-p",
            prompt,
        ]

        started_at = _utc_now()

        try:
            completed = subprocess.run(
                command,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            finished_at = _utc_now()

            self._last_generation_evidence = {
                "prompt_sha256": prompt_sha256,
                "model_sha256": model_sha256,
                "runtime": "llama.cpp",
                "runtime_executable_sha256": executable_sha256,
                "runtime_build": self.runtime_build,
                "runtime_commit": self.runtime_commit,
                "started_at": started_at,
                "finished_at": finished_at,
                "status": "TIMEOUT",
                "inference": self._inference_metadata(),
            }

            raise RuntimeError(
                "llama.cpp inference timed out"
            ) from exc

        finished_at = _utc_now()

        self._last_generation_evidence = {
            "prompt_sha256": prompt_sha256,
            "model_sha256": model_sha256,
            "runtime": "llama.cpp",
            "runtime_executable_sha256": executable_sha256,
            "runtime_build": self.runtime_build,
            "runtime_commit": self.runtime_commit,
            "started_at": started_at,
            "finished_at": finished_at,
            "status": (
                "COMPLETED"
                if completed.returncode == 0
                else "RUNTIME_ERROR"
            ),
            "returncode": completed.returncode,
            "inference": self._inference_metadata(),
        }

        if completed.returncode != 0:
            stderr = completed.stderr.strip()

            raise RuntimeError(
                f"llama.cpp inference failed with exit code "
                f"{completed.returncode}: {stderr}"
            )

        output = completed.stdout

        begin_marker = "ARCSTONE_PROPOSAL_BEGIN"
        end_marker = "ARCSTONE_PROPOSAL_END"

        begin = output.rfind(begin_marker)

        if begin == -1:
            raise RuntimeError(
                "llama.cpp output missing proposal begin marker"
            )

        begin += len(begin_marker)

        end = output.find(
            end_marker,
            begin,
        )

        if end == -1:
            raise RuntimeError(
                "llama.cpp output missing proposal end marker"
            )

        proposal = output[begin:end].strip()

        if not proposal:
            raise RuntimeError(
                "llama.cpp returned empty proposal"
            )

        return proposal