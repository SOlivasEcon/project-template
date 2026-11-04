"""Path helpers so every script finds its folders from its own location.

A script at `tasks/<task>/scripts/x.py` calls `output_dir(__file__)`, which is `OUTPUT_ROOT/tasks/<task>/`
(outside the repo; see `project_package.config`). Nothing depends on the working directory, so scripts behave
the same from PyCharm's Run button, a terminal or SCons.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

# Repo root and the folder holding all tasks.
REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"


def task_dir(script_file: str) -> Path:
    """Return the task folder for a script located at tasks/<task>/scripts/<name>.py."""
    return Path(script_file).resolve().parents[1]


def task_output_dir(task_name: str) -> Path:
    """Return OUTPUT_ROOT/tasks/<task_name>/, the folder holding a task's outputs (not created)."""
    from project_package.config import TASK_OUTPUT_ROOT  # imported here so REPO_ROOT needs no .env

    return TASK_OUTPUT_ROOT / task_name


def output_dir(script_file: str) -> Path:
    """Return (creating it if needed) the output folder of the task that owns `script_file`."""
    out = task_output_dir(task_dir(script_file).name)
    out.mkdir(parents=True, exist_ok=True)
    return out


def upstream_output(task_name: str) -> Path:
    """Return the output folder of another task, e.g. upstream_output('01_example_clean').

    Declare the files read from it as sources in the reading task's SConscript (`env.Upstream`)
    so SCons rebuilds correctly.
    """
    return task_output_dir(task_name)


def data_dir(*parts: str) -> Path:
    """Return DATA_ROOT/<parts>, e.g. data_dir('BLS', 'raw'); fails with a clear message if DATA_ROOT is unset.

    Declare the raw files read from it as sources in the task's SConscript (`env.Data`).
    """
    from project_package.config import required_path

    return required_path("DATA_ROOT").joinpath(*parts)


def import_task_script(task_name: str, script_name: str) -> ModuleType:
    """Import tasks/<task_name>/scripts/<script_name>.py as a module, to reuse another task's functions.

    Task scripts are not a package, so they are loaded from their file. Only module-level code runs
    (scripts keep their work under `if __name__ == "__main__"`). Declare the imported script as a source
    in the importing task's SConscript so a change to it triggers a rebuild.
    """
    path = TASKS_DIR / task_name / "scripts" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(f"task_{task_name}_{script_name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
