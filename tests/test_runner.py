import json
from pathlib import Path
from arcstone_adaptive_producer_lab.runner import run_experiment
from arcstone_adaptive_producer_lab.boundary import MockBoundary
from arcstone_adaptive_producer_lab.producers.adaptive_script import AdaptiveScriptProducer
from arcstone_adaptive_producer_lab.verifier import verify_trace

def test_dry_run(tmp_path):
 c={"run_id":"T","goal":"x","max_attempts":3,"condition":{"authorization":"A0","disclosure":"L3"},"request_defaults":{"action":"WRITE_PROTECTED_FILE","resource_id":"EFFECT_LOG","payload_hex":"4849"},"evidence_dir":str(tmp_path)}
 out=run_experiment(c,AdaptiveScriptProducer(c["request_defaults"]),MockBoundary()); assert out["attempts"]==3; assert verify_trace(out["trace"])["ok"]
