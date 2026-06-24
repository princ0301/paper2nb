from typing import TypedDict

class PaperState(TypedDict):
    source: str
    pdf_path: str
    raw_text: str
    num_pages: int

    analysis: dict
    analysis_feedback: str

    notebook_plan: list
    plan_feedback: str
    scope: str          # "toy" | "full"

    cells: list         # list of {"type": "code"|"markdown", "content": str}

    validation_results: list
    retry_count: int

    output_path: str
    status: str
