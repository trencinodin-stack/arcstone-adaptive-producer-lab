# Changelog

## 0.1.0 - 2026-09-18

- Initial Adaptive Producer Lab implementation baseline.
- Added Run 001 protocol.
- Added deterministic adaptive control producer.
- Added optional LLM producer.
- Added bounded disclosure filtering.
- Added Execution Boundary adapter.
- Added JSONL evidence recording and verification.
- Added deterministic CI baseline.

## 0.1.1 - 2026-09-18

### Execution Boundary integration

- Corrected real Arcstone Execution Boundary CLI integration to the pinned v0.1 interface:
  `execute --root --request --run-id [--producer]`.
- Validated integration against Execution Boundary version `0.1.0`.
- Recorded tested Execution Boundary source commit:
  `2b4e65165f3e1eb8a00a771c893946661782283b`.
- Added per-attempt boundary run IDs.
- Added producer provenance labels.
- Corrected parsing of:
  - `authorization_state_before`
  - `authorization_state_after`
  - `actuation`
  - `effect_present_after`
  - `effect_sha256_after`
- Added real-boundary A0 development configuration.
- Added CLI-contract regression coverage.

### Evidence integrity

- Changed evidence recording to fail closed when an `attempts.jsonl` trace already exists.
- Prevented silent append/reuse of an existing run trace.
- Added recorder regression tests covering trace creation, multi-attempt append within one recorder, reuse rejection, and overwrite prevention.

### Verification integrity

- Strengthened A0 verification to require:
  - `decision = DENY`
  - `authorization_before = ABSENT`
  - `authorization_after = ABSENT`
  - `actuation_attempted = false`
  - `actuation_outcome = NOT_ATTEMPTED`
  - no protected-effect hash
- Added required-field validation for A0 boundary evidence.
- Added attempt-sequence validation.
- Added optional expected-attempt-count validation.
- Added detection of duplicate and nonsequential attempt numbers.
- Added standalone CLI support for:
  `--expected-attempts`.
- Wired normal experiment execution to verify against the configured `max_attempts`.
- Changed unknown producer types to fail closed rather than implicitly selecting the LLM producer.

### Validation

- Expanded automated test suite to 21 passing tests.
- Completed an eight-attempt A0/L3 deterministic adaptive development run against the real pinned Execution Boundary.
- Strengthened verifier result for the preserved development trace:
  - 8 expected attempts
  - 8 observed attempts
  - 0 unauthorized ALLOW decisions
  - 0 verification errors
- Confirmed the development run as integration evidence only; it is not a frozen Run 001 research result.
