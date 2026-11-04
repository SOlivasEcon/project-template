"""Checks of the repo layout: every task follows the conventions the build and the docs rely on."""

import csv
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TASKS = sorted(p for p in (REPO / "tasks").iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


@pytest.mark.parametrize("task", TASKS, ids=lambda p: p.name)
def test_task_has_sconscript_readme_and_scripts(task):
    for name in ["SConscript", "README.md", "scripts"]:
        assert (task / name).exists(), f"{task.name} has no {name}"


@pytest.mark.parametrize("task", TASKS, ids=lambda p: p.name)
def test_readme_lists_inputs(task):
    assert "**Inputs:**" in (task / "README.md").read_text(encoding="utf-8"), f"{task.name}/README.md lists no inputs"


@pytest.mark.parametrize("task", TASKS, ids=lambda p: p.name)
def test_sconscript_scripts_exist(task):
    """Every scripts/<file> named in an SConscript exists."""
    for script in re.findall(r"[\"'](scripts/[^\"']+)[\"']", (task / "SConscript").read_text(encoding="utf-8")):
        assert (task / script).is_file(), f"{task.name}/SConscript names missing {script}"


@pytest.mark.parametrize("task", TASKS, ids=lambda p: p.name)
def test_upstream_tasks_exist(task):
    """Every task named in env.Upstream(...) exists."""
    for upstream in re.findall(r"env\.Upstream\(\s*[\"']([^\"']+)", (task / "SConscript").read_text(encoding="utf-8")):
        assert (REPO / "tasks" / upstream).is_dir(), f"{task.name} reads from unknown task {upstream}"


def test_manifest_sources_come_from_existing_tasks():
    with open(REPO / "paper" / "generated_manifest.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            task = row["source"].split("/", 1)[0]
            assert (REPO / "tasks" / task).is_dir(), f"manifest source {row['source']}: no task {task}"
            assert (REPO / row["producing_script"]).is_file(), f"manifest: {row['producing_script']} not found"


@pytest.mark.parametrize("extension", ["do", "R", "m", "jl"])
def test_language_helper_exists(extension):
    assert (REPO / "helpers" / f"project_paths.{extension}").is_file()
