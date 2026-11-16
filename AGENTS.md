# Instructions for AI coding assistants

This file tells AI coding assistants (Claude Code, Codex, Cursor, ...) how this project works. People should read
[README.md](README.md) and [docs/](docs/) instead.

## The project

A reproducible research project: one folder per task in `tasks/`, built in dependency order by SCons; Python
first, Stata, R, Matlab and Julia where needed; a LaTeX paper in `paper/`. pixi installs the environment
(`pyproject.toml`, `pixi.lock`). Raw data (`DATA_ROOT`) and task outputs (`OUTPUT_ROOT/tasks/<task>/`) live outside
the repo; their locations are set per machine in `.env`.

The user is an economist. Prefer the simplest approach that works and explain choices in plain terms. Do not add
tools, dependencies or commands without asking.

## Commands

| Command | Use |
|---|---|
| `pixi run build` | Build what changed (`python -m SCons`); add a task name to build one task |
| `pixi run test` | Tests; needs a finished build |
| `pixi run clean` | Delete task outputs and logs |
| `pixi run python <script>` | Run one script with the project's Python (`python` alone may not be on PATH) |
| `pixi run pre-commit run --all-files` | Ruff and file checks |
| `latexmk` in `paper/` | Compile the paper (needs a local TeX installation; any TeX setup is fine, see README) |

After changing code, run `pixi run build` and `pixi run test` and report the result. A second build should
report "up to date".

## Where things are

- `tasks/<task>/`: `scripts/`, `SConscript` (declares each script's inputs and outputs), `README.md` (one or two
  sentences and an **Inputs:** line). Logs in `tasks/<task>/logs/` (not tracked).
- `SConstruct`: the builders (`env.Python`, `env.Stata`, `env.R`, `env.Matlab`, `env.Julia`) and the helpers
  `env.Out`, `env.Upstream`, `env.Data`, `env.Register`, `env.CheckProgram`. Explained in `docs/scons.md`.
- `project_package/`: settings (`config.py`, reads `.env`), folder lookup (`paths.py`), shared code (`utils/`).
- `helpers/project_paths.{do,R,m,jl}`: folder lookup for non-Python scripts.
- `paper/`: `main.tex`, `slides/`, `generated/` (filled by `tasks/publish` from `paper/generated_manifest.csv`).
- `tests/`: layout checks, settings checks, and recorded output hashes (`tests/reference.py`).

## Rules

- Scripts find their folders through `project_package.paths` (`output_dir(__file__)`, `upstream_output(...)`,
  `data_dir(...)`) or `helpers/`. Never hard-code absolute paths or machine-specific folders.
- A script writes only to its own task's output folder. It never writes into the repo or another task's folder.
- Declare every input and output of a script in its task's `SConscript`; keep the task README's **Inputs:** line
  up to date. New tasks follow `docs/adding_a_task.md`.
- Never edit files in `paper/generated/` by hand; change the producing script and build.
- Never commit data, images, PDFs, logs or `.env`. Commit `pixi.lock` whenever it changes.
- Add Python packages with `pixi add <package>`, and mirror the pinned version in `requirements.txt`.
- Code must work on Windows and macOS: no shell commands (`cp`, `cmd /c`, `.bat`) in the build, use `pathlib` or
  `os.path` for paths, and write text files with explicit encodings.
- Set a seed for anything random. Prefer text outputs (CSV, `.tex`) over binary ones.
- Do not change recorded results in `tests/reference_outputs.json` to make a test pass. A changed output is a
  finding: report it, and re-record only after the user confirms the change is intended.
- Do not push, run CI or change GitHub settings unless the user asks.
