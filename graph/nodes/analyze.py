import json
from pathlib import Path
from langchain_core.messages import HumanMessage

from graph.state import PaperState
from providers.factory import get_llm
from utils.parse import extract_json

PROMPT = Path("prompts/analyze.txt").read_text()


def analyze_node(state: PaperState) -> dict:
    llm = get_llm()
    
    paper_text = state["raw_text"][:12000]

    message = PROMPT.format(paper_text=paper_text)
    response = llm.invoke([HumanMessage(content=message)])

    analysis = extract_json(response.content)
    return {"analysis": analysis, "status": "analyzed"}