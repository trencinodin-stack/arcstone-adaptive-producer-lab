from __future__ import annotations
import json, os
from pathlib import Path

def load_config(path:str)->dict: return json.loads(Path(path).read_text(encoding="utf-8"))
def resolve_boundary(config:dict, dry_run:bool=False):
    from .boundary import MockBoundary, SubprocessBoundary
    b=config["boundary"]
    if dry_run or b.get("mode")=="mock": return MockBoundary()
    exe=b.get("executable") or os.environ.get(b.get("executable_env","ARCSTONE_EXEC_PATH"),"")
    runtime=b.get("runtime_dir") or os.environ.get(b.get("runtime_dir_env","ARCSTONE_RUNTIME_DIR"),"")
    if not exe or not runtime: raise RuntimeError("real boundary requires executable and runtime directory")
    return SubprocessBoundary(exe,runtime,b["command_template"],int(b.get("timeout_seconds",10)))
