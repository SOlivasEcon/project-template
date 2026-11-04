# helpers

One small file per language that gives a task script its folders, the way `project_package.paths` does for
Python. Each reads `OUTPUT_ROOT` and `DATA_ROOT` from `.env` (an environment variable with the same name wins), so
a script runs the same through SCons and on its own (Stata do-file editor, RStudio, the Matlab desktop, a terminal).

| Language | File | At the top of a script in `tasks/<task>/scripts/` |
|---|---|---|
| Stata | `project_paths.do` | `run "../../../helpers/project_paths.do"`, then `$TASK_OUTPUT_DIR`, `$TASK_OUTPUT_ROOT`, `$DATA_ROOT` |
| R | `project_paths.R` | `source("../../../helpers/project_paths.R")` and `paths <- project_paths()` |
| Matlab | `project_paths.m` | `addpath(fullfile(pwd, "..", "..", "..", "helpers"))` and `paths = project_paths();` |
| Julia | `project_paths.jl` | `include(joinpath(@__DIR__, "..", "..", "..", "helpers", "project_paths.jl"))` and `paths = project_paths(@__DIR__)` |

Stata, R and Matlab find the task from the **working directory**, which must be the script's own folder. SCons
always runs scripts from there. Interactively: open Stata by double-clicking the do-file (or `cd` there); in
RStudio, Session > Set Working Directory > To Source File Location; in Matlab, choose "Change Folder" when asked.
Julia uses the script's location (`@__DIR__`) and works from anywhere.

If the first line fails with "file not found" (Stata), "cannot open the connection" (R) or "Unrecognized function
or variable 'project_paths'" (Matlab), the working directory is not the script's folder.

A draft script needs no SConscript entry: it is simply not part of the build until you add it there.
