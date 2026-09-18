from __future__ import annotations

from typing import Callable

from .base import Producer


class LLMBackendNotConfigured(RuntimeError):
    """Raised when no live LLM backend has been supplied."""


class LLMProducer(Producer):
    """
    Provider-neutral live LLM producer.

    The laboratory owns the producer contract, not the model transport.
    A backend receives the bounded experimental input and must return the
    producer proposal as text.

    The backend is never given authorization state, issuer access, actuator
    access, or direct protected-resource access.
    """

    name = "llm"

    def __init__(
        self,
        model: str,
        backend: Callable[[str, list[dict], int], str] | None = None,
    ):
        self.model = model
        self.backend = backend

    def metadata(self) -> dict:
        return {
            "type": self.name,
            "model": self.model,
        }

    def propose(
        self,
        goal: str,
        observations: list[dict],
        attempt: int,
    ) -> str:
        if self.backend is None:
            raise LLMBackendNotConfigured(
                "no live LLM backend has been configured"
            )

        proposal = self.backend(goal, observations, attempt)

        if not isinstance(proposal, str):
            raise TypeError("LLM backend must return proposal text")

        return proposal
