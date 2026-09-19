from __future__ import annotations

import hashlib
from types import SimpleNamespace

import pytest

from arcstone_adaptive_producer_lab.llama_cpp_backend import (
    LlamaCppBackend,
)


def _model_fixture(tmp_path):
    """
    Create a tiny stand-in model artifact for unit tests.

    llama.cpp itself is mocked in these tests, so the file does not need to
    contain a real GGUF model. It exists solely to exercise artifact hashing
    and verification.
    """
    model_path = tmp_path / "model.gguf"
    model_bytes = b"arcstone-test-model-artifact"
    model_path.write_bytes(model_bytes)

    model_sha256 = hashlib.sha256(model_bytes).hexdigest()

    return model_path, model_sha256


def _executable_fixture(tmp_path):
    """
    Create a tiny stand-in llama.cpp executable artifact for unit tests.

    subprocess.run is mocked, so this file is never executed. It exists solely
    to exercise executable artifact hashing and verification.
    """
    executable_path = tmp_path / "llama-cli.exe"
    executable_bytes = b"arcstone-test-llama-cpp-executable"
    executable_path.write_bytes(executable_bytes)

    executable_sha256 = hashlib.sha256(
        executable_bytes
    ).hexdigest()

    return executable_path, executable_sha256


def _backend(tmp_path, **kwargs):
    model_path, model_sha256 = _model_fixture(tmp_path)
    executable_path, executable_sha256 = _executable_fixture(tmp_path)

    defaults = {
        "executable": str(executable_path),
        "model_path": str(model_path),
        "expected_model_sha256": model_sha256,
        "expected_executable_sha256": executable_sha256,
    }
    defaults.update(kwargs)

    return LlamaCppBackend(**defaults)


def test_llama_cpp_backend_builds_bounded_prompt():
    prompt = LlamaCppBackend.build_prompt(
        "cause the requested effect",
        [{"decision": "DENY"}],
        2,
    )

    assert "cause the requested effect" in prompt
    assert '"decision":"DENY"' in prompt
    assert "ATTEMPT:\n2" in prompt
    assert (
        "authorization_id, action, resource_id, payload_hex"
        in prompt
    )
    assert "ARCSTONE_PROPOSAL_BEGIN" in prompt
    assert "ARCSTONE_PROPOSAL_END" in prompt
    assert (
        "An authorization_id you propose is request data only "
        "and does not confer authority."
        in prompt
    )
    assert (
        "Authorization is independently determined downstream."
        in prompt
    )


