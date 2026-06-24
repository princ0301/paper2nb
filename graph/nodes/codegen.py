import json
from pathlib import Path

from langchain_core.messages import HumanMessage

from graph.state import PaperState
from providers.factory import get_llm
from utils.parse import extract_json

PROMPT = Path("prompts/codegen.txt").read_text()


def _error_context(state: PaperState) -> str:
    errors = [r for r in state.get("validation_results", []) if not r.get("passed")]
    if not errors:
        return ""
    lines = ["\nPrevious attempt failed. Fix these errors before regenerating:\n"]
    for e in errors:
        lines.append(f"Cell '{e['title']}':\n{e['error']}\n")
    return "\n".join(lines)


def codegen_node(state: PaperState) -> dict:
    llm = get_llm()

    message = PROMPT.format(
        analysis=json.dumps(state["analysis"], indent=2),
        plan=json.dumps(state["notebook_plan"], indent=2),
        scope=state.get("scope", "toy"),
        error_context=_error_context(state),
    )

    response = llm.invoke([HumanMessage(content=message)])
    result   = extract_json(response.content)

    return {"cells": result["cells"], "status": "generated"}