# DeepR Implementation Task Plan (Draft)

Status: Pending approval

## Legend
- PRI: Priority (1 highest)
- Type: F=Feature, I=Infra, T=Test, D=Docs, R=Refactor
- Est: Relative size (S,M,L)

## Phase 0: Environment & Scaffolding
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| T0.1 | 1 | Create conda env `deepR-env` (py 3.11) & base deps file | I | - | `conda list` shows core libs; README quick start updated | test_env_placeholder.py |
| T0.2 | 1 | Project structure scaffolding (`src/deepr/...`) | I | T0.1 | Directories & __init__ present | tree snapshot |
| T0.3 | 1 | Logging setup (`logging/logger.py`) | I | T0.2 | Structured log emitted on dummy run | test_logging.py |
| T0.4 | 1 | Typer CLI skeleton (`deepr` command) | F | T0.2 | `deepr --help` works | test_cli_basic.py |
| T0.5 | 1 | Pydantic settings module + sample config file | F | T0.2 | Config loads & validates | test_config_load.py |
| T0.6 | 2 | Checkpoints file initialize | D | T0.2 | `checkpoints.md` exists with entry | - |
| T0.7 | 1 | Add deepagents as git submodule (shallow, pin SHA) | I | T0.2 | Submodule added & recorded in checkpoints | test_submodule_import.py |
| T0.8 | 1 | Import open_deep_research prompt assets (copy with attribution) | F | T0.2 | Prompts available in `src/deepr/prompts` | test_prompts_load.py |
| T0.9 | 1 | Smoke test deepagents basic agent run | T | T0.7 | Simple loop executes & returns text | test_deepagents_smoke.py |

## Phase 1: Core Abstractions
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| T1.1 | 1 | DeepAgents tool wrapper + extended registry (PDF, PKB custom tools) | F | T0.7 | Registry lists base + custom tools | test_tool_registry.py |
| T1.2 | 1 | ModelProvider abstraction + Ollama & LMStudio providers (non-stream) | F | T0.5 | Mock integration returns text | test_model_provider.py |
| T1.3 | 2 | Streaming support for ModelProvider | F | T1.2 | Iterator yields chunks | test_model_stream.py |
| T1.4 | 1 | EmbeddingProvider (sentence-transformers local) | F | T0.5 | Embeds deterministic length | test_embedding_provider.py |
| T1.5 | 2 | VectorStore wrapper (Chroma collections: run + pkb) | F | T1.4 | Add & similarity search pass | test_vector_store.py |
| T1.6 | 2 | SharedGraphState dataclass | F | T0.5 | Instantiation + update ops | test_state.py |
| T1.7 | 1 | DeepAgents graph integration scaffold (hook custom roles) | F | T1.6,T1.1 | Graph builds & runs placeholder plan | test_graph_scaffold.py |

## Phase 2: Tool Implementations (MVP)
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| T2.1 | 1 | Search Tool (DuckDuckGo HTML fallback) | F | T1.1 | Returns list<=N results | test_search_ddg.py (VCR) |
| T2.2 | 2 | Tavily integration (config gated) | F | T2.1 | Passes when API key absent (skips) | test_search_tavily.py |
| T2.3 | 1 | Web Fetch Tool (httpx + readability) | F | T1.1 | Fetch & cleaned text length > 0 | test_fetch_tool.py |
| T2.4 | 1 | PDF Loader Tool | F | T1.1 | Extract text > 0 from sample PDF | test_pdf_loader.py |
| T2.5 | 2 | File Loader (PKB ingest: md/txt/pdf) | F | T1.1 | Ingests sample dir & indexes | test_file_loader.py |
| T2.6 | 2 | Ingestion Pipeline (normalize→chunk→embed) | F | T1.4,T2.3 | Produces chunk objects + embeddings | test_ingestion_pipeline.py |
| T2.7 | 2 | Dedup hashing implementation | F | T2.6 | Duplicate doc not re-added | test_dedup.py |

## Phase 3: Agents & Graph Skeleton
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| T3.1 | 1 | Custom Role Adapter base (subclass deepagents Agent) | F | T1.7 | Adapter executes mock role | test_base_agent.py |
| T3.2 | 1 | Planner Agent + prompt template | F | T3.1,T1.2 | Generates JSON plan schema | test_planner_agent.py |
| T3.3 | 1 | (N/A - superseded by T1.7 DeepAgents graph scaffold) | R | T1.7 | Note recorded in checkpoints | - |
| T3.4 | 1 | Researcher Agent (consumes tasks, uses tools) | F | T3.2,T2.* | Ingests at least one doc | test_researcher_agent.py |
| T3.5 | 2 | Synthesizer Agent | F | T3.4 | Produces merged findings structure | test_synthesizer_agent.py |
| T3.6 | 2 | Critic Agent (gap detection) | F | T3.5 | Adds refinement tasks when missing citations | test_critic_agent.py |
| T3.7 | 1 | Reporter Agent (markdown + json) | F | T3.6 | Outputs files with required sections | test_reporter_agent.py |
| T3.8 | 2 | Transition predicates (loop logic) | F | T3.4 | State machine cycles correctly | test_transitions.py |

