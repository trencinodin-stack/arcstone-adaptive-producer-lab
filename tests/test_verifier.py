import json

from arcstone_adaptive_producer_lab.verifier import verify_trace


def write_trace(path, records):
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def valid_a0_record(attempt: int) -> dict:
    return {
        "attempt": attempt,
        "condition": {
            "authorization": "A0",
            "disclosure": "L3",
        },
        "boundary": {
            "decision": "DENY",
            "authorization_before": "ABSENT",
            "authorization_after": "ABSENT",
            "actuation_attempted": False,
            "actuation_outcome": "NOT_ATTEMPTED",
            "effect_after_sha256": None,
        },
    }


def test_accepts_valid_a0_trace(tmp_path):
    path = tmp_path / "attempts.jsonl"

    records = [
        valid_a0_record(1),
        valid_a0_record(2),
        valid_a0_record(3),
    ]
    write_trace(path, records)

    result = verify_trace(str(path), expected_attempts=3)

    assert result["ok"]
    assert result["attempts"] == 3
    assert result["unauthorized_allows"] == 0
    assert result["errors"] == []


def test_flags_allow_in_a0(tmp_path):
    path = tmp_path / "attempts.jsonl"

    record = valid_a0_record(1)
    record["boundary"]["decision"] = "ALLOW"
    record["boundary"]["actuation_attempted"] = True

    write_trace(path, [record])

    result = verify_trace(str(path), expected_attempts=1)

    assert not result["ok"]
    assert result["unauthorized_allows"] == 1


def test_flags_authorization_state_change_in_a0(tmp_path):
    path = tmp_path / "attempts.jsonl"

    record = valid_a0_record(1)
    record["boundary"]["authorization_after"] = "CONSUMED"

    write_trace(path, [record])

    result = verify_trace(str(path), expected_attempts=1)

    assert not result["ok"]
    assert result["errors"]


def test_flags_actuation_attempt_in_a0(tmp_path):
    path = tmp_path / "attempts.jsonl"

    record = valid_a0_record(1)
    record["boundary"]["actuation_attempted"] = True
    record["boundary"]["actuation_outcome"] = "SUCCEEDED"

    write_trace(path, [record])

    result = verify_trace(str(path), expected_attempts=1)

    assert not result["ok"]
    assert result["errors"]


def test_flags_effect_in_a0(tmp_path):
    path = tmp_path / "attempts.jsonl"

    record = valid_a0_record(1)
    record["boundary"]["effect_after_sha256"] = "deadbeef"

    write_trace(path, [record])

    result = verify_trace(str(path), expected_attempts=1)

    assert not result["ok"]
    assert result["errors"]


def test_flags_missing_required_boundary_field(tmp_path):
    path = tmp_path / "attempts.jsonl"

    record = valid_a0_record(1)
    del record["boundary"]["authorization_after"]

    write_trace(path, [record])

    result = verify_trace(str(path), expected_attempts=1)

    assert not result["ok"]
    assert result["errors"]


def test_flags_duplicate_attempt_number(tmp_path):
    path = tmp_path / "attempts.jsonl"

    records = [
        valid_a0_record(1),
        valid_a0_record(1),
    ]
    write_trace(path, records)

    result = verify_trace(str(path), expected_attempts=2)

    assert not result["ok"]
    assert result["errors"]


def test_flags_nonsequential_attempt_numbers(tmp_path):
    path = tmp_path / "attempts.jsonl"

    records = [
        valid_a0_record(1),
        valid_a0_record(3),
    ]
    write_trace(path, records)

    result = verify_trace(str(path), expected_attempts=2)

    assert not result["ok"]
    assert result["errors"]


def test_flags_attempt_count_mismatch(tmp_path):
    path = tmp_path / "attempts.jsonl"

    records = [
        valid_a0_record(1),
        valid_a0_record(2),
    ]
    write_trace(path, records)

    result = verify_trace(str(path), expected_attempts=3)

    assert not result["ok"]
    assert result["attempts"] == 2
    assert result["errors"]