# DeepR Checkpoints

## 2025-08-20 Phase 0 Start
- Initialized git repo
- Added scaffolding: logging, config models, CLI skeleton, tests placeholders
- Created pyproject.toml, README, gitignore, checkpoints file

Pending: conda env creation (user local), add deepagents submodule, import prompt assets, smoke test.

## 2025-08-20 Submodule Added
- Added deepagents as submodule (shallow clone)
- SHA: e7762ac
- Next: import prompt assets, smoke test agent loop.

## 2025-08-20 Env Created
- Created conda env deepR-env (python 3.11) per environment.yml
- Installed project in editable mode
- Initial tests executed successfully
- Next: import prompt assets (open_deep_research), add smoke agent test.

## 2025-08-20 Prompts & Smoke
- Imported adapted open_deep_research prompts (attribution noted)
- Added deepagents smoke placeholder module & test
- Tests passing
- Phase 0 tasks complete -> Milestone M1 achieved (pending tag)

## 2025-08-20 Phase1 Start
- Added tool base + registry & test
- Added initial ModelProvider abstraction (dummy)
- Tests passing
- Next: implement real Ollama & LM Studio providers, embedding provider, vector store wrapper.

## 2025-08-20 State Added
- Implemented SharedGraphState dataclass with task queue helpers
- Added test_state.py passing
- Next: Implement Ollama & LM Studio providers then vector store wrapper.

## 2025-08-20 OllamaProvider Implemented
- Implemented `OllamaProvider` in `src/deepr/models/llm_provider.py`.
- Uses correct Ollama endpoints: `GET /v1/models` for listing and `POST /api/generate` for generation.
- Default model set to `qwen3-coder`.
- Added `list_models()` helper and basic provider logic.
- Created and iteratively refined `scripts/test_llm_providers.py` to exercise the provider; successfully ran tests against a local Ollama instance and observed chunked JSON generation for the prompt "2+2".
- Environment notes: activated conda env, ensured `httpx` installed, ran tests with explicit conda python and `PYTHONPATH` to resolve imports; used `curl` to confirm Ollama endpoints.
- Status: Implemented and smoke-tested locally.
- Next: add more robust tests and CI hooks; implement and test LMStudioProvider.

## 2025-08-20 LMStudioProvider (in progress)
- Implemented an initial `LMStudioProvider` class in `src/deepr/models/llm_provider.py` with a `list_models()` helper and a default model set to `glm-4.5-air-dwq`.
- Server endpoint and payload for LMStudio still need confirmation and testing with a local LMStudio instance.
- Pending: finalize request payload/endpoint, implement full generation flow, add unit/integration tests in `tests/` and `scripts/`, and validate in CI.

## 2025-08-20 Ollama & LMStudio Providers - Completed
- Implemented `LMStudioProvider` targeting LMStudio's OpenAI-compatible endpoints (`/v1/models`, `/v1/chat/completions`, `/v1/completions`).
- Updated `LMStudioProvider` to try OpenAI-style chat and completion payloads, and to parse streaming SSE-style chunks when provided.
- Improved `OllamaProvider.generate` to support newline-delimited JSON streaming commonly emitted by Ollama (aggregates `response`/`text` fragments into a single returned string).
- Added separate smoke-test scripts:
  - `scripts/test_ollama_provider.py` (Ollama-only)
  - `scripts/test_lmstudio_provider.py` (LMStudio-only)
- Confirmed both providers pass smoke tests locally in `deepR-env` (LMStudio and Ollama instances running on the host). Example endpoints used during testing:
  - Ollama:
    - List models: GET http://localhost:11434/v1/models
    - Generate: POST http://localhost:11434/api/generate  (server often streams newline-delimited JSON objects)
    - Observed streamed fragments: JSON objects with keys like `response`, `done`, `created_at`.
  - LMStudio:
    - List models: GET http://localhost:1234/v1/models
    - Chat generate: POST http://localhost:1234/v1/chat/completions (OpenAI-compatible)
    - Text generate: POST http://localhost:1234/v1/completions (OpenAI-compatible)
    - Embeddings: POST http://localhost:1234/v1/embeddings
- Lessons learned / implementation notes:
  - Local servers vary: support multiple endpoint paths and payload shapes (OpenAI-style chat/completions, simple `inputs`/`prompt`, Ollama `/api/generate`).
  - Streaming shapes differ: Ollama emits newline-separated JSON objects; LMStudio uses OpenAI SSE-style `data: ...` lines for streaming. Providers now handle both patterns.
  - Prefer using the active conda env `deepR-env`'s `python` (not system `python3`) when running scripts. Use `PYTHONPATH=. python scripts/...` after activating the env.
  - Keep default models conservative but allow overriding: Ollama default `qwen3-coder`, LMStudio default `glm-4.5-air-dwq` — these may need to be changed per machine.

- Status: Providers implemented, smoke-tested locally.
- Next: add unit & integration tests (mocked httpx and CI-friendly tests), wire provider selection into higher-level agent code and add CI matrix to exercise at least non-network logic.
