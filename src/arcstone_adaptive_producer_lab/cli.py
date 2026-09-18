from __future__ import annotations

import argparse
import json

from .config import load_config, resolve_boundary
from .producers.adaptive_script import AdaptiveScriptProducer
from .producers.llm import LLMProducer
from .runner import run_experiment
from .verifier import verify_trace


def main() -> None:
    parser = argparse.ArgumentParser(prog="arcstone-adaptive-lab")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--config", required=True)
    run_parser.add_argument("--dry-run", action="store_true")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("trace")
    verify_parser.add_argument(
        "--expected-attempts",
        type=int,
        default=None,
        help="Require exactly this many attempts in the evidence trace.",
    )

    args = parser.parse_args()

    if args.cmd == "verify":
        verification = verify_trace(
            args.trace,
            expected_attempts=args.expected_attempts,
        )
        print(json.dumps(verification, indent=2))
        return

    config = load_config(args.config)
    producer_type = config["producer"]["type"]

    if producer_type == "adaptive_script":
        producer = AdaptiveScriptProducer(
            config["request_defaults"]
        )

    elif producer_type == "llm":
        model = config["producer"].get("model")
        if not model:
            raise ValueError(
                "LLM producer requires producer.model in the experiment config"
            )

        producer = LLMProducer(model=model)

    else:
        raise ValueError(
            f"Unsupported producer type: {producer_type!r}"
        )

    result = run_experiment(
        config,
        producer,
        resolve_boundary(config, args.dry_run),
    )

    print(json.dumps(result, indent=2))

    verification = verify_trace(
        result["trace"],
        expected_attempts=config.get("max_attempts"),
    )

    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
    