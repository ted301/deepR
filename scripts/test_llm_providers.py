#!/usr/bin/env python3
"""Simple sequential test: Ollama + LMStudio.

Runs each provider's generate() once. Designed to be safe when testing large models
— only one provider is invoked each, and errors are caught.
"""
from __future__ import annotations
import traceback

from deepr.models.llm_provider import OllamaProvider, LMStudioProvider


def try_provider(p):
    name = type(p).__name__
    print(f"--- Testing {name} ---")
    try:
        out = p.generate("Please answer: 2+2=")
        snippet = out.replace("\n", "\\n")
        print(f"OK [{name}]: {snippet[:500]}")
    except Exception as e:
        print(f"ERROR [{name}]: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # Test Ollama first (fast, if available)
    ollama = OllamaProvider()
    try_provider(ollama)

    # Then attempt LMStudio (may not be running locally)
    lm = LMStudioProvider()
    try_provider(lm)
