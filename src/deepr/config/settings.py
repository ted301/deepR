from __future__ import annotations
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Literal

class ModelConfig(BaseModel):
    provider: Literal['ollama','lmstudio','remote'] = 'ollama'
    model: str = 'llama3'
    temperature: float = 0.2
    max_tokens: int | None = None

class EmbeddingConfig(BaseModel):
    provider: Literal['sentence_transformers','huggingface_local'] = 'sentence_transformers'
    model: str = 'all-MiniLM-L6-v2'
    dim: int | None = None

class SearchConfig(BaseModel):
    enable_tavily: bool = True
    enable_duckduckgo: bool = True
    max_results: int = 8

class PKBConfig(BaseModel):
    paths: list[Path] = Field(default_factory=list)
    auto_index: bool = False

class ConcurrencyConfig(BaseModel):
    max_fetch_parallel: int = 4
    embed_batch_size: int = 16

class BudgetConfig(BaseModel):
    max_tokens: int | None = None
    max_time_seconds: int | None = None

class DeepRSettings(BaseModel):
    model: ModelConfig = ModelConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    search: SearchConfig = SearchConfig()
    pkb: PKBConfig = PKBConfig()
    concurrency: ConcurrencyConfig = ConcurrencyConfig()
    budget: BudgetConfig = BudgetConfig()
    workspace_root: Path = Path('./runs')
    output_formats: list[str] = ['markdown','json']
    cache_dir: Path = Path('./cache')

__all__ = [
    'DeepRSettings','ModelConfig','EmbeddingConfig','SearchConfig','PKBConfig','ConcurrencyConfig','BudgetConfig'
]
