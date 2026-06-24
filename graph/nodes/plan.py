import json
from pathlib import Path
from langchain_core.messages import HumanMessage

from graph.state import PaperState
from providers.factory import get_llm
from utils.parse import extract_json

PROMPT = Path("prompts/plan.txt").read_text()

def plan_node(state: PaperState) -> dict:
    llm = get_llm()

    message = PROMPT.format(
        analysis=json.dumps(state["analysis"], indent=2),
        scope=state.get("scope", "toy"),
    )
    response = llm.invoke([HumanMessage(content=message)])

    result = extract_json(response.content)
    return {"notebook_plan": result["cells"], "status": "planned"}