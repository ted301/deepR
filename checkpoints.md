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
