from __future__ import annotations
import json, re
from .types import ExecutionRequest

_ALLOWED={"authorization_id","action","resource_id","payload_hex"}
_HEX=re.compile(r"^[0-9A-Fa-f]*$")

class ProposalError(ValueError): pass

def parse_proposal(raw: str) -> ExecutionRequest:
    try: obj=json.loads(raw)
    except json.JSONDecodeError as e: raise ProposalError(f"invalid_json:{e.msg}") from e
    if not isinstance(obj,dict): raise ProposalError("proposal_must_be_object")
    if set(obj)!=_ALLOWED: raise ProposalError("proposal_fields_must_match_protocol_exactly")
    for k in _ALLOWED:
        if not isinstance(obj[k],str): raise ProposalError(f"{k}_must_be_string")
    if not obj["authorization_id"]: raise ProposalError("authorization_id_empty")
    if len(obj["authorization_id"])>256 or len(obj["action"])>128 or len(obj["resource_id"])>128: raise ProposalError("field_too_long")
    if len(obj["payload_hex"])>8192 or not _HEX.fullmatch(obj["payload_hex"]): raise ProposalError("payload_hex_invalid")
    if len(obj["payload_hex"])%2: raise ProposalError("payload_hex_must_have_even_length")
    return ExecutionRequest(**obj)
