from __future__ import annotations
from abc import ABC, abstractmethod

class Producer(ABC):
    name="producer"
    @abstractmethod
    def propose(self, goal: str, observations: list[dict], attempt: int) -> str: ...
    def metadata(self) -> dict: return {"type":self.name}
