#!/usr/bin/env python3
"""Edge-case tests for LMStudioProvider using respx.

Run with pytest from repository root:

PYTHONPATH=. pytest -q
"""
from __future__ import annotations

import pytest
respx = pytest.importorskip("respx")

from deepr.models.llm_provider import LMStudioProvider


@respx.mock
def test_generate_handles_non_json_text_response():
    route = respx.post("http://localhost:1234/v1/chat/completions").respond(
        content=b"service busy, try later", headers={"Content-Type": "text/plain"}
    )
    p = LMStudioProvider()
    out = p.generate("Please answer: 2+2=")
    assert "service busy" in out
    assert route.called


@respx.mock
def test_generate_fallback_to_completion_endpoint():
    # Simulate chat failing but completion endpoint succeeds
    r1 = respx.post("http://localhost:1234/v1/chat/completions").respond(status_code=500)
    r2 = respx.post("http://localhost:1234/v1/completions").respond(json={"choices": [{"text": "4"}]})
    p = LMStudioProvider()
    out = p.generate("Please answer: 2+2=")
    assert out.strip() == "4"
    assert r1.called
    assert r2.called


@respx.mock
def test_streaming_fallbacks_to_generate_on_failure():
    # streaming endpoint returns 500; stream() should call generate() as fallback
    r_stream = respx.post("http://localhost:1234/v1/chat/completions").respond(status_code=500)
    # stream fails on chat; fallback generate() will try /v1/completions which we mock to succeed
    r_gen = respx.post("http://localhost:1234/v1/completions").respond(json={"choices": [{"text": "4"}]})
    p = LMStudioProvider()
    chunks = list(p.stream("Please answer: 2+2="))
    assert "4" in "".join(chunks)
    assert r_stream.called
    assert r_gen.called
