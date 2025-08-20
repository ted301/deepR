from deepr.prompts import open_deep_research_prompts as p

def test_prompts_present():
    assert hasattr(p, 'PLANNER_SYSTEM')
    assert 'phased research plan' in p.PLANNER_SYSTEM.lower()
