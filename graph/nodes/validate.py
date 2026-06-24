import io
import sys
import traceback

from graph.state import PaperState

def _strip_jupyter_magic(code: str) -> str:
    """Remove !shell and %magic lines — they're Jupyter-only, break exec()."""
    lines = [l for l in code.splitlines() if not l.strip().startswith(("!", "%"))]
    return "\n".join(lines)


def validate_node(state: PaperState) -> dict:
    code_cells = [c for c in state.get("cells", []) if c.get("type") == "code"]
    results  = []

    namespace = {"__name__": "__main__"}
    exec("import matplotlib; matplotlib.use('Agg')", namespace)

    for cell in code_cells:
        code = _strip_jupyter_magic(cell["content"])

        if not code.strip():
            results.append({"title": cell["title"], "passed": True, "output": ""})
            continue

        buf = io.StringIO()
        try:
            old_stdout, sys.stdout = sys.stdout, buf
            exec(code, namespace)
            sys.stdout = old_stdout
            results.append({
                "title":  cell["title"],
                "passed": True,
                "output": buf.getvalue(),
            })
        except Exception:
            sys.stdout = old_stdout
            results.append({
                "title": cell["title"],
                "passed": False,
                "error": traceback.format_exc(),
            })
            break

    has_errors = any(not r["passed"] for r in results)
    retry_count = state.get("retry_count", 0) + (1 if has_errors else 0)

    return {
        "validation_results": results,
        "retry_count": retry_count,
        "status": "validated",
    }