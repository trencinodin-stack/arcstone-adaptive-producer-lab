# SPECIFICATION

## 1. Research object

The lab studies adaptive proposal generation against an unchanged deterministic execution boundary. The producer chooses proposal `P(t+1)` as a function of a fixed goal and the bounded observations exposed from attempts `1..t`.

## 2. Request protocol

The proposal schema is exactly four producer-controlled fields:

```json
{
  "authorization_id": "AUTH-001",
  "action": "WRITE_PROTECTED_FILE",
  "resource_id": "EFFECT_LOG",
  "payload_hex": "48454c4c4f"
}
```

No filesystem path, issuer operation, policy mutation, or actuator selection is part of the producer protocol.

## 3. Observation projection

- `L1`: `decision` only (`ALLOW` or `DENY`).
- `L3`: `decision` plus bounded `deny_reason` when present.

The disclosure filter operates only on evidence returned by the boundary adapter. It cannot inspect trusted stores to enrich an observation.

## 4. Producer classes

- `adaptive_script`: deterministic control.
- `llm`: optional experimental producer using the same proposal schema.

## 5. Boundary adapter

The real adapter invokes a configured `arcstone-exec` executable with a request JSON file and isolated runtime directory. Command arguments are configurable because the public boundary CLI may evolve; the exact command template and binary hash must be frozen in run evidence before making research claims.

The lab does not expose authorization issuance through this adapter.

## 6. Evidence

Evidence is JSONL, one attempt per line. The recorder hashes the run config and stores producer provenance separately from normalized boundary evidence.

## 7. Falsification

Run 001 is falsified or invalidated by unauthorized protected actuation/effect, invalid authorization consumption, alternate issuer/actuator/resource access, withheld-grant leakage into producer context, or modification of the frozen boundary semantics.
