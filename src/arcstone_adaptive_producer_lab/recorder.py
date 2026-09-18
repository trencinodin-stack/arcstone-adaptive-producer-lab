from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canonical_hash(obj: Any) -> str:
    return sha256_text(
        json.dumps(obj, sort_keys=True, separators=(",", ":"))
    )


class Recorder:
    """
    Append-only recorder for one experimental run.

    A Recorder owns exactly one attempts.jsonl trace. If that trace already
    exists when the Recorder is created, initialization fails closed rather
    than silently appending a new run to existing evidence.
    """

    def __init__(self, directory: str | Path):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

        self.trace = self.dir / "attempts.jsonl"

        if self.trace.exists():
            raise FileExistsError(
                f"Evidence trace already exists: {self.trace}. "
                "Refusing to append a new run to existing evidence."
            )

        # Reserve the trace path immediately. Exclusive creation prevents
        # accidental reuse if two run initializations target the same path.
        with self.trace.open(
            "x",
            encoding="utf-8",
            newline="\n",
        ):
            pass

    def append(self, record: dict[str, Any]) -> None:
        """
        Append one canonical JSON record to this run's trace.

        Repeated append() calls on the same Recorder are valid because they
        represent successive attempts belonging to the same run.
        """
        line = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
        )

        with self.trace.open(
            "a",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(line + "\n")
            