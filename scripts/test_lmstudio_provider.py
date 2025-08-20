#!/usr/bin/env python3
"""Smoke test for LMStudioProvider only.

Run this from the activated deepR-env with the repository root as PYTHONPATH:

PYTHONPATH=. python scripts/test_lmstudio_provider.py
"""
from __future__ import annotations
import traceback

from deepr.models.llm_provider import LMStudioProvider


def main():
    p = LMStudioProvider()
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
    main()
