# AGENTS.md

These rules apply to humans, scripts, LLMs, coding assistants, and automated tools working in this repository.

## Non-negotiable boundaries

1. Producer identity is provenance, never authority.
2. Favorable deterministic evaluation is not authorization.
3. Do not add issuer access to producer code.
4. Do not read/write trusted authorization directories from producer code.
5. Do not invoke or reimplement the protected actuator.
6. Do not copy authorization/gate logic from the Execution Boundary into this lab.
7. The boundary adapter may execute only the configured published boundary command.
8. Disclosure code may redact/project observations; it must not fabricate trusted state.
9. Never put API keys, tokens, authorization secrets, or machine-specific runtime paths in committed files.
10. Preserve decision, authorization transition, actuation attempt, actuation outcome, and observed effect as separate fields.
11. A null result is valid. Do not add features merely to make the experiment interesting.
12. Do not add browser, shell, autonomous coding, persistent memory, multi-agent orchestration, MCP orchestration, extra actuators, networking, WASM, or cryptographic redesign to Run 001.

## Code changes

Changes that affect experiment semantics require corresponding updates to `EXPERIMENT.md`, `SPECIFICATION.md`, `machine/test-matrix.json`, and the config hash/evidence version.
