from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Protocol

class ToolInput(BaseModel):
    pass

class ToolResult(BaseModel):
    ok: bool = True
    data: Any | None = None
    error: str | None = None

class BaseTool(Protocol):
    name: str
    description: str
    InputModel: type[ToolInput]

    async def run(self, inp: ToolInput) -> ToolResult: ...

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        return self._tools[name]

    def list(self) -> list[str]:
        return sorted(self._tools.keys())

registry = ToolRegistry()

__all__ = ["ToolRegistry","registry","BaseTool","ToolInput","ToolResult"]
