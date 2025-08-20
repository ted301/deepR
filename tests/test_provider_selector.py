#!/usr/bin/env python3
from __future__ import annotations

from deepr.agents.provider_selector import get_provider
from deepr.config.settings import DeepRSettings


def test_default_provider_is_ollama():
    p = get_provider()
    assert p.__class__.__name__ in ("OllamaProvider", "LMStudioProvider", "DummyProvider")


def test_selector_respects_settings():
    s = DeepRSettings()
    s.model.provider = "lmstudio"
    p = get_provider(s)
    assert p.__class__.__name__ == "LMStudioProvider"

    s.model.provider = "dummy"
    p = get_provider(s)
    assert p.__class__.__name__ == "DummyProvider"
