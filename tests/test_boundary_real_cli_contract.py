import hashlib
import json
import sys

import pytest

from arcstone_adaptive_producer_lab.boundary import (
    SubprocessBoundary,
)
from arcstone_adaptive_producer_lab.types import ExecutionRequest


def test_subprocess_boundary_uses_real_cli_contract(tmp_path):
    fake = tmp_path / "fake_boundary.py"

    fake.write_text(
        "import json,sys\n"
        "a=sys.argv[1:]\n"
        "assert a[0]=='execute'\n"
        "assert '--root' in a and '--request' in a "
        "and '--run-id' in a and '--producer' in a\n"
        "print(json.dumps({"
        "'decision':'DENY',"
        "'deny_reason':'ABSENT_AUTHORIZATION',"
        "'authorization_state_before':'ABSENT',"
        "'authorization_state_after':'ABSENT',"
        "'actuation':'NOT_ATTEMPTED',"
        "'effect_present_after':False,"
        "'effect_sha256_after':None"
        "}))\n",
        encoding="utf-8",
    )

    executable_path = sys.executable
    executable_bytes = open(
        executable_path,
        "rb",
    ).read()
    executable_sha256 = hashlib.sha256(
        executable_bytes
    ).hexdigest()

    template = [
        sys.executable,
        str(fake),
        "execute",
        "--root",
        "{runtime_dir}",
        "--request",
        "{request_file}",
        "--run-id",
        "{run_id}",
        "--producer",
        "{producer_label}",
    ]

    boundary = SubprocessBoundary(
        executable=sys.executable,
        runtime_dir=str(tmp_path / "runtime"),
        command_template=template,
        expected_executable_sha256=executable_sha256,
    )

    request = ExecutionRequest(
        "NOPE",
        "WRITE_PROTECTED_FILE",
        "EFFECT_LOG",
        "4849",
    )

    result = boundary.execute(
        request,
        run_id="R-A001",
        producer_label="script",
    )

    assert result.decision == "DENY"
    assert result.authorization_before == "ABSENT"
    assert result.actuation_attempted is False
    assert result.actuation_outcome == "NOT_ATTEMPTED"
    assert (
        result.raw["executable_sha256"]
        == executable_sha256
    )


def test_subprocess_boundary_fails_closed_on_executable_hash_mismatch(
    tmp_path,
):
    runtime_dir = tmp_path / "runtime"

    with pytest.raises(
        RuntimeError,
        match="Execution Boundary executable SHA-256",
    ):
        SubprocessBoundary(
            executable=sys.executable,
            runtime_dir=str(runtime_dir),
            command_template=[
                "{executable}",
                "execute",
            ],
            expected_executable_sha256="0" * 64,
        )

    assert runtime_dir.exists() is False