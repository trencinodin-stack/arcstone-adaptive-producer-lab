from __future__ import annotations

import json
import os
from pathlib import Path


def load_config(path: str) -> dict:
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def resolve_boundary(
    config: dict,
    dry_run: bool = False,
):
    from .boundary import MockBoundary, SubprocessBoundary

    boundary_config = config["boundary"]

    if dry_run or boundary_config.get("mode") == "mock":
        return MockBoundary()

    executable = (
        boundary_config.get("executable")
        or os.environ.get(
            boundary_config.get(
                "executable_env",
                "ARCSTONE_EXEC_PATH",
            ),
            "",
        )
    )

    runtime_dir = (
        boundary_config.get("runtime_dir")
        or os.environ.get(
            boundary_config.get(
                "runtime_dir_env",
                "ARCSTONE_RUNTIME_DIR",
            ),
            "",
        )
    )

    if not executable or not runtime_dir:
        raise RuntimeError(
            "real boundary requires executable "
            "and runtime directory"
        )

    return SubprocessBoundary(
        executable=executable,
        runtime_dir=runtime_dir,
        command_template=boundary_config[
            "command_template"
        ],
        timeout_seconds=int(
            boundary_config.get(
                "timeout_seconds",
                10,
            )
        ),
        expected_executable_sha256=(
            boundary_config.get(
                "executable_sha256"
            )
        ),
    )