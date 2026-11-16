# Adding a task

A task is a folder `tasks/<task>/` with a `scripts/` folder, an `SConscript` and a `README.md`. Its outputs go to
`OUTPUT_ROOT/tasks/<task>/`. Copy a demo task and adapt it.

## 1. Create the folder

```
tasks/03_regressions/
├── scripts/
│   └── run_regressions.py
├── SConscript
└── README.md
```

Start a task's name with a number when it is part of the main chain (`03_...`); the number only helps people
read the order, SCons works it out from the declared inputs.

## 2. Write the script

**Python:**

```python
"""Run the main regressions on the clean panel."""

import pandas as pd

from project_package.paths import data_dir, output_dir, upstream_output


def main() -> None:
    panel = pd.read_csv(upstream_output("01_example_clean") / "panel.csv")   # another task's output
    prices = pd.read_csv(data_dir("BLS") / "ppi.csv")                          # raw data in DATA_ROOT
    ...
    results.to_csv(output_dir(__file__) / "regressions.csv", index=False)     # this task's output folder


if __name__ == "__main__":
    main()
```

**Stata** (and similarly R, Matlab, Julia; see [helpers/README.md](../helpers/README.md)):

```stata
version 18
clear all
run "../../../helpers/project_paths.do"

import delimited using "$TASK_OUTPUT_ROOT/01_example_clean/panel.csv", clear
regress log_output log_capital log_labor
export delimited using "$TASK_OUTPUT_DIR/regressions.csv", replace
```

Write only to the task's own output folder. Never write into another task's folder or into the repo.

## 3. Write the SConscript

```python
"""SConscript for 03_regressions: the main regressions."""

Import("env")

regressions = env.Python(            # env.Stata, env.R, env.Matlab, env.Julia for other languages
    target=env.Out("regressions.csv"),
    source=[
        "scripts/run_regressions.py",
        env.Upstream("01_example_clean", "panel.csv"),
        env.Data("BLS", "ppi.csv"),
    ],
)
env.Register(regressions)
```

For a Stata, R, Matlab or Julia task, wrap the steps in `if env.CheckProgram("stata"):` (see `tasks/example_stata/`)
if the project should still build on machines without that program.

## 4. Write the README

One or two sentences on what the task does, and its inputs:

```markdown
# 03_regressions

Runs the main regressions on the clean panel.

- **Inputs:** `01_example_clean`; `DATA_ROOT/BLS/ppi.csv`.
```

## 5. Build and check

```bash
pixi run build 03_regressions
```

```bash
pixi run test
```

Then look at the log (`tasks/03_regressions/logs/`) and the outputs.

## Putting a result in the paper

1. Add a row to `paper/generated_manifest.csv`: where the file comes from (`source`, as `<task>/<file>`), its name
   under `paper/generated/` (`figures/...` or `tables/...`), the script that makes it, and the documents using it.
2. Use it in the paper: `\input{generated/tables/regressions}` or `\includegraphics{regressions}` (figures are
   looked up in `generated/figures/`).
3. `pixi run build` copies it and checks that every `\input` and `\includegraphics` in `paper/` resolves.
4. Commit the new table in `paper/generated/tables/`; figures are not tracked.

To have a test notice if the result ever changes, record it once you have checked it:

```bash
pixi run python tests/reference.py 03_regressions/regressions.csv
```

## Removing the demo tasks

When your project has its own tasks, delete the demo folders you do not need (`tasks/00_example_raw/` ...
`tasks/example_julia/`), their rows in `paper/generated_manifest.csv` and `tests/reference_outputs.json`, and the
demo text in `paper/main.tex`. Keep `publish/` and `task_graph/`. Then `pixi run build` and `pixi run test`.
