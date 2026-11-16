# project-template

A template for reproducible research projects in economics: Python first, with Stata, R, Matlab and Julia when
needed. One command rebuilds every result from the raw data, in the right order, and reruns only what changed.

- **One folder per task** (`tasks/<task>/`): its scripts, a short README, and an `SConscript` that says which
  files the scripts read and write.
- **[SCons](https://scons.org)** reads those files and runs the tasks in dependency order.
- **[pixi](https://pixi.sh)** installs the same Python, packages and tools on Windows, macOS and Linux.
- **Data and outputs stay outside the repo**, in folders you choose per machine (`.env`): local, OneDrive, Dropbox
  or Box. Git tracks code, the paper and its tables, never data or images.
- **The paper** (`paper/`) is LaTeX; a `publish` task copies the figures and tables it uses into
  `paper/generated/`.

The demo tasks simulate a small firm panel, estimate a production function, and put a table and a figure in the
paper, so a fresh copy builds end to end.

## Start a new project

1. On GitHub, click **Use this template** → **Create a new repository**, then clone it.
2. Install [pixi](https://pixi.sh) and git, if you haven't ([docs/setup.md](docs/setup.md)).
3. In the project folder, set up your names (title, package name, author):
   ```bash
   pixi run python scripts/new_project.py
   ```
   ```bash
   pixi install
   ```
4. Copy `.env.example` to `.env` and set at least `OUTPUT_ROOT` (see [Settings](#settings-env)).
5. Build everything, then run the tests:
   ```bash
   pixi run build
   ```
   ```bash
   pixi run test
   ```
6. Check `git diff`, commit, and replace this README's text with your project's description.

## Everyday commands

Run these in a terminal in the project folder. pixi installs everything the first time.

| Command | What it does |
|---|---|
| `pixi run build` | Run every task whose scripts or inputs changed; a second run does nothing |
| `pixi run build 02_example_analysis` | Build one task (and whatever it needs first) |
| `pixi run clean` | Delete all task outputs and logs (the paper's tables in `paper/generated/` stay) |
| `pixi run test` | Run the tests in `tests/` |
| `pixi run task-graph` | Draw how the tasks depend on each other: `docs/task_graph.png` |
| `pixi run python path/to/script.py` | Run one Python script with the project's Python |

`pixi run build` is a shortcut for `python -m SCons`. In PyCharm, the run configurations **Build all**, **Tests**
and **Clean** do the same (see [docs/setup.md](docs/setup.md#pycharm)).

Then compile the paper from `paper/` with `latexmk` (see [LaTeX](#latex)).

## Layout

```
├── tasks/                 one folder per task, built in dependency order
│   ├── 00_example_raw/       scripts/, SConscript, README.md (lists its inputs), logs/ (not tracked)
│   ├── 01_example_clean/
│   ├── 02_example_analysis/
│   ├── example_stata/ example_r/ example_matlab/ example_julia/   skipped if the program isn't found
│   ├── publish/              copies the paper's figures and tables into paper/generated/
│   └── task_graph/           draws docs/task_graph.png (on request only)
├── project_package/       shared Python code: settings (config.py), folders (paths.py), helpers (utils/)
├── helpers/               the same folder lookup for Stata, R, Matlab and Julia scripts
├── paper/                 main.tex, references.bib, slides/, generated/ (filled by publish)
├── tests/                 checks of the layout, the settings and recorded results
├── docs/                  setup, SCons, adding a task, conventions
├── scripts/new_project.py one-time setup of a new project
├── SConstruct             the build: how scripts are run and logged
├── pyproject.toml         Python packages and tools (pixi), pixi shortcuts, Ruff and pytest settings
├── pixi.lock              exact versions of everything pixi installs (generated; commit it)
├── requirements.txt       the same packages for pip, if you don't use pixi
├── .env.example           settings to copy into .env (per machine, never committed)
└── .github/workflows/     CI: build and test on Windows and macOS, on request
```

A task's outputs go to `OUTPUT_ROOT/tasks/<task>/`, outside the repo. Each script finds its folders by itself
(Python: `project_package.paths`; other languages: `helpers/`), so it runs the same through SCons, from PyCharm or
RStudio, or from a terminal. See [docs/adding_a_task.md](docs/adding_a_task.md).

## Settings (`.env`)

`.env` holds the settings that differ between machines. Copy `.env.example` and fill in:

| Setting | Meaning |
|---|---|
| `OUTPUT_ROOT` | Required. Task outputs go to `OUTPUT_ROOT/tasks/<task>/`. Keep it on a local disk, not a synced folder |
| `DATA_ROOT` | Raw data. Any folder: local, or a cloud folder shared with coauthors |
| `SHARED_OUTPUT_ROOT` | Optional. `publish` also copies the paper's figures and tables here, e.g. for coauthors |
| `STATA_EXE`, `R_EXE`, `MATLAB_EXE`, `JULIA_EXE` | Optional. Where each program is, if it isn't found on PATH |

Paths may start with `~` (your home folder); relative paths start at the project folder. An environment variable
with the same name overrides `.env`; this is how CI sets `OUTPUT_ROOT`. If a setting seems to be ignored, check
that no such variable is set on your machine.

**Why outputs should not be in OneDrive, Dropbox or Box:** SCons keeps its record of what it built inside each
copy of the project. When two machines write to one synced output folder, each rebuilds the other's work, and the
sync service may lock files mid-build or create "conflicted copies". Raw data in a shared folder is fine.

## LaTeX

LaTeX is only needed to compile `paper/main.tex` and `paper/slides/slides.tex`. The build and the publish task
don't use it. Compile from the document's folder:

```bash
latexmk
```

(in `paper/`; `paper/latexmkrc` holds the settings), or `latexmk -pdf slides.tex` in `paper/slides/`.

This template was built and tested on Windows 11 with **MiKTeX 25.12** (pdfTeX 4.23), **latexmk 4.88** and
**Strawberry Perl 5.42.3**. latexmk is a Perl script and MiKTeX does not include Perl, hence Strawberry Perl;
TeX Live on Windows, and macOS, already have Perl.

**Any TeX setup works**: TeX Live, MacTeX, Overleaf, Tectonic, or your editor's build button. The only
requirement is to compile each document from its own folder, because the paths to the figures and tables
(`generated/...`, `../generated/...`) are relative to it. The packages used are standard: `geometry`, `amsmath`,
`booktabs`, `caption`, `graphicx`, `natbib`, `hyperref` and `beamer`.

## Checks: tests, pre-commit and CI

- `pixi run test` checks the layout (every task has its files), the settings, and that recorded results have
  not changed ([docs/conventions.md](docs/conventions.md#recorded-results)).
- **pre-commit** runs Ruff (Python style and likely bugs) and small file checks, including a 1 MB limit that keeps
  data out of git. Turn it on once per copy with `pixi run pre-commit install`; it then runs on every commit.
- **CI** (`.github/workflows/ci.yml`) builds the project from scratch and runs the tests on Windows and macOS,
  only when you ask: GitHub → **Actions** → **CI** → **Run workflow**. See [docs/setup.md](docs/setup.md#ci).

## Credits and license

Layout and SCons design inspired by
[shihhsuanhsu/project-template](https://github.com/shihhsuanhsu/project-template). pixi, pre-commit, CI and
`AGENTS.md` follow ideas from
[OpenSourceEconomics/econ-project-templates](https://github.com/OpenSourceEconomics/econ-project-templates).

MIT license: see [LICENSE](LICENSE).
