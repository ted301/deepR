from deepr.integrations.deepagents_smoke import run_smoke

def test_deepagents_smoke():
    assert run_smoke() == 'deepagents_smoke_ok'
