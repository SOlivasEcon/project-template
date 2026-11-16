# Conventions

The rules that keep a project rebuildable by someone else, from the raw data, on another machine.

## Where things live

| What | Where | In git? |
|---|---|---|
| Code, SConscripts, task READMEs | `tasks/<task>/` | yes |
| Shared Python code | `project_package/` | yes |
| Raw data | `DATA_ROOT` (any folder, may be shared) | no |
| Task outputs (data, tables, figures) | `OUTPUT_ROOT/tasks/<task>/` (local disk) | no |
| Logs | `tasks/<task>/logs/` | no |
| Paper and slides | `paper/` | yes |
| Paper tables | `paper/generated/tables/` (copied by publish) | yes, so `git diff` shows changed numbers |
| Paper figures | `paper/generated/figures/` (copied by publish) | no (no images in git) |
| Per-machine settings | `.env` | no; `.env.example` is |

Git never holds data, images or PDFs (`.gitignore` excludes them, and pre-commit blocks files over 1 MB).

## Rules for scripts

- **One script, one job.** Each script reads declared inputs and writes declared outputs; nothing else.
- **Find folders from the script, never hard-code paths.** Python: `output_dir(__file__)`,
  `upstream_output("<task>")`, `data_dir(...)`. Other languages: `helpers/`. No `C:\Users\...` in code.
- **Write only to the task's own output folder.** Read other tasks' outputs, never modify them.
- **Never edit `paper/generated/` by hand.** Change the script that makes the file, then build.
- **Reproducible randomness:** set a seed (`np.random.default_rng(SEED)`, `set seed` in Stata).
- **Python scripts** keep their work under `if __name__ == "__main__":`, so other scripts can import their
  functions (`project_package.paths.import_task_script`).
- **Shared code goes in `project_package/utils/`**, not copied between tasks.
- Text outputs (CSV, `.tex`) are preferable to binary ones: git and the tests can compare them.

## Recorded results

`tests/reference_outputs.json` holds a fingerprint (SHA-256 hash) of outputs you have checked by hand. The test
`tests/test_reference_outputs.py` fails if a recorded output changes, so a silent change after a package update or
a refactor does not go unnoticed. When a change is intended (new data, a method change), look at the new output,
then record it again:

```bash
pixi run python tests/reference.py <task>/<file>
```

Text files are compared regardless of line endings (Windows and macOS agree). Leave figures out: their bytes
differ between systems.

## Packages

Add a Python package with pixi, which updates `pyproject.toml` and `pixi.lock`:

```bash
pixi add <package>
```

Commit both files. Add the package to `requirements.txt` too, with the version `pixi list` shows, for people who
use pip. Stata, R, Matlab and Julia packages are installed in those programs as usual; list them in the README of
the tasks that need them.

## Git

- Commit small, labelled steps. Commit `pixi.lock` whenever it changes.
- Before sharing, run `pixi run build` and `pixi run test`; for a full check on clean machines, run CI.
- The demo tasks and this documentation are part of the template; replace or delete them as your project grows.

## Coauthors

- Each person has their own clone, `.env` and local `OUTPUT_ROOT`, and builds on their own machine.
- `DATA_ROOT` can point to a shared folder (OneDrive, Dropbox, Box), so everyone reads the same raw data.
- To share results without asking coauthors to build, set `SHARED_OUTPUT_ROOT` to a shared folder: `publish`
  copies the paper's figures and tables there.
- Run CI before asking a coauthor to pull, so they are not the first to find a broken build.
