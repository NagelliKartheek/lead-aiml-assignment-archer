from src.agentic_workflow import plan

def test_plan_includes_search_for_issue_queries():
    steps = plan("Find issues in transit report")
    tool_names = [s["tool"] for s in steps]
    assert "search_corpus" in tool_names
    assert "summarize" in tool_names
