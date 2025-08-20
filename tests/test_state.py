from deepr.graph.state import SharedGraphState

def test_state_basic():
    s = SharedGraphState(run_id='r1')
    s.add_task({'id':'t1'})
    assert s.next_task()['id'] == 't1'
    assert s.next_task() is None
