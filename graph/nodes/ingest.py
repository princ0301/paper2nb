from pathlib import Path
from graph.state import PaperState
from utils.arxiv_fetch import download_pdf, parse_arxiv_id
from utils.pdf import extract_text

def ingest_node(state: PaperState) -> dict:
    source = state["source"]

    if Path(source).exists() and source.endswith(".pdf"):
        pdf_path = source
    else:
        arxiv_id = parse_arxiv_id(source)
        cached = f"outputs/{arxiv_id}.pdf"
        pdf_path = cached if Path(cached).exists() else download_pdf(source)

    result = extract_text(pdf_path)

    return {
        "pdf_path": pdf_path,
        "raw_text": result["full_text"],
        "num_pages": result["num_pages"],
        "status": "ingested",
    }