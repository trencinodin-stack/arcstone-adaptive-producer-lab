import json
from pathlib import Path
from arcstone_adaptive_producer_lab.boundary import SubprocessBoundary
from arcstone_adaptive_producer_lab.types import ExecutionRequest


def test_subprocess_boundary_uses_real_cli_contract(tmp_path):
    fake = tmp_path / "fake_boundary.py"
    fake.write_text(
        "import json,sys\n"
        "a=sys.argv[1:]\n"
        "assert a[0]=='execute'\n"
        "assert '--root' in a and '--request' in a and '--run-id' in a and '--producer' in a\n"
        "print(json.dumps({'decision':'DENY','deny_reason':'ABSENT_AUTHORIZATION','authorization_state_before':'ABSENT','authorization_state_after':'ABSENT','actuation':'NOT_ATTEMPTED','effect_present_after':False,'effect_sha256_after':None}))\n",
        encoding="utf-8",
    )
    import sys
    template=[sys.executable, str(fake), 'execute', '--root', '{runtime_dir}', '--request', '{request_file}', '--run-id', '{run_id}', '--producer', '{producer_label}']
    b=SubprocessBoundary(sys.executable, str(tmp_path/'runtime'), template)
    req=ExecutionRequest('NOPE','WRITE_PROTECTED_FILE','EFFECT_LOG','4849')
    out=b.execute(req, run_id='R-A001', producer_label='script')
    assert out.decision=='DENY'
    assert out.authorization_before=='ABSENT'
    assert out.actuation_attempted is False
    assert out.actuation_outcome=='NOT_ATTEMPTED'
