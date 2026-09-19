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
        provenance: dict | None = None,
    ):
        self.model = model
        self.backend = backend
        self.provenance = dict(provenance or {})

    def metadata(self) -> dict:
        metadata = {
            "type": self.name,
            "model": self.model,
        }

        if self.provenance:
            metadata["provenance"] = self.provenance.copy()

        return metadata

    def generation_evidence(self) -> dict | None:
        """
        Return evidence from the most recent backend generation when the
        configured backend exposes such evidence.
        """
        if self.backend is None:
            return None

        evidence_method = getattr(
            self.backend,
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
                "LLM backend generation evidence must be a dictionary"
            )

        return dict(evidence)

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

        proposal = self.backend(
            goal,
            observations,
            attempt,
        )

        if not isinstance(proposal, str):
            raise TypeError(
                "LLM backend must return proposal text"
            )

        return proposal