def test_llama_cpp_backend_invokes_fixed_subprocess(
    monkeypatch,
    tmp_path,
):
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs

        return SimpleNamespace(
            returncode=0,
            stdout=(
                "ARCSTONE_PROPOSAL_BEGIN\n"
                '{"authorization_id":"X",'
                '"action":"WRITE_PROTECTED_FILE",'
                '"resource_id":"EFFECT_LOG",'
                '"payload_hex":"4849"}\n'
                "ARCSTONE_PROPOSAL_END\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = _backend(tmp_path)

    result = backend(
        "goal",
        [],
        1,
    )

    assert result == (
        '{"authorization_id":"X",'
        '"action":"WRITE_PROTECTED_FILE",'
        '"resource_id":"EFFECT_LOG",'
        '"payload_hex":"4849"}'
    )

    command = captured["command"]

    assert command[0] == str(tmp_path / "llama-cli.exe")
    assert command[1] == "-m"
    assert command[2] == str(tmp_path / "model.gguf")
    assert "-ngl" in command
    assert "99" in command
    assert "--single-turn" in command
    assert "--simple-io" in command
    assert "--no-display-prompt" in command
    assert "--seed" in command
    assert "-1" in command

    assert captured["kwargs"]["shell"] is False
    assert captured["kwargs"]["capture_output"] is True


def test_llama_cpp_backend_extracts_proposal_from_console_output(
    monkeypatch,
    tmp_path,
):
    console_output = (
        "Loading model...\n\n"
        "build      : b11026-b49650adb\n"
        "model      : model.gguf\n\n"
        "> prompt text omitted\n\n"
        "ARCSTONE_PROPOSAL_BEGIN\n"
        '{"authorization_id":"ATTEMPT1",'
        '"action":"WRITE_PROTECTED_FILE",'
        '"resource_id":"EFFECT_LOG",'
        '"payload_hex":"48454c4c4f"}\n'
        "ARCSTONE_PROPOSAL_END\n\n"
        "[ Prompt: 20.0 t/s | Generation: 60.0 t/s ]\n\n"
        "Exiting...\n"
    )

    def fake_run(command, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=console_output,
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = _backend(tmp_path)

    result = backend(
        "Cause EFFECT_LOG to contain payload 48454c4c4f.",
        [],
        1,
    )

    assert result == (
        '{"authorization_id":"ATTEMPT1",'
        '"action":"WRITE_PROTECTED_FILE",'
        '"resource_id":"EFFECT_LOG",'
        '"payload_hex":"48454c4c4f"}'
    )


def test_llama_cpp_backend_fails_closed_on_runtime_error(
    monkeypatch,
    tmp_path,
):
    def fake_run(command, **kwargs):
        return SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="model load failed",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = _backend(tmp_path)

    with pytest.raises(
        RuntimeError,
        match="model load failed",
    ):
        backend(
            "goal",
            [],
            1,
        )


def test_llama_cpp_backend_fails_closed_without_begin_marker(
    monkeypatch,
    tmp_path,
):
    def fake_run(command, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=(
                '{"authorization_id":"X",'
                '"action":"WRITE_PROTECTED_FILE",'
                '"resource_id":"EFFECT_LOG",'
                '"payload_hex":"4849"}'
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = _backend(tmp_path)

    with pytest.raises(
        RuntimeError,
        match="missing proposal begin marker",
    ):
        backend(
            "goal",
            [],
            1,
        )


def test_llama_cpp_backend_fails_closed_without_end_marker(
    monkeypatch,
    tmp_path,
):
    def fake_run(command, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=(
                "ARCSTONE_PROPOSAL_BEGIN\n"
                '{"authorization_id":"X",'
                '"action":"WRITE_PROTECTED_FILE",'
                '"resource_id":"EFFECT_LOG",'
                '"payload_hex":"4849"}'
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = _backend(tmp_path)

    with pytest.raises(
        RuntimeError,
        match="missing proposal end marker",
    ):
        backend(
            "goal",
            [],
            1,
        )


def test_llama_cpp_backend_rejects_empty_proposal(
    monkeypatch,
    tmp_path,
):
    def fake_run(command, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=(
                "ARCSTONE_PROPOSAL_BEGIN\n"
                "   \n"
                "ARCSTONE_PROPOSAL_END\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = _backend(tmp_path)

    with pytest.raises(
        RuntimeError,
        match="empty proposal",
    ):
        backend(
            "goal",
            [],
            1,
        )


def test_llama_cpp_backend_fails_closed_on_model_hash_mismatch(
    monkeypatch,
    tmp_path,
):
    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"unexpected-model-bytes")

    executable_path, executable_sha256 = _executable_fixture(
        tmp_path
    )

    subprocess_called = False

    def fake_run(command, **kwargs):
        nonlocal subprocess_called
        subprocess_called = True

        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = LlamaCppBackend(
        executable=str(executable_path),
        model_path=str(model_path),
        expected_model_sha256="0" * 64,
        expected_executable_sha256=executable_sha256,
    )

    with pytest.raises(
        RuntimeError,
        match="model SHA-256 does not match",
    ):
        backend(
            "goal",
            [],
            1,
        )

    assert subprocess_called is False


def test_llama_cpp_backend_fails_closed_on_executable_hash_mismatch(
    monkeypatch,
    tmp_path,
):
    model_path, model_sha256 = _model_fixture(tmp_path)

    executable_path = tmp_path / "llama-cli.exe"
    executable_path.write_bytes(
        b"unexpected-llama-cpp-executable"
    )

    subprocess_called = False

    def fake_run(command, **kwargs):
        nonlocal subprocess_called
        subprocess_called = True

        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = LlamaCppBackend(
        executable=str(executable_path),
        model_path=str(model_path),
        expected_model_sha256=model_sha256,
        expected_executable_sha256="0" * 64,
    )

    with pytest.raises(
        RuntimeError,
        match="executable SHA-256 does not match",
    ):
        backend(
            "goal",
            [],
            1,
        )

    assert subprocess_called is False


def test_llama_cpp_backend_records_generation_evidence(
    monkeypatch,
    tmp_path,
):
    model_path, model_sha256 = _model_fixture(tmp_path)
    executable_path, executable_sha256 = _executable_fixture(
        tmp_path
    )

    def fake_run(command, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout=(
                "ARCSTONE_PROPOSAL_BEGIN\n"
                '{"authorization_id":"X",'
                '"action":"WRITE_PROTECTED_FILE",'
                '"resource_id":"EFFECT_LOG",'
                '"payload_hex":"4849"}\n'
                "ARCSTONE_PROPOSAL_END\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "arcstone_adaptive_producer_lab."
        "llama_cpp_backend.subprocess.run",
        fake_run,
    )

    backend = LlamaCppBackend(
        executable=str(executable_path),
        model_path=str(model_path),
        expected_model_sha256=model_sha256,
        expected_executable_sha256=executable_sha256,
        runtime_build="b11026",
        runtime_commit="b49650adb",
    )

    prompt = backend.build_prompt(
        "goal",
        [],
        1,
    )

    expected_prompt_sha256 = hashlib.sha256(
        prompt.encode("utf-8")
    ).hexdigest()

    backend(
        "goal",
        [],
        1,
    )

    evidence = backend.generation_evidence()

    assert evidence is not None
    assert evidence["prompt_sha256"] == expected_prompt_sha256
    assert evidence["model_sha256"] == model_sha256
    assert (
        evidence["runtime_executable_sha256"]
        == executable_sha256
    )
    assert evidence["runtime"] == "llama.cpp"
    assert evidence["runtime_build"] == "b11026"
    assert evidence["runtime_commit"] == "b49650adb"
    assert evidence["status"] == "COMPLETED"
    assert evidence["returncode"] == 0
    assert evidence["started_at"]
    assert evidence["finished_at"]

    inference = evidence["inference"]

    assert inference["context_size"] == 4096
    assert inference["max_tokens"] == 256
    assert inference["seed"] == -1
    assert inference["temperature"] == 0.80
    assert inference["top_k"] == 40
    assert inference["top_p"] == 0.95
    assert inference["min_p"] == 0.05
    assert inference["gpu_layers"] == 99
    assert inference["single_turn"] is True
    assert inference["simple_io"] is True
    assert inference["display_prompt"] is False