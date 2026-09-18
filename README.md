# Arcstone Adaptive Producer Lab

**Status:** Experimental / Downstream / Non-Canonical  
**Run 001:** Adaptive Withheld-Grant Containment

This repository studies **closed-loop adaptive proposal generation upstream of an unchanged deterministic execution boundary**. It is not an agent platform and does not grant authority to a producer.

The scientific variable is adaptation: a producer receives a bounded observation, revises its next proposal, and resubmits. A deterministic adaptive script is the control producer; a live LLM can be used as an experimental producer through the same four-field request protocol.

## Constitutional separation

`reasoning != evaluation != authorization != actuation != observed effect`

`producer identity != authority`

`information != authority`

The lab must not issue trusted authorization on behalf of a producer, expose trusted authorization state to a producer, invoke the protected actuator directly, or copy/reimplement the Execution Boundary's authorization logic.

## Existing public surfaces

The lab is a sibling downstream experiment. It does **not** make the following repositories a mandatory runtime pipeline:

- `arcstone-continuity-core` — deterministic evaluation/reference surface; not authorization.
- `arcstone-path-a-ingress-lab` — producer capture/replay experiment; not authorization or actuation.
- `arcstone-mcp-sidecar` — Arcstone Execution Boundary; the external enforcement surface used by this lab.

Run 001 should target a **pinned, unchanged** `arcstone-exec` binary from the Execution Boundary repository.

## Configuration model

The laboratory separates **experiment configuration** from **machine-specific runtime configuration**.

Experiment configurations under `configs/` define the research condition, producer class, authorization condition, disclosure level, attempt budget, request defaults, boundary interface, and evidence location.

Machine-specific boundary configuration is kept separately in `configs/local.json`, which is ignored by Git.

This separation prevents machine-specific executable paths and runtime directories from becoming part of the experimental condition.

## Quick start (deterministic dry run)

Requires Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
pytest
arcstone-adaptive-lab run --config configs/run-001.json --dry-run
