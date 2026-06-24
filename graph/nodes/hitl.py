from langgraph.types import interrupt
from graph.state import PaperState

def review_analysis_node(state: PaperState) -> dict:
    feedback = interrupt({
        "checkpoint": "analysis",
        "data": state.get("analysis", {}),
    })
    return {"analysis_feedback": feedback or ""}


def review_plan_node(state: PaperState) -> dict:
    result = interrupt({
        "checkpoint": "plan",
        "data": state.get("notebook_plan", []),
    })
    return {
        "plan_feedback": result.get("feedback", ""),
        "scope": result.get("scope", "toy"),
    }


def review_notebook_node(state: PaperState) -> dict:
    interrupt({
        "checkpoint": "notebook",
        "data": state.get("cells", []),
    })
    return {}