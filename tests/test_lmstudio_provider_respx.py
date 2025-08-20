#!/usr/bin/env python3
"""Unit tests for LMStudioProvider using respx to mock httpx calls.

Run with pytest from repository root:

PYTHONPATH=. pytest -q
"""
from __future__ import annotations

import pytest
respx = pytest.importorskip("respx")


from deepr.models.llm_provider import LMStudioProvider


@respx.mock
def test_list_models_lmstudio():
    route = respx.get("http://localhost:1234/v1/models").respond(
        json={"data": [{"id": "glm-4.5"}, {"id": "gpt-4"}]}
    )
    p = LMStudioProvider()
    models = p.list_models()
    assert models == ["glm-4.5", "gpt-4"]
    assert route.called


@respx.mock
def test_generate_chat_style_lmstudio():
    route = respx.post("http://localhost:1234/v1/chat/completions").respond(
        json={
            "choices": [{"message": {"content": "4"}}]
        }
    )
    p = LMStudioProvider()
    out = p.generate("Please answer: 2+2=")
    assert out.strip() == "4"
    assert route.called


@respx.mock
def test_generate_completion_style_lmstudio():
    route = respx.post("http://localhost:1234/v1/completions").respond(
        json={"choices": [{"text": "4"}]}
    )
    p = LMStudioProvider()
    out = p.generate("Please answer: 2+2=")
    assert out.strip() == "4"
    assert route.called


@respx.mock
def test_generate_streaming_lmstudio_sse():
    # Simulate SSE-style streaming with 'data: ' prefixed JSON lines
    sse = b'data: {"choices": [{"delta":{"content":"The answer is "}}]}\ndata: {"choices": [{"delta":{"content":"4"}}]}\ndata: [DONE]\n'
    route = respx.post("http://localhost:1234/v1/chat/completions").respond(
        content=sse, headers={"Content-Type": "text/event-stream"}
    )

    p = LMStudioProvider()
    chunks = list(p.stream("Please answer: 2+2="))
    joined = "".join(chunks)
    assert "The answer is" in joined
    assert "4" in joined
    assert route.called
