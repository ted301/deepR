# DeepR Local Deep Research Platform - Requirements (Draft)

## 1. Goal / Vision
Provide a fully local (or selectively hybrid) "deep research" platform on macOS (Apple Silicon M4 Max) leveraging:
- Deep Agents (reasoning / tool-using multi-step agent loop)
- Deep Agents UI (optional local dashboard)
- Open Deep Research (prompt patterns & workflow inspiration)
- LangChain & LangGraph for structured multi-agent orchestration
- Local / on-device or self-hosted LLM & embedding models accelerated via Metal Performance Shaders (MPS)

The platform ("DeepR") should enable automated, multi-phase research on arbitrary user questions, producing:
- Structured research plan
- Source acquisition (web, papers, code, PDFs)
- Extraction & summarization
- Cross-source synthesis & critique
- Artifact generation (final report, structured JSON, citations, optional slides / mindmap)

## 2. Operating Constraints
- Must run under a dedicated conda environment: `deepR-env` (Python >=3.11)
- Default to local inference (Ollama @ `http://localhost:11434` or LM Studio @ `http://localhost:1234`)
- Preferred base models: lightweight (llama3 8B / mistral 7B / phi3) and optional heavy model (`gpt-oss:120b`) when resources allow
- Ability to toggle remote APIs (OpenAI, Anthropic, etc.) via config (disabled by default)
- Support Apple MPS acceleration for PyTorch-based models
- Offline-capable core (graceful degradation when no network; skips web retrieval)
- Modular: easy to swap LLMs, embedding models, vector stores, retrievers
- Secure: minimal external calls unless enabled; redact secrets in logs
- Resource aware: concurrency limits (max parallel fetches = 4), token & rate budgeting
- Personal Knowledge Base (PKB) integration: configurable set of local directories to ingest / index

## 3. High-Level Functional Requirements
1. User Input Interface
   - CLI command: `deepr research "question" --config path.yaml`
   - (Optional) Web UI (Deep Agents UI fork / adapter) to submit queries & monitor graph state (Phase 2)
   - Support multi-turn refinement of initial query
2. Research Orchestration
   - Planner agent creates hierarchical research plan (phases, tasks)
   - Executor agents perform tasks: search, crawl, read, extract, summarize, compare
   - Analyst / Synthesizer agent merges findings, performs gap analysis
   - Critic / QA agent flags weak evidence & hallucination risk
   - Reporter agent produces final deliverables
3. Tooling Layer
   - Web search (priority: free-access APIs / engines) Tavily free tier, DuckDuckGo HTML, fallback local index
   - Web page fetch & clean (readability, boilerplate removal)
   - PDF ingestion (PyPDF, unstructured, or pdfminer), chunking
   - GitHub / code fetch (optional)
   - Arxiv / Semantic Scholar API (when enabled)
   - Local file ingestion (markdown, txt, PDF) + PKB directories
4. Retrieval & Memory
   - Local vector store: Chroma (final decision) per project + shared PKB index
   - Short-term scratchpad (agent state) vs long-term corpus (cached sources)
   - Embeddings: local (e.g., `nomic-embed-text`, `all-MiniLM`, `gte-small`) or remote override
5. LLM / Model Layer
   - Default local model(s) via Ollama or LM Studio; model selection per agent role
   - Optional heavy model (`gpt-oss:120b`) for synthesis phases if enabled
   - Streaming token support for UI
   - Fallback / override to remote API providers
6. Configuration
   - Central YAML file (e.g., `config/deepr.yaml`) controlling: models, tools, timeouts, retriever params, max cost, PKB paths
7. Caching & Persistence
   - Cache raw fetched sources, normalized text, embeddings, intermediate summaries
   - Re-run detection: skip unchanged sources
8. Observability
   - Structured logs (JSON option), colored CLI progress, per-agent event timeline
   - Optional OpenTelemetry hooks (future)
9. Testing & QA
   - Unit tests for tool adapters & planners
   - Integration tests for multi-agent graph (small mock run)
   - Regression snapshot for final report diffs
10. Extensibility
   - Plugin interface for custom tools (Python entrypoint class pattern)
   - Easy to add new agent roles or swap strategies

