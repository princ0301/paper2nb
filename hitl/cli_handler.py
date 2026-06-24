import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

def handle_analysis(data: dict) -> str:
    console.print(Panel.fit("[bold yellow]HITL Checkpoint 1 — Review Analysis[/bold yellow]"))

    console.print(f"\n[bold]Contribution[/bold]\n  {data.get('contribution', '')}")

    console.print("\n[bold]Algorithm Steps[/bold]")
    for i, step in enumerate(data.get("algorithm_steps", []), 1):
        console.print(f"  {i}. {step}")

    console.print(f"\n[bold]Complexity[/bold]  {data.get('complexity', '')}\n")

    if Confirm.ask("Approve analysis and continue?", default=True):
        return ""

    return Prompt.ask("Feedback (will be passed to planner)")

def handle_plan(data: list) -> dict:
    console.print(Panel.fit("[bold yellow]HITL Checkpoint 2 — Review Notebook Plan[/bold yellow]"))

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("#",       width=3,  style="dim")
    table.add_column("Type",    width=8)
    table.add_column("Title",   width=30)
    table.add_column("Purpose")

    for i, cell in enumerate(data, 1):
        color = "cyan" if cell["type"] == "code" else "yellow"
        table.add_row(
            str(i),
            f"[{color}]{cell['type']}[/{color}]",
            cell.get("title", ""),
            cell.get("purpose", ""),
        )

    console.print(table)

    scope    = Prompt.ask("\nScope", choices=["toy", "full"], default="toy")
    approved = Confirm.ask("Approve plan and continue?", default=True)

    feedback = "" if approved else Prompt.ask("Feedback")
    return {"scope": scope, "feedback": feedback}

def handle_notebook(data: list) -> str:
    console.print(Panel.fit("[bold yellow]HITL Checkpoint 3 — Review Notebook[/bold yellow]"))
    console.print(f"  {len(data)} cells generated\n")

    for i, cell in enumerate(data, 1):
        color = "cyan" if cell.get("type") == "code" else "yellow"
        title = cell.get("title", cell.get("type", ""))
        console.print(f"  [{color}]{i:>2}.[/{color}] {title}")

    console.print()

    if Confirm.ask("Approve notebook?", default=True):
        return "approved"

    return Prompt.ask("Feedback for regeneration")