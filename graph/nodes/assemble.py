from pathlib import Path
import nbformat
from graph.state import PaperState

def _colab_badge(arxiv_id: str) -> str:
    url = f"https://arxiv.org/abs/{arxiv_id}"
    return f'<a href="{url}" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>\n\n'

def assemble_node(state: PaperState) -> dict:
    nb    = nbformat.v4.new_notebook()
    cells = []

    for i, cell in enumerate(state.get("cells", [])):
        content = cell.get("content", "")

        if cell["type"] == "markdown":
            if i == 0:
                content = _colab_badge(state.get("source", "")) + content
            cells.append(nbformat.v4.new_markdown_cell(content))

        elif cell["type"] == "code":
            cells.append(nbformat.v4.new_code_cell(content))

    nb.cells = cells
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name":    "python",
            "version": "3.10.0",
        },
    }

    arxiv_id = state.get("source", "notebook").replace("/", "_")
    output_path = f"outputs/{arxiv_id}.ipynb"
    Path("outputs").mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    return {"output_path": output_path, "status": "done"}