"""Per-machine settings, read from `.env` in the repo root (see `.env.example`).

DATA_ROOT holds the raw inputs and OUTPUT_ROOT every task's results (`OUTPUT_ROOT/tasks/<task>/`, see
`project_package.paths`). Both live outside the repo, in any local or cloud-synced folder. Variables already
set in the environment (e.g. by CI) take precedence over `.env`. Paths may start with `~`; relative paths
are read from the repo root.
"""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

# Repo root; `.env` lives here and is never committed.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def optional_path(name: str) -> Path | None:
    """Return the path stored in environment variable `name`, or None when it is unset or empty."""
    value = os.getenv(name, "").strip()
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def required_path(name: str) -> Path:
    """Return the path stored in environment variable `name`, or fail with a clear message."""
    path = optional_path(name)
    if path is None:
        raise RuntimeError(f"{name} not set. Add it to {PROJECT_ROOT / '.env'} (see .env.example).")
    return path


# Task outputs go to OUTPUT_ROOT/tasks/<task>/. Every build needs it.
OUTPUT_ROOT = required_path("OUTPUT_ROOT")
TASK_OUTPUT_ROOT = OUTPUT_ROOT / "tasks"

# Raw inputs. Optional here so the demo tasks, which simulate their data, build without it; scripts read it
# through `paths.data_dir()`, which fails with a clear message when it is missing.
DATA_ROOT = optional_path("DATA_ROOT")

# Optional folder shared with coauthors, which the publish task copies final results into.
SHARED_OUTPUT_ROOT = optional_path("SHARED_OUTPUT_ROOT")

# Programs for non-Python tasks: the `.env` variable that points to each, and the names tried on PATH otherwise.
PROGRAMS = {
    "stata": ("STATA_EXE", ["StataMP-64", "StataSE-64", "StataBE-64", "stata-mp", "stata-se", "stata"]),
    "r": ("R_EXE", ["Rscript"]),
    "matlab": ("MATLAB_EXE", ["matlab"]),
    "julia": ("JULIA_EXE", ["julia"]),
}


def program_path(language: str) -> str | None:
    """Return the executable for `language` ('stata', 'r', 'matlab', 'julia'), or None if it is not found.

    Uses the `.env` variable when set (and fails if it points to a missing file), otherwise searches PATH.
    """
    variable, names = PROGRAMS[language]
    path = optional_path(variable)
    if path is not None:
        if not path.is_file():
            raise RuntimeError(f"{variable}={path} (from .env or the environment) is not a file.")
        return str(path)
    return next((found for name in names if (found := shutil.which(name))), None)
