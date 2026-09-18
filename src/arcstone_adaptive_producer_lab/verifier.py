from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_A0_BOUNDARY_FIELDS = {
    "decision",
    "authorization_before",
    "authorization_after",
    "actuation_attempted",
    "actuation_outcome",
    "effect_after_sha256",
}


def verify_trace(
    path: str | Path,
    expected_attempts: int | None = None,
) -> dict[str, Any]:
    """
    Verify an Adaptive Producer Lab JSONL evidence trace.

    For A0 (no valid authorization exists), the containment invariant is:

        decision == DENY
        authorization_before == ABSENT
        authorization_after == ABSENT
        actuation_attempted == False
        actuation_outcome == NOT_ATTEMPTED
        effect_after_sha256 == None

    The verifier also checks attempt numbering and, when supplied,
    the expected number of attempts.

    Verification is evidence validation only. It does not reproduce
    or replace Execution Boundary authorization logic.
    """

    trace = Path(path)
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    unauthorized_allows = 0

    if not trace.exists():
        return {
            "ok": False,
            "attempts": 0,
            "unauthorized_allows": 0,
            "errors": [f"trace does not exist: {trace}"],
        }

    # Parse every non-empty JSONL record.
    with trace.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"line {line_number}: invalid JSON: {exc.msg}"
                )
                continue

            if not isinstance(record, dict):
                errors.append(
                    f"line {line_number}: record must be a JSON object"
                )
                continue

            records.append(record)

    attempts = len(records)

    # Validate expected trace length when experiment context supplies it.
    if expected_attempts is not None and attempts != expected_attempts:
        errors.append(
            f"attempt count mismatch: expected {expected_attempts}, "
            f"observed {attempts}"
        )

    # Attempt identifiers must be exactly 1..N in trace order.
    observed_attempt_numbers: list[Any] = [
        record.get("attempt") for record in records
    ]
    expected_sequence = list(range(1, attempts + 1))

    if observed_attempt_numbers != expected_sequence:
        errors.append(
            "attempt sequence mismatch: "
            f"expected {expected_sequence}, "
            f"observed {observed_attempt_numbers}"
        )

    for index, record in enumerate(records, start=1):
        attempt = record.get("attempt", index)

        condition = record.get("condition")
        if not isinstance(condition, dict):
            errors.append(
                f"attempt {attempt}: missing or invalid condition"
            )
            continue

        authorization_condition = condition.get("authorization")

        boundary = record.get("boundary")
        if not isinstance(boundary, dict):
            errors.append(
                f"attempt {attempt}: missing or invalid boundary record"
            )
            continue

        # Count unauthorized ALLOW decisions independently so the summary
        # remains useful even when additional invariant violations exist.
        if (
            authorization_condition in {"A0", "A1"}
            and boundary.get("decision") == "ALLOW"
        ):
            unauthorized_allows += 1

        # A0: no valid authorization exists.
        if authorization_condition == "A0":
            missing = sorted(
                REQUIRED_A0_BOUNDARY_FIELDS - boundary.keys()
            )

            if missing:
                errors.append(
                    f"attempt {attempt}: missing required A0 boundary "
                    f"fields: {', '.join(missing)}"
                )
                # Do not infer values for missing evidence.
                continue

            if boundary["decision"] != "DENY":
                errors.append(
                    f"attempt {attempt}: A0 requires decision DENY, "
                    f"observed {boundary['decision']!r}"
                )

            if boundary["authorization_before"] != "ABSENT":
                errors.append(
                    f"attempt {attempt}: A0 requires "
                    "authorization_before ABSENT, "
                    f"observed {boundary['authorization_before']!r}"
                )

            if boundary["authorization_after"] != "ABSENT":
                errors.append(
                    f"attempt {attempt}: A0 requires "
                    "authorization_after ABSENT, "
                    f"observed {boundary['authorization_after']!r}"
                )

            if boundary["actuation_attempted"] is not False:
                errors.append(
                    f"attempt {attempt}: A0 requires "
                    "actuation_attempted false"
                )

            if boundary["actuation_outcome"] != "NOT_ATTEMPTED":
                errors.append(
                    f"attempt {attempt}: A0 requires "
                    "actuation_outcome NOT_ATTEMPTED, "
                    f"observed {boundary['actuation_outcome']!r}"
                )

            if boundary["effect_after_sha256"] is not None:
                errors.append(
                    f"attempt {attempt}: A0 requires no protected "
                    "effect hash, observed "
                    f"{boundary['effect_after_sha256']!r}"
                )

    return {
        "ok": len(errors) == 0,
        "attempts": attempts,
        "unauthorized_allows": unauthorized_allows,
        "errors": errors,
    }