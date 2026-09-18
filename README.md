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

## Quick start (deterministic dry run)

Requires Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
pytest
arcstone-adaptive-lab run --config configs/run-001.json --dry-run
```

The dry run uses a deterministic mock boundary and never claims Execution Boundary evidence. It exists to validate the lab loop, parser, disclosure projection, evidence format, and verifier.

## Real boundary configuration

Build/pin `arcstone-exec` in the sibling `arcstone-mcp-sidecar` repository. Then set:

```powershell
$env:ARCSTONE_EXEC_PATH="C:\path\to\arcstone-exec.exe"
$env:ARCSTONE_RUNTIME_DIR="C:\path\to\isolated\runtime"
```

Or copy `configs/local.example.json` to `configs/local.json` (ignored by Git) and set machine-specific values there.

The adapter executes only the configured boundary command. It has no issuer API and no direct actuator/resource API.

## Live LLM producer

Run 001 does not require a live model to validate the control. The included `OpenAICompatibleProducer` is deliberately SDK-free and uses the standard library HTTP client against an OpenAI-compatible Responses endpoint. API keys remain environment variables and are never written to evidence.

Set `OPENAI_API_KEY` and choose producer `llm` in a local config only after deterministic and boundary integration tests pass.

## Evidence discipline

Every attempt records two planes:

1. **Non-authoritative provenance** — producer output, observation shown, parser result, model metadata.
2. **Authoritative boundary evidence** — submitted request, decision, deny reason, authorization transition, actuation, and protected-state hashes when supplied by the boundary adapter.

A producer's statement that it succeeded is never evidence of actuation.

## Stop rule

If adaptive producers merely generate looped variants of already-tested invalid fixtures and reveal no new phenomenon, freeze Run 001 as a null/little-added-knowledge result. Do not expand this repository into a generalized agent platform.
