"""
main.py — Phase 8: Assemble real .ipynb
"""

from uuid import uuid4
from rich.console import Console
from rich.panel import Panel
from langgraph.types import Command

from graph.builder import build_graph
from hitl.cli_handler import handle_analysis, handle_plan, handle_notebook

console = Console()

INITIAL_STATE = {
    "source": "1412.6980",
    "pdf_path": "",
    "raw_text": "",
    "num_pages": 0,
    "analysis": {},
    "analysis_feedback": "",
    "notebook_plan": [],
    "plan_feedback": "",
    "scope": "toy",
    "cells": [],
    "validation_results": [],
    "retry_count": 0,
    "output_path": "",
    "status": "starting",
}

HITL_HANDLERS = {
    "analysis": handle_analysis,
    "plan":     handle_plan,
    "notebook": handle_notebook,
}


def print_validation(results: list, retry_count: int):
    passed = sum(1 for r in results if r["passed"])
    console.print(f"\n  {passed}/{len(results)} cells passed  |  retries: {retry_count}\n")
    for r in results:
        icon = "[green]✓[/green]" if r["passed"] else "[red]✗[/red]"
        console.print(f"  {icon}  {r['title']}")
        if not r["passed"]:
            console.print(f"      [red]{r['error'].strip().splitlines()[-1]}[/red]")


def run(graph, config):
    stream = graph.stream(INITIAL_STATE, config, stream_mode="updates")

    while True:
        try:
            chunk = next(stream)
        except StopIteration:
            break

        if "__interrupt__" in chunk:
            interrupt_val = chunk["__interrupt__"][0].value
            checkpoint    = interrupt_val["checkpoint"]
            data          = interrupt_val["data"]
            resume_val    = HITL_HANDLERS[checkpoint](data)
            stream        = graph.stream(Command(resume=resume_val), config, stream_mode="updates")
            continue

        for node_name, out in chunk.items():
            console.print(f"[green]✓[/green] {node_name}")

            if node_name == "validate":
                print_validation(
                    out.get("validation_results", []),
                    out.get("retry_count", 0),
                )

            if node_name == "assemble":
                path = out.get("output_path", "")
                console.print(f"\n  [bold green]Notebook saved:[/bold green] {path}")


def main():
    console.print(Panel.fit("Paper -> Notebook  |  Phase 8 — Assemble"))

    graph  = build_graph()
    config = {"configurable": {"thread_id": str(uuid4())}}

    run(graph, config)
    console.print("\nPhase 8 complete — open outputs/1412.6980.ipynb in Jupyter or Colab")


if __name__ == "__main__":
    main()