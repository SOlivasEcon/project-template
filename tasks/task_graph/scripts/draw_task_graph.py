"""Draw how the tasks depend on each other, as docs/task_graph.png (needs Graphviz's `dot`, installed by pixi).

Reads each tasks/<task>/SConscript: an arrow A -> B means B reads A's outputs (`env.Upstream("A", ...)`), and the
publish task reads every task named in paper/generated_manifest.csv. Box colors show each task's language;
a dashed box is a task outside the default build (no `env.Register`), built only on request.
"""

import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUTPUT = REPO / "docs" / "task_graph.png"
THIS_TASK = Path(__file__).resolve().parents[1].name

# Builder name -> box color.
COLORS = {"Python": "#dbe9f6", "Stata": "#fde2c8", "R": "#d9f0d3", "Matlab": "#fbd9d3", "Julia": "#e8dcf3"}


def read_tasks() -> dict[str, dict]:
    """Return {task: {"languages": [...], "upstream": {...}, "registered": bool}} from the SConscripts."""
    tasks = {}
    for sconscript in sorted(REPO.glob("tasks/*/SConscript")):
        task = sconscript.parent.name
        if task == THIS_TASK:
            continue
        text = sconscript.read_text(encoding="utf-8")
        tasks[task] = {
            "languages": sorted(set(re.findall(r"env\.(" + "|".join(COLORS) + r")\(", text))),
            "upstream": set(re.findall(r"env\.Upstream\(\s*[\"']([^\"']+)", text)),
            "registered": "env.Register(" in text,
        }
    if "publish" in tasks:
        with open(REPO / "paper" / "generated_manifest.csv", newline="", encoding="utf-8") as f:
            tasks["publish"]["upstream"] |= {row["source"].split("/", 1)[0] for row in csv.DictReader(f)}
    return tasks


def dot_source(tasks: dict[str, dict]) -> str:
    """Return the graph in Graphviz's DOT language."""
    lines = [
        "digraph tasks {",
        '  rankdir=LR; node [shape=box, style="rounded,filled", fontname="Helvetica"];',
    ]
    for task, info in tasks.items():
        color = COLORS.get(info["languages"][0], "white") if info["languages"] else "white"
        style = '"rounded,filled"' if info["registered"] else '"rounded,filled,dashed"'
        lines.append(f'  "{task}" [fillcolor="{color}", style={style}];')
    for task, info in tasks.items():
        lines += [f'  "{upstream}" -> "{task}";' for upstream in sorted(info["upstream"])]
    lines.append("}")
    return "\n".join(lines) + "\n"


def render(dot: str, source: str) -> subprocess.CompletedProcess:
    """Run `dot` to turn the DOT source into OUTPUT."""
    command = [dot, "-Tpng", "-Gdpi=150", "-o", str(OUTPUT)]
    return subprocess.run(command, input=source, text=True, capture_output=True, check=False)


def main() -> None:
    dot = shutil.which("dot")
    if dot is None:
        sys.exit("Graphviz's `dot` not found: run this through pixi (`pixi run task-graph`) or install Graphviz.")
    source = dot_source(read_tasks())
    print(source)
    OUTPUT.parent.mkdir(exist_ok=True)
    result = render(dot, source)
    if result.returncode != 0:
        # Graphviz from conda-forge registers its output formats (png, ...) in an install step that pixi skips;
        # `dot -c` does that registration, then try again.
        print(f"dot failed:\n{result.stderr}\nRegistering Graphviz plugins (dot -c) and retrying.")
        subprocess.run([dot, "-c"], check=False)
        result = render(dot, source)
    if result.returncode != 0:
        sys.exit(f"dot failed:\n{result.stderr}")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
