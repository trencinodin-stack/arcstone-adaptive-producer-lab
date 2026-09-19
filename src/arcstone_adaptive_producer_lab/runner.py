from __future__ import annotations

from dataclasses import asdict

from .disclosure import project
from .parser import ProposalError, parse_proposal
from .recorder import Recorder, canonical_hash, sha256_text


def _generation_evidence(producer) -> dict | None:
    """
    Retrieve evidence from the producer's most recent generation when the
    producer exposes generation evidence.

    Producers without generation evidence, including deterministic controls,
    remain valid and return None here.
    """
    evidence_method = getattr(
        producer,
        "generation_evidence",
        None,
    )

    if not callable(evidence_method):
        return None

    evidence = evidence_method()

    if evidence is None:
        return None

    if not isinstance(evidence, dict):
        raise TypeError(
            "producer generation evidence must be a dictionary"
        )

    return dict(evidence)


def run_experiment(config: dict, producer, boundary) -> dict:
    recorder = Recorder(config["evidence_dir"])
    observations = []
    config_hash = canonical_hash(config)
    completed = 0

    for attempt in range(
        1,
        int(config["max_attempts"]) + 1,
    ):
        raw = producer.propose(
            config["goal"],
            observations.copy(),
            attempt,
        )

        generation = _generation_evidence(producer)

        parser = {
            "accepted": False,
        }

        boundary_record = {
            "decision": "NOT_SUBMITTED",
            "actuation_attempted": False,
        }

        shown = {
            "decision": "MALFORMED",
        }

        try:
            req = parse_proposal(raw)

            parser = {
                "accepted": True,
                "request": req.to_dict(),
            }

            result = boundary.execute(
                req,
                run_id=(
                    f"{config['run_id']}-"
                    f"A{attempt:03d}"
                ),
                producer_label=producer.metadata().get(
                    "type",
                    "adaptive-producer",
                ),
            )

            boundary_record = asdict(result)

            shown = project(
                result,
                config["condition"]["disclosure"],
            )

        except ProposalError as exc:
            parser = {
                "accepted": False,
                "error": str(exc),
            }

            shown = {
                "decision": "MALFORMED",
            }

        boundary_config = config.get(
            "boundary",
            {},
        )

        record = {
            "run_id": config["run_id"],
            "attempt": attempt,
            "producer": producer.metadata(),
            "condition": config["condition"],
            "boundary_provenance": {
                "version": boundary_config.get(
                    "version"
                ),
                "commit": boundary_config.get(
                    "commit"
                ),
                "executable_sha256": (
                    boundary_config.get(
                        "executable_sha256"
                    )
                ),
            },
            "observation_shown": shown,
            "raw_output_sha256": sha256_text(raw),
            "raw_output": raw,
            "parser": parser,
            "boundary": boundary_record,
            "config_sha256": config_hash,
        }

        if generation is not None:
            record["generation"] = generation

        recorder.append(record)

        observations.append(shown)
        completed += 1

        if boundary_record.get("decision") == "ALLOW":
            break

    return {
        "run_id": config["run_id"],
        "attempts": completed,
        "trace": str(recorder.trace),
        "config_sha256": config_hash,
    }