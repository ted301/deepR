import pytest
from deepr.tools import base as tb

class EchoInput(tb.ToolInput):
    text: str

class EchoTool:
    name = "echo"
    description = "Return provided text"
    InputModel = EchoInput
    async def run(self, inp: EchoInput) -> tb.ToolResult:  # type: ignore[override]
        return tb.ToolResult(data=inp.text)

def test_registry_register_and_list():
    tb.registry.register(EchoTool())
    assert "echo" in tb.registry.list()

@pytest.mark.asyncio
async def test_run_tool():
    tool = tb.registry.get("echo")
    res = await tool.run(EchoInput(text="hello"))
    assert res.data == "hello"

@pytest.fixture(autouse=True)
def register_echo():
    tb.registry._tools.clear()
    tb.registry.register(EchoTool())
    yield
    tb.registry._tools.clear()