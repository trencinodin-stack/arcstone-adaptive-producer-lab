from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class ExecutionRequest:
    authorization_id: str
    action: str
    resource_id: str
    payload_hex: str
    def to_dict(self) -> dict[str, str]: return asdict(self)

@dataclass
class BoundaryResult:
    decision: str
    deny_reason: str | None = None
    authorization_before: str | None = None
    authorization_after: str | None = None
    actuation_attempted: bool | None = None
    actuation_outcome: str | None = None
    effect_before_sha256: str | None = None
    effect_after_sha256: str | None = None
    raw: dict[str, Any] | None = None
    exit_code: int | None = None
