import pytest

from arcstone_adaptive_producer_lab.producers.llm import (
    LLMBackendNotConfigured,
    LLMProducer,
)


def test_llm_producer_metadata():
    producer = LLMProducer(model="gpt-5.6-sol")

    assert producer.metadata() == {
        "type": "llm",
        "model": "gpt-5.6-sol",
    }


def test_llm_producer_passes_bounded_inputs_to_backend():
    received = {}

    def backend(goal, observations, attempt):
        received["goal"] = goal
        received["observations"] = observations
        received["attempt"] = attempt
        return '{"authorization_id":"A","action":"WRITE_PROTECTED_FILE","resource_id":"EFFECT_LOG","payload_hex":"4849"}'

    producer = LLMProducer(
        model="gpt-5.6-sol",
        backend=backend,
    )

    proposal = producer.propose(
        "test goal",
        [{"decision": "DENY"}],
        3,
    )

    assert proposal == (
        '{"authorization_id":"A","action":"WRITE_PROTECTED_FILE",'
        '"resource_id":"EFFECT_LOG","payload_hex":"4849"}'
    )
    assert received == {
        "goal": "test goal",
        "observations": [{"decision": "DENY"}],
        "attempt": 3,
    }


def test_llm_producer_fails_closed_without_backend():
    producer = LLMProducer(model="gpt-5.6-sol")

    with pytest.raises(LLMBackendNotConfigured):
        producer.propose("test goal", [], 1)


def test_llm_producer_rejects_non_string_backend_result():
    def backend(goal, observations, attempt):
        return {"authorization_id": "A"}

    producer = LLMProducer(
        model="gpt-5.6-sol",
        backend=backend,
    )

    with pytest.raises(TypeError):
        producer.propose("test goal", [], 1)

def test_llm_producer_includes_provenance_metadata():
    provenance = {
        "model_sha256": "abc123",
        "runtime": "llama.cpp",
        "inference": {
            "seed": -1,
            "temperature": 0.80,
        },
    }

    producer = LLMProducer(
        model="model.gguf",
        provenance=provenance,
    )

    assert producer.metadata() == {
        "type": "llm",
        "model": "model.gguf",
        "provenance": provenance,
    }
