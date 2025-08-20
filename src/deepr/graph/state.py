from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class SharedGraphState:
    run_id: str
    plan: dict[str, Any] | None = None
    tasks: list[dict[str, Any]] = field(default_factory=list)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    critiques: list[dict[str, Any]] = field(default_factory=list)
    report: dict[str, Any] | None = None

    def add_task(self, task: dict[str, Any]) -> None:
        self.tasks.append(task)

    def next_task(self) -> dict[str, Any] | None:
        return self.tasks.pop(0) if self.tasks else None

__all__ = ["SharedGraphState"]
