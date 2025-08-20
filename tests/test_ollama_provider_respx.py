#!/usr/bin/env python3
"""Unit tests for OllamaProvider using respx to mock httpx calls.

Run with pytest from repository root:

PYTHONPATH=. pytest -q
"""
from __future__ import annotations

import pytest
respx = pytest.importorskip("respx")


from deepr.models.llm_provider import OllamaProvider


@respx.mock
def test_list_models_ollama():
    route = respx.get("http://localhost:11434/v1/models").respond(
        json={"data": [{"id": "modelA"}, {"id": "modelB"}]}
    )
    p = OllamaProvider()
    models = p.list_models()
    assert models == ["modelA", "modelB"]
    assert route.called


@respx.mock
def test_generate_single_shot_ollama():
    route = respx.post("http://localhost:11434/api/generate").respond(
        json={"text": "4"}
    )
    p = OllamaProvider()
    out = p.generate("Please answer: 2+2=")
    assert out == "4"
    assert route.called


@respx.mock
def test_generate_streaming_ollama():
    # Simulate newline-delimited JSON chunks commonly emitted by Ollama
    stream_content = b'{"response":"The answer is "}\n{"response":"4"}\n'
    route = respx.post("http://localhost:11434/api/generate").respond(
        content=stream_content, headers={"Content-Type": "application/json"}
    )
    p = OllamaProvider()
    out = p.generate("Please answer: 2+2=")
    assert "The answer is" in out
    assert "4" in out
    assert route.called
