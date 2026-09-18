from __future__ import annotations
import json
from .base import Producer

class AdaptiveScriptProducer(Producer):
    name="adaptive_script"
    def __init__(self, defaults: dict): self.defaults=defaults
    def propose(self, goal: str, observations: list[dict], attempt: int) -> str:
        # Deterministic control: adapt authorization ID based only on bounded observation.
        suffix=attempt
        if observations and observations[-1].get("deny_reason") == "MalformedRequest": suffix=attempt+100
        req={"authorization_id":f"ADAPTIVE-{suffix:03d}","action":self.defaults["action"],"resource_id":self.defaults["resource_id"],"payload_hex":self.defaults["payload_hex"]}
        return json.dumps(req,separators=(",",":"),sort_keys=True)