## 4. Non-Functional Requirements
- Performance: Single typical research run (<10 sources) completes in <5 min local models; scalable to >50 sources with streaming feedback
- Reliability: Recover mid-run after interruption (persist graph state)
- Maintainability: Clear layering (config, models, tools, agents, graph, UI)
- Documentation: README + architecture + task lifecycle + test guide

## 5. Core Components (Initial)
- Config Loader & Settings model (Pydantic)
- Model Provider Abstraction (local / remote)
- Embedding Provider
- Tool Registry & BaseTool interface
- Retrieval Layer (VectorStore wrapper over Chroma)
- Document Ingestion Pipeline (detect → load → chunk → embed → persist)
- PKB Ingestion Module (background / on-demand indexing of configured dirs)
- Agent Role Classes (Planner, Researcher, Synthesizer, Critic, Reporter)
- LangGraph / Deep Agents Graph Assembly
- Orchestrator (CLI entry) building run context & executing plan
- Persistence Layer (workspace dir per research query slug)
- Output Renderer (Markdown + JSON + citation map)
- UI Adapter (optional phase 2)

## 6. Deliverables
- `requirements.md` (this doc) ➜ approval gate
- `architecture.md`
- `tasks.md` (sequenced backlog with test hooks)
- `checkpoints.md` (rolling progress log)
- Source tree under `/Users/ted/deepR` with `src/deepr/...`
- `tests/` with unit + integration suites (pytest)
- Example config & example run script
- Minimal demo run producing sample report

## 7. External Dependencies (Preliminary)
- Core: python 3.11, langchain, langgraph, pydantic, typer (CLI), rich (UI), tenacity (retry)
- LLM Local: ollama (invoke via REST), LM Studio client, litellm (unified interface optional)
- Embeddings: sentence-transformers OR local embedding via huggingface; chromadb
- Parsing: beautifulsoup4, lxml, trafilatura/readability-lxml, unstructured[pdf]
- PDF/Text: pypdf, unstructured, markdown-it-py
- Vector DB: chromadb
- HTTP: httpx, aiohttp (async), requests-cache (optional)
- Testing: pytest, pytest-asyncio, responses / vcrpy for HTTP mocking
- Dev: black, isort, ruff, mypy (strict-ish) optional phase 2
- Optional: duckduckgo-search (if suitable), tavily-python

(Exact pins & compatibility to be finalized after environment creation.)

## 8. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Local model quality insufficient | Poor synthesis | Allow remote override & model selection per stage |
| Tool rate limits / failures | Incomplete data | Retry + multi-provider fallback |
| Hallucinations | Incorrect report | Critic agent + citation enforcement + source coverage checks |
| Performance on large docs | Slow runs | Adaptive chunk sizing + concurrency + caching |
| State loss mid-run | Wasted time | Periodic checkpoint serialization |
| API cost (if remote) | Expense | Budget guard & dry-run mode |

## 9. Resolved Decisions (Former Open Questions)
| Topic | Decision |
|-------|----------|
| Default local inference endpoints | Ollama (11434) and/or LM Studio (1234) selectable |
| Base models | llama3 8B / mistral 7B / phi3; optional `gpt-oss:120b` for heavy synthesis |
| Deep Agents UI timing | Phase 2 feature (not blocking core CLI) |
| External search APIs | Prefer free access (Tavily free tier, DuckDuckGo). Paid / other APIs disabled by default |
| Offline embedding download | Yes; bootstrap script downloads & caches models |
| Vector store | Chroma (single choice for MVP) |
| Output formats | Markdown + JSON only (no PDF/HTML initial) |
| Max concurrency | 4 parallel fetch / ingestion tasks cap (configurable <=4) |
| Personal Knowledge Base | Yes; configurable directories ingested into shared index |

## 10. Approval Gates Workflow
requirements.md -> (approve) -> architecture.md -> (approve) -> tasks.md -> (approve) -> incremental implementation (with checkpoints & tests).

## 11. Next Step Pending
Awaiting your approval of updated requirements to proceed with `architecture.md` design (component diagrams, data flows, class/module boundaries, sequence examples, state persistence strategy, test plan mapping).

---
Please review and approve or request adjustments.
