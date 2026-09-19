# AGENTS.md

These rules apply to humans, scripts, LLMs, coding assistants, autonomous agents, and automated tools working in this repository.

This repository is an Experimental, Downstream, Non-Canonical research laboratory for adaptive proposal generation upstream of deterministic execution authority.

Run 001 is completed and frozen. Its canonical evidence and experimental semantics are historical research artifacts, not an active development target.

## Constitutional boundaries

1. Producer identity is provenance, never authority.
2. Reasoning is not authorization.
3. Information is not authorization.
4. Favorable deterministic evaluation is not authorization.
5. Producer-generated authorization-shaped data is untrusted request data unless independently established by the Execution Boundary.
6. Authorization, authorization transition, actuation attempt, actuation outcome, protected-state transition, and observed effect must remain separately represented.
7. The producer must never infer authoritative success from its own output, reasoning, or self-report.

## Authority isolation

1. Do not add issuer access to producer code.
2. Do not expose issued or withheld authorization secrets to a producer except where explicitly required by a separately defined experimental condition.
3. Do not read or write trusted authorization state from producer code.
4. Do not invoke or reimplement the protected actuator from producer code.
5. Do not give producer code direct write access to the protected resource.
6. Do not copy authorization, gate, claim, or actuator logic from the Execution Boundary into this repository.
7. The boundary adapter may execute only the explicitly configured published Execution Boundary interface.
8. Disclosure code may redact or project authoritative observations; it must not fabricate trusted state.
9. Deterministic evaluation results must not be converted into execution authority.
10. No producer-side component may create an alternate authority path around the Execution Boundary.

## Frozen Run 001

Run 001 is complete and frozen at repository commit `4227beb` (`Freeze Run 001 evidence set`).

Do not:

- modify canonical Run 001 evidence;
- regenerate canonical Run 001 evidence under the same run identity;
- append attempts to frozen Run 001 traces;
- change Run 001 authorization, disclosure, producer, or attempt conditions in place;
- reinterpret development evidence as canonical Run 001 evidence;
- silently alter the Execution Boundary baseline associated with Run 001;
- rewrite Run 001 configuration or evidence hashes;
- modify frozen evidence merely to improve presentation or support a later interpretation.

A changed scientific question, producer class, authority condition, disclosure condition, capability surface, or boundary semantics requires a new run or experiment identity.

Historical errors discovered in frozen evidence must be documented explicitly. Do not silently repair the historical record.

## Run 001 scope exclusions

Do not add the following capabilities to Run 001:

- browser autonomy;
- shell autonomy;
- autonomous coding;
- persistent cross-run memory;
- multi-agent orchestration;
- MCP orchestration;
- additional protected actuators;
- network services;
- generalized policy engines;
- WASM isolation;
- cryptographic capability redesign;
- modifications to Continuity Core;
- modifications to Path A Ingress Lab;
- modifications to the frozen Execution Boundary baseline.

These may become variables in separately preregistered future experiments if evidence creates a scientific reason to study them.

## Evidence discipline

1. Preserve raw producer output separately from authoritative boundary evidence.
2. Preserve exact parser results and submitted requests.
3. Preserve the observation actually disclosed to the producer.
4. Preserve authoritative authorization state before and after execution.
5. Preserve boundary decision and denial reason independently of producer interpretation.
6. Preserve actuation attempt, actuation outcome, and protected effect independently.
7. Preserve configuration, software, model/runtime, and artifact provenance required by the experiment.
8. Evidence verification must rely on authoritative fields, not producer narrative.
9. A null result is valid. Do not add capabilities merely to make an experiment interesting.
10. Falsification evidence must be preserved rather than patched away.

## Secrets and environment

Never commit API keys, access tokens, authorization secrets, credentials, or other authority-bearing secrets.

Do not introduce hosted-provider credentials or provider-specific authority dependencies merely to operate a producer.

Machine-specific configuration should remain outside committed reusable configuration unless the path or value is itself intentionally preserved as historical execution evidence.

## Code changes after Run 001

Ordinary maintenance must not change the meaning of frozen Run 001 evidence.

Changes that alter experimental semantics require a new explicitly identified experiment or run and corresponding updates to the applicable:

- experiment definition;
- specification;
- machine-readable test matrix;
- configuration;
- evidence schema/version where necessary;
- provenance and artifact hashes.

Do not retroactively update frozen Run 001 artifacts to conform to a later experiment.

## Upstream repository boundaries

`arcstone-continuity-core`, `arcstone-path-a-ingress-lab`, and `arcstone-mcp-sidecar` / the Arcstone Execution Boundary are independent research surfaces.

Do not modify sibling repositories as a side effect of work in this repository.

Do not treat the repositories as a mandatory runtime pipeline unless a separately defined experiment explicitly establishes such a composition.

Compatibility with an upstream architecture is not evidence that this repository implements every upstream mechanism.

## Agent behavior

Before making a change:

1. Determine whether the requested work affects frozen Run 001.
2. If it would mutate Run 001 semantics or canonical evidence, do not perform the mutation.
3. Determine whether the work constitutes a new scientific question.
4. If so, create or propose a new run/experiment identity rather than extending Run 001.
5. Keep producer capability separate from execution authority.
6. Prefer the smallest change capable of answering the stated research question.

When uncertain whether a change crosses an authority or frozen-evidence boundary, preserve the existing state and surface the ambiguity rather than silently modifying it.