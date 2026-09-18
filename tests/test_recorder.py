import json

import pytest

from arcstone_adaptive_producer_lab.recorder import Recorder


def test_recorder_creates_fresh_trace(tmp_path):
    evidence_dir = tmp_path / "run"

    recorder = Recorder(evidence_dir)

    assert recorder.trace.exists()
    assert recorder.trace.read_text(encoding="utf-8") == ""


def test_same_recorder_can_append_multiple_attempts(tmp_path):
    evidence_dir = tmp_path / "run"

    recorder = Recorder(evidence_dir)
    recorder.append({"attempt": 1, "decision": "DENY"})
    recorder.append({"attempt": 2, "decision": "DENY"})

    lines = recorder.trace.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0]) == {
        "attempt": 1,
        "decision": "DENY",
    }
    assert json.loads(lines[1]) == {
        "attempt": 2,
        "decision": "DENY",
    }


def test_new_recorder_refuses_existing_trace(tmp_path):
    evidence_dir = tmp_path / "run"

    first = Recorder(evidence_dir)
    first.append({"attempt": 1})

    with pytest.raises(FileExistsError):
        Recorder(evidence_dir)

    lines = first.trace.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1
    assert json.loads(lines[0]) == {"attempt": 1}


def test_existing_trace_is_never_overwritten(tmp_path):
    evidence_dir = tmp_path / "run"
    evidence_dir.mkdir()

    trace = evidence_dir / "attempts.jsonl"
    original = '{"preserve":"this"}\n'
    trace.write_text(original, encoding="utf-8")

    with pytest.raises(FileExistsError):
        Recorder(evidence_dir)

    assert trace.read_text(encoding="utf-8") == original
    