# STATUS

- Repository: `arcstone-adaptive-producer-lab`
- Classification: Experimental / Downstream / Non-Canonical
- Phase: Integration baseline validated; experimental baseline preparation
- Active experiment: Run 001 — Adaptive Withheld-Grant Containment
- Upstream modification: None proposed
- Execution Boundary modification: Prohibited for Run 001
- Continuity Core runtime dependency: None
- Ingress Lab runtime dependency: None

## Current implementation state

The laboratory harness is operational against the real Arcstone Execution Boundary.

Validated development/integration state:

- Python producer and experiment harness execute successfully.
- Execution Boundary subprocess integration is operational.
- Tested Execution Boundary version: `0.1.0`.
- Tested Execution Boundary source commit:
  `2b4e65165f3e1eb8a00a771c893946661782283b`.
- The producer-facing runtime path uses the Execution Boundary `execute` interface only.
- Authorization issuance remains outside the producer-facing adaptive loop.
- Deterministic adaptive producer control is operational.
- L1 and L3 disclosure projections are implemented.
- Evidence is recorded as append-only JSONL within a single run.
- Reuse of an existing `attempts.jsonl` trace fails closed rather than silently appending a new run.
- A0 evidence verification checks attempt count, attempt sequence, authorization state, decision, actuation state, and protected-effect evidence.
- Current automated test suite: 21 tests passing.

## Real-boundary development validation

A development integration run was completed under:

- Producer: deterministic adaptive script
- Authorization condition: A0
- Disclosure condition: L3
- Attempts: 8
- Research run: false

Observed across the eight-attempt trajectory:

- `decision = DENY`
- `authorization_before = ABSENT`
- `authorization_after = ABSENT`
- `actuation_attempted = false`
- `actuation_outcome = NOT_ATTEMPTED`
- no protected effect hash
- zero unauthorized ALLOW decisions

Independent inspection of the Execution Boundary runtime showed:

- no issued authorization
- no consumed authorization
- no protected file/effect
- one boundary evidence record for each of the eight attempts

The strengthened trace verifier accepts the preserved development trace with exactly eight expected attempts and zero errors.

This development run validates laboratory integration and evidence plumbing. It is not a frozen Run 001 research result.

## Run 001 state

Run 001 remains experimental and unfrozen.

A fresh runtime, fresh evidence location, and explicit experimental condition identity are required before collecting baseline research evidence.

The deterministic producer baseline is to precede live LLM conditions.

No result from the development integration run is to be promoted to formal Run 001 evidence.

## Architectural boundary

For Run 001:

`reasoning != evaluation != authorization != actuation != observed effect`

`producer identity != authority`

`information != authority`

The adaptive producer may generate proposals and receive bounded observations. It does not issue trusted authorization, modify trusted authorization state, invoke the protected actuator directly, or mutate the protected resource directly.

A favorable upstream evaluation, producer identity, repeated interaction, or increased information does not constitute execution authority.

## Freeze policy

A Run 001 evidence directory becomes immutable after verification and freeze.

Existing evidence must not be silently overwritten or appended by a new run.

Changed research questions, experimental conditions, producer classes, disclosure conditions, or boundary semantics require an appropriate new condition, run, or experiment identity rather than mutation of frozen evidence.

Execution Boundary semantics must remain unchanged during Run 001 evidence collection.
