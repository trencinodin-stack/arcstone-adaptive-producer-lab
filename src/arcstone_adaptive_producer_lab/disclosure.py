from .types import BoundaryResult

def project(result: BoundaryResult, level: str) -> dict:
    if level == "L1": return {"decision": result.decision}
    if level == "L3":
        out={"decision":result.decision}
        if result.deny_reason is not None: out["deny_reason"]=result.deny_reason
        return out
    raise ValueError(f"unsupported disclosure level: {level}")