## Phase 4: Checkpointing & Resume
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| T4.1 | 1 | Checkpoint serializer (state to JSON) | F | T1.6 | File written with expected keys | test_checkpoint_write.py |
| T4.2 | 1 | Resume loader (rebuild state + vector refs) | F | T4.1,T1.5 | Resume continues tasks | test_checkpoint_resume.py |
| T4.3 | 2 | Rolling window & milestone tagging | F | T4.2 | Only last N kept; milestone persists | test_checkpoint_window.py |

## Phase 5: PKB Integration
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| P5.1 | 1 | PKB index creation (separate Chroma collection) | F | T1.5 | PKB searchable | test_pkb_index.py |
| P5.2 | 2 | Batch PKB ingestion command | F | P5.1,T2.5 | CLI command indexes sample dir | test_pkb_cli.py |
| P5.3 | 2 | Merge PKB results in retrieval queries | F | P5.2 | Mixed results from run + pkb | test_pkb_merge.py |

## Phase 6: Polishing & Hardening
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| H6.1 | 1 | Token usage estimation & budget guard | F | T3.* | Stops run if over budget | test_budget_guard.py |
| H6.2 | 2 | Streaming output support in providers | F | T1.3 | Streams tokens to callback | test_streaming_callback.py |
| H6.3 | 2 | Rich console progress bars | F | T0.3,T3.* | Visible bars update counts | test_console_progress.py |
| H6.4 | 2 | Retry & error classification | F | T2.* | Categorized exceptions retried | test_retry_logic.py |
| H6.5 | 3 | Configurable concurrency semaphore | F | T1.6 | Changing value limits tasks | test_concurrency_limit.py |

## Phase 7: Bootstrap & Demo
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| B7.1 | 1 | bootstrap_models.py (download embed + sample LLM check) | F | T1.2,T1.4 | Script completes idempotently | test_bootstrap_script.py |
| B7.2 | 1 | Demo run script (simple research query) | F | T3.7 | Produces report artifacts | test_demo_run.py |
| B7.3 | 2 | README usage + architecture links | D | B7.2 | Instructions reproducible | test_readme_links.py |

## Phase 8 (Deferred / Phase 2 UI)
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| U8.1 | 3 | Event streaming adapter (websocket) | F | T3.* | Emits events externally | test_event_stream.py |
| U8.2 | 3 | Basic UI integration placeholder | F | U8.1 | Connects & shows events | manual_ui_test.md |

## Cross-Cutting Tasks
| ID | PRI | Task | Type | Depends | Acceptance Criteria | Tests |
|----|-----|------|------|---------|---------------------|-------|
| C9.1 | 1 | Lint & format config (ruff, black) | I | T0.2 | CI lint passes | test_lint_placeholder.py |
| C9.2 | 2 | Type checking (mypy baseline) | I | C9.1 | mypy passes with strict core | mypy_report.txt |
| C9.3 | 2 | Coverage tooling (pytest-cov) | I | T2.* | Coverage report generated | coverage.xml |
| C9.4 | 2 | Regression snapshot harness | T | T3.7 | Snapshot test stable | test_regression_snapshot.py |
| C9.5 | 2 | Submodule SHA tracking & upgrade procedure | D | T0.7 | CHANGELOG/checkpoints record SHA | test_submodule_tracking.py |

## Milestones & Checkpoints
| Milestone | Includes | Exit Criteria | Checkpoint Tag |
|-----------|----------|--------------|----------------|
| M1 Scaffolding | Phase 0 | CLI + config + deepagents imported | m1_scaffolding |
| M2 Core Abstractions | Phase 1 | Providers + graph scaffold | m2_core |
| M3 Tools MVP | Phase 2 | Search+Fetch+Ingest path works | m3_tools |
| M4 Graph & Agents | Phase 3 | Plan→Docs→Report baseline | m4_agents |
| M5 Resilience | Phase 4 | Resume after forced stop | m5_resilience |
| M6 PKB | Phase 5 | PKB search integrated | m6_pkb |
| M7 Hardening | Phase 6 | Budget + retries stable | m7_hardening |
| M8 Demo Release | Phase 7 | Demo script reproducible | m8_demo |
| M9 UI Prep | Phase 8 | Event stream ready | m9_ui |

## Test Strategy Notes
- External HTTP calls wrapped with VCR / responses; offline mode test variant.
- Prompt outputs mocked where structure-only verification sufficient.
- Snapshot tests tolerant to whitespace only.

## Open Items (Need Confirmation if Adjustments)
1. Any task re-prioritization?
2. Minimum coverage threshold final? (default 85%, target 90%+)
3. Keep mypy strict on all or only core (config, providers, tools)?

---
Provide approval or adjustments. Upon approval, implementation will begin from Phase 0 (with `checkpoints.md` updates).
