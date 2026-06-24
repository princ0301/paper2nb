from __future__ import annotations

from pathlib import Path

import typer
from IPython.display import Image, display

from graph.builder import build_graph


app = typer.Typer(help="Render the Paper-to-Notebook LangGraph workflow.")


def workflow_png() -> bytes:
    """Return a PNG rendering of the compiled workflow."""
    graph = build_graph()
    return graph.get_graph().draw_mermaid_png()


def display_workflow() -> None:
    """Display the workflow inline in IPython/Jupyter."""
    display(Image(data=workflow_png()))


@app.command()
def render(
    output: Path = typer.Option(
        Path("outputs/workflow.png"),
        "--output",
        "-o",
        help="Destination PNG path.",
    ),
) -> None:
    """Save a PNG rendering of the workflow."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(workflow_png())
    typer.echo(f"Workflow image saved: {output}")


if __name__ == "__main__":
    app()
