from __future__ import annotations
from dataclasses import asdict
from .parser import parse_proposal, ProposalError
from .disclosure import project
from .recorder import Recorder, sha256_text, canonical_hash

def run_experiment(config: dict, producer, boundary) -> dict:
    recorder=Recorder(config["evidence_dir"]); observations=[]; config_hash=canonical_hash(config); completed=0
    for attempt in range(1,int(config["max_attempts"])+1):
        raw=producer.propose(config["goal"],observations.copy(),attempt)
        parser={"accepted":False}; boundary_record={"decision":"NOT_SUBMITTED","actuation_attempted":False}
        shown={"decision":"MALFORMED"}
        try:
            req=parse_proposal(raw); parser={"accepted":True,"request":req.to_dict()}
            result=boundary.execute(req, run_id=f"{config["run_id"]}-A{attempt:03d}", producer_label=producer.metadata().get("type", "adaptive-producer")); boundary_record=asdict(result); shown=project(result,config["condition"]["disclosure"])
        except ProposalError as e:
            parser={"accepted":False,"error":str(e)}; shown={"decision":"MALFORMED"}
        rec={"run_id":config["run_id"],"attempt":attempt,"producer":producer.metadata(),"condition":config["condition"],"observation_shown":shown,"raw_output_sha256":sha256_text(raw),"raw_output":raw,"parser":parser,"boundary":boundary_record,"config_sha256":config_hash}
        recorder.append(rec); observations.append(shown); completed+=1
        if boundary_record.get("decision") == "ALLOW": break
    return {"run_id":config["run_id"],"attempts":completed,"trace":str(recorder.trace),"config_sha256":config_hash}
