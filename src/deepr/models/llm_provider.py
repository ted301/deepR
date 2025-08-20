from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable

class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str: ...

    def stream(self, prompt: str) -> Iterable[str]:  # default non-stream
        yield self.generate(prompt)

class DummyProvider(ModelProvider):
    def generate(self, prompt: str) -> str:  # pragma: no cover
        return f"echo: {prompt[:20]}"

__all__ = ["ModelProvider","DummyProvider"]
