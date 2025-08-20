from __future__ import annotations
from typing import Optional
from ..models.llm_provider import ModelProvider, OllamaProvider, LMStudioProvider, DummyProvider
from ..config.settings import DeepRSettings


def get_provider(settings: Optional[DeepRSettings] = None) -> ModelProvider:
    """Return a ModelProvider instance based on settings (scaffold).

    Defaults to Ollama if settings not provided.
    """
    if settings is None:
        settings = DeepRSettings()

    provider = settings.model.provider
    model = settings.model.model
    temp = settings.model.temperature
    max_t = settings.model.max_tokens

    if provider == "ollama":
        return OllamaProvider(model=model, temperature=temp, max_tokens=max_t)
    if provider == "lmstudio":
        return LMStudioProvider(model=model, temperature=temp, max_tokens=max_t)
    if provider == "dummy":
        return DummyProvider()
    # fallback
    return OllamaProvider(model=model, temperature=temp, max_tokens=max_t)
