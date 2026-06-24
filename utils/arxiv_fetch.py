import re
from pathlib import Path
import httpx

def parse_arxiv_id(source: str) -> str:
    source = source.strip()
    match = re.search(r"(\d{4}\.\d{4,5})", source)
    if match:
        return match.group(1)
    raise ValueError(f"Could not parse arXiv ID from: {source}")

def download_pdf(source: str, output_dir: str = "./outputs") -> str:
    arxiv_id = parse_arxiv_id(source)
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    pdf_path = str(Path(output_dir) / f"{arxiv_id}.pdf")

    headers = {"User-Agent": "paper-to-notebook/1.0 (research tool)"}
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        response = client.get(pdf_url, headers=headers)
        response.raise_for_status()
        Path(pdf_path).write_bytes(response.content)

    return pdf_path