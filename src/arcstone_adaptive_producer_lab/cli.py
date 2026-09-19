from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config, resolve_boundary
from .llama_cpp_backend import LlamaCppBackend
from .producers.adaptive_script import AdaptiveScriptProducer
from .producers.llm import LLMProducer
from .runner import run_experiment
from .verifier import verify_trace


MODEL_SHA256 = (
    "7B064F5842BF9532C91456DEDA288A1B672397A54FA729AA665952863033557C"
)
LLAMA_CPP_EXECUTABLE_SHA256 = (
    "4C38646A30B11A70DA32DCBE896F0CF035D991225AD8A5FC6E02A5205C0D7A87"
)
LLAMA_CPP_BUILD = "b11026"
LLAMA_CPP_COMMIT = "b49650adb"

CONTEXT_SIZE = 4096
MAX_TOKENS = 256
SEED = -1
TEMPERATURE = 0.80
TOP_K = 40
TOP_P = 0.95
MIN_P = 0.05
GPU_LAYERS = 99


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="arcstone-adaptive-lab"
    )
    subparsers = parser.add_subparsers(
        dest="cmd",
        required=True,
    )

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument(
        "--config",
        required=True,
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
    )

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
        print(
            json.dumps(
                verification,
                indent=2,
            )
        )
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
                "LLM producer requires producer.model "
                "in the experiment config"
            )

        local_path = Path("configs/local.json")

        if not local_path.is_file():
            raise RuntimeError(
                "live LLM producer requires gitignored "
                "configs/local.json"
            )

        local = load_config(str(local_path))
        llm_local = local.get("llm", {})

        executable = llm_local.get("executable")
        model_path = llm_local.get("model_path")

        if not executable or not model_path:
            raise RuntimeError(
                "configs/local.json requires "
                "llm.executable and llm.model_path"
            )

        backend = LlamaCppBackend(
            executable=executable,
            model_path=model_path,
            expected_model_sha256=MODEL_SHA256,
            expected_executable_sha256=LLAMA_CPP_EXECUTABLE_SHA256,
            runtime_build=LLAMA_CPP_BUILD,
            runtime_commit=LLAMA_CPP_COMMIT,
            context_size=CONTEXT_SIZE,
            max_tokens=MAX_TOKENS,
            seed=SEED,
            temperature=TEMPERATURE,
            top_k=TOP_K,
            top_p=TOP_P,
            min_p=MIN_P,
            gpu_layers=GPU_LAYERS,
        )

        producer = LLMProducer(
            model=model,
            backend=backend,
            provenance={
                "model_sha256": MODEL_SHA256,
                "runtime": "llama.cpp",
                "runtime_executable_sha256": (
                    LLAMA_CPP_EXECUTABLE_SHA256
                ),
                "runtime_build": LLAMA_CPP_BUILD,
                "runtime_commit": LLAMA_CPP_COMMIT,
                "inference": {
                    "context_size": CONTEXT_SIZE,
                    "max_tokens": MAX_TOKENS,
                    "seed": SEED,
                    "temperature": TEMPERATURE,
                    "top_k": TOP_K,
                    "top_p": TOP_P,
                    "min_p": MIN_P,
                    "gpu_layers": GPU_LAYERS,
                    "single_turn": True,
                    "simple_io": True,
                    "display_prompt": False,
                },
            },
        )

    else:
        raise ValueError(
            f"Unsupported producer type: {producer_type!r}"
        )

    boundary = resolve_boundary(
        config,
        args.dry_run,
    )

    result = run_experiment(
        config,
        producer,
        boundary,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    verification = verify_trace(
        result["trace"],
        expected_attempts=config.get("max_attempts"),
    )

    print(
        json.dumps(
            verification,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()