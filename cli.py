import sys
from uuid import uuid4

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from langgraph.types import Command

from config.settings import settings
from graph.builder import build_graph
from hitl.cli_handler import handle_analysis, handle_plan, handle_notebook

app = Console()
console = Console()
cli = typer.Typer(help="Convert a research paper into a runnable Jupyter notebook.")

HITL_HANDLERS = {
    "analysis": handle_analysis,
    "plan": handle_plan,
    "notebook": handle_notebook,
}

def _run_graph(source: str):
    initial_state = {
        "source": source,
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
        "retry_count":        0,
        "output_path":        "",
        "status":             "starting",
    }

    graph  = build_graph()
    config = {"configurable": {"thread_id": str(uuid4())}}
    stream = graph.stream(initial_state, config, stream_mode="updates")

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
                passed = sum(1 for r in out.get("validation_results", []) if r["passed"])
                total  = len(out.get("validation_results", []))
                retries = out.get("retry_count", 0)
                console.print(f"  {passed}/{total} cells passed  |  retries: {retries}")

            if node_name == "assemble":
                path = out.get("output_path", "")
                console.print(f"\n  [bold green]Saved:[/bold green] {path}\n")
                return path


@cli.command()
def run(
    source: str = typer.Argument(..., help="arXiv ID, arXiv URL, or local PDF path"),
    provider: str = typer.Option(None, "--provider", "-p", help="Override LLM provider"),
):
    """Convert a research paper into a runnable Jupyter notebook."""
    if provider:
        import os
        os.environ["LLM_PROVIDER"] = provider

    console.print(Panel.fit(f"paper2nb  |  [bold]{source}[/bold]  |  {settings.llm_provider} / {settings.active_model}"))
    _run_graph(source)


@cli.command()
def providers():
    """List all supported LLM providers and their configured models."""
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Status")

    configs = {
        "anthropic":  (settings.anthropic_model,  bool(settings.anthropic_api_key)),
        "openai":     (settings.openai_model,      bool(settings.openai_api_key)),
        "google":     (settings.google_model,      bool(settings.google_api_key)),
        "openrouter": (settings.openrouter_model,  bool(settings.openrouter_api_key)),
        "ollama":     (f"{settings.ollama_model} ({settings.ollama_base_url})", True),
    }

    for name, (model, ready) in configs.items():
        active = name == settings.llm_provider
        status = "[green]active[/green]" if active else ("[dim]ready[/dim]" if ready else "[dim]no key[/dim]")
        label  = f"[bold]{name}[/bold]" if active else name
        table.add_row(label, model, status)

    console.print(table)


@cli.command()
def config():
    """Show current configuration."""
    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("key",   style="dim")
    table.add_column("value", style="bold green")

    table.add_row("provider",    settings.llm_provider)
    table.add_row("model",       settings.active_model)
    table.add_row("output_dir",  settings.output_dir)
    table.add_row("max_retries", str(settings.max_validation_retries))
    table.add_row("langsmith",   str(settings.langchain_tracing_v2))

    console.print(table)


if __name__ == "__main__":
    cli()