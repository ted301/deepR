#!/usr/bin/env python3
"""Edge-case tests for OllamaProvider using respx.

Run with pytest from repository root:

PYTHONPATH=. pytest -q
"""
from __future__ import annotations

import pytest
respx = pytest.importorskip("respx")

from deepr.models.llm_provider import OllamaProvider


@respx.mock
def test_generate_non_json_response_returns_text():
    route = respx.post("http://localhost:11434/api/generate").respond(
        content=b"plain text error or fallback", headers={"Content-Type": "text/plain"}
    )
    p = OllamaProvider()
    out = p.generate("Please answer: 2+2=")
    assert "plain text error or fallback" in out
    assert route.called


@respx.mock
def test_list_models_handles_non_standard_shape():
    # return unexpected JSON shape -> should return empty list
    route = respx.get("http://localhost:11434/v1/models").respond(json={"models": ["x"]})
    p = OllamaProvider()
    models = p.list_models()
    assert models == []
    assert route.called
