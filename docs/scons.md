# SCons in this project

SCons is the build tool: it knows which script produces which file from which inputs, and reruns a script only
when the script or one of its inputs changed. You describe each task once, in its `SConscript`; SCons works out
the order.

## Commands

```bash
pixi run build                      # build everything in the default build
pixi run build 01_example_clean     # one task, after whatever it needs
pixi run build -j 4                 # run up to 4 scripts at once
pixi run clean                      # delete all task outputs and logs
pixi run build -n                   # dry run: list what would run, run nothing
```

`pixi run build` is `python -m SCons`; any SCons option can follow it.

## How a build works

1. SCons reads `SConstruct` (the project's build settings) and every `tasks/*/SConscript`.
2. Each SConscript declares steps: "this script, reading these inputs, writes these outputs".
3. SCons runs a step when an output is missing, or when the script or an input changed since the last build. A
   file counts as changed when its contents changed: saving a file without changing it, or rebuilding an
   input that comes out identical, triggers nothing. (To be fast, SCons only reads a file's contents when its
   modification time changed.)
4. A step's outputs are inputs of later steps, so changing one script reruns exactly what depends on it.

SCons keeps its record of past builds in `.sconsign.dblite` in the project folder (not tracked by git). Each copy
of the project has its own record; that is why `OUTPUT_ROOT` should not be shared between machines.

## Anatomy of an SConscript

```python
"""SConscript for 01_example_clean: drop bad rows from the toy panel and add logs."""

Import("env")                                   # the build settings from SConstruct

panel = env.Python(                             # run a Python script
    target=env.Out("panel.csv"),                # what it writes: OUTPUT_ROOT/tasks/01_example_clean/panel.csv
    source=[
        "scripts/clean_panel.py",               # the script itself comes first
        env.Upstream("00_example_raw", "raw_panel.csv"),   # what it reads from another task
    ],
)
env.Register(panel)                             # part of the default build, and of `pixi run build 01_example_clean`
```

| In an SConscript | Meaning |
|---|---|
| `env.Python`, `env.Stata`, `env.R`, `env.Matlab`, `env.Julia` | Run the first source with that program, from its own folder; output goes to `logs/<script>.log` |
| `env.Out("a.csv", "b.png")` | This task's output files, in `OUTPUT_ROOT/tasks/<task>/` |
| `env.Upstream("<task>", "file.csv")` | Another task's output, read as an input |
| `env.Data("BLS", "ppi.csv")` | A raw file in `DATA_ROOT`, read as an input |
| `"#/project_package/utils/x.py"` | A file in the repo (`#` is the project folder), read as an input |
| `env.Register(targets)` | Add to the default build. Without it, the task builds only when named |
| `env.CheckProgram("stata")` | True if Stata is found; otherwise prints that the task is skipped |

Every script automatically depends on `project_package/config.py` and `paths.py` (and, for Stata, R, Matlab and
Julia, on its file in `helpers/`), so changing how folders are found reruns everything.

## What to declare

Declare every file a script reads (as a source) and every file it writes (as a target). If a script reads a file
that is not declared, SCons will not rerun it when that file changes; if it writes an undeclared file, `clean`
will not remove it and later tasks cannot depend on it. The tests check part of this: every script and upstream
task named in an SConscript must exist.

## Logs and errors

Everything a script prints goes to `tasks/<task>/logs/<script>.log`, overwritten on each run and not tracked by
git. When a script fails, the build stops and prints the last lines of its log. Stata always reports success, so
the build reads Stata's log and fails on its error lines (`r(198);`). A Python script that crashes hard leaves a
traceback in its log.

## Work in progress

A script that no SConscript mentions is not part of the build: write and run it on its own until it works.
Add it to the SConscript when its outputs are needed by other tasks. A task without `env.Register(...)` builds
only on request (`pixi run build <task>`), which suits exploratory work.
