from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import PaperState
from graph.nodes.ingest import ingest_node
from graph.nodes.analyze import analyze_node
from graph.nodes.plan import plan_node
from graph.nodes.codegen import codegen_node
from graph.nodes.validate import validate_node
from graph.nodes.assemble import assemble_node
from graph.nodes.hitl import review_analysis_node, review_plan_node, review_notebook_node
from config.settings import settings

def _route_after_validate(state: PaperState) -> str:
    has_errors = any(not r.get("passed") for r in state.get("validation_results", []))
    under_limit = state.get("retry_count", 0) < settings.max_validation_retries
    if has_errors and under_limit:
        return "codegen"
    return "review_notebook"


def build_graph():
    g = StateGraph(PaperState)

    g.add_node("ingest", ingest_node)
    g.add_node("analyze", analyze_node)
    g.add_node("review_analysis", review_analysis_node)
    g.add_node("plan", plan_node)
    g.add_node("review_plan", review_plan_node)
    g.add_node("codegen", codegen_node)
    g.add_node("validate", validate_node)
    g.add_node("review_notebook", review_notebook_node)
    g.add_node("assemble", assemble_node)

    g.add_edge(START, "ingest")
    g.add_edge("ingest", "analyze")
    g.add_edge("analyze", "review_analysis")
    g.add_edge("review_analysis", "plan")
    g.add_edge("plan", "review_plan")
    g.add_edge("review_plan", "codegen")
    g.add_edge("codegen", "validate")
    g.add_edge("review_notebook", "assemble")
    g.add_edge("assemble", END)

    g.add_conditional_edges(
        "validate",
        _route_after_validate,
        {"codegen": "codegen", "review_notebook": "review_notebook"},
    )

    return g.compile(checkpointer=MemorySaver())