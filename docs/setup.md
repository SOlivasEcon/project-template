# Setup

What to install on a new machine, Windows or macOS, and how to set up PyCharm. Only pixi and git are required;
the rest depends on what your project uses.

## 1. Install the tools

| Tool | Needed for | Windows | macOS |
|---|---|---|---|
| **git** | everything | [git-scm.com](https://git-scm.com) or `winget install Git.Git` | `xcode-select --install` |
| **pixi** | everything: it installs Python, SCons, Graphviz and the packages | see below | see below |
| **LaTeX** | compiling the paper only | MiKTeX + [Strawberry Perl](https://strawberryperl.com), or TeX Live | MacTeX |
| Stata, R, Matlab, Julia | only tasks in that language | usual installer | usual installer |

Install pixi with the command from [pixi.sh](https://pixi.sh). In PowerShell (Windows):

```bash
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

In Terminal (macOS):

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

Open a new terminal afterwards and check with `pixi --version`.

You do not need to install Python: pixi installs the project's own Python (3.13) into `.pixi/` inside the project
folder, with the exact package versions in `pixi.lock`. A second project reuses pixi's download cache, so it costs
little extra disk space. Your other Python installations (Anaconda, python.org) are left alone.

## 2. Get the project and its environment

```bash
git clone https://github.com/<owner>/<project>.git
```

Then, in the project folder:

```bash
pixi install
```

This creates `.pixi/envs/default/` (a few minutes the first time). Any `pixi run ...` command also does it.

## 3. Create `.env`

Copy `.env.example` to `.env` in the project folder and set at least `OUTPUT_ROOT`, a local folder for task
outputs, e.g. `C:\Users\you\Documents\myproject-output` or `~/myproject-output`. The README's
[Settings](../README.md#settings-env) section explains every setting.

Stata, R, Matlab and Julia are found on PATH. If one is not (Stata usually isn't on Windows), set its full path:

| Setting | Windows example | macOS example |
|---|---|---|
| `STATA_EXE` | `C:\Program Files\Stata18\StataMP-64.exe` | `/Applications/Stata/StataMP.app/Contents/MacOS/stata-mp` |
| `R_EXE` | `C:\Program Files\R\R-4.6.1\bin\Rscript.exe` (Rscript, not R) | `/usr/local/bin/Rscript` |
| `MATLAB_EXE` | `C:\Program Files\MATLAB\R2024a\bin\matlab.exe` | `/Applications/MATLAB_R2024a.app/bin/matlab` |
| `JULIA_EXE` | `C:\Users\you\AppData\Local\Programs\Julia-1.x.x\bin\julia.exe` | `~/.juliaup/bin/julia` |

A task whose program is not found is skipped, with a message naming the setting.

## 4. Build

```bash
pixi run build
```

```bash
pixi run test
```

The demo build takes about a minute (Stata and Matlab are slow to start). A second `pixi run build` reports
"up to date".

## PyCharm

1. **File → Open** the project folder; trust it if asked.
2. Set the interpreter: click the interpreter name at the bottom right → **Add New Interpreter → Add Local
   Interpreter… → Select existing**, and choose the pixi environment's Python:
   - Windows: `<project>\.pixi\envs\default\python.exe`
   - macOS: `<project>/.pixi/envs/default/bin/python`
3. Wait for indexing to finish. Imports such as `from project_package.paths import ...` should not be underlined.
4. The run configurations **Build all**, **Tests** and **Clean** appear in the dropdown at the top right. You can
   also right-click any Python script → **Run**.

PyCharm starts this Python directly, without pixi's activation step (which `pixi run` does). The template's
packages work that way, but if a script crashes in PyCharm and not with `pixi run python <script>`, that
difference is the likely cause.

## Without pixi (pip)

If you cannot use pixi, any Python 3.13 environment works, e.g. a new Anaconda environment for the project:

```bash
python -m pip install -r requirements.txt
```

```bash
python -m pip install -e .
```

Then use `python -m SCons` for the build and `python -m pytest` for the tests. `requirements.txt` pins the same
package versions as `pixi.lock`, but not Python itself or system libraries, so results can differ slightly.
Graphviz (only for the task graph) must be installed separately.

## pre-commit

Once per copy of the project, turn on the checks that run before each commit:

```bash
pixi run pre-commit install
```

On each `git commit` (also from PyCharm), Ruff and a few file checks run first. If they fix something, such as
trailing spaces, the commit stops with "files were modified by this hook": look at the change, then commit again.
To run the checks on every file at any time: `pixi run pre-commit run --all-files`.

## CI

CI runs the whole build and the tests on fresh Windows and macOS machines at GitHub, as a check that the project
rebuilds from scratch anywhere. Stata and Matlab need licenses, so those tasks are skipped there.

It runs only when you ask: on GitHub, **Actions** → **CI** → **Run workflow** → choose the branch → **Run
workflow**. Results show as a green check or a red cross; click a failed job and step to see its output.
Use **Run workflow** after changing code; **Re-run jobs** on an old run repeats it on that run's old commit.

Cost: on a private repository each run uses about 75 of GitHub's monthly free Actions minutes (macOS minutes count
10 times). Public repositories have no limit. To run CI on every push instead, add `push:` and `pull_request:`
under `on:` in `.github/workflows/ci.yml`. To turn it off: repository **Settings → Actions → Disable actions**.

## Troubleshooting

- **A setting in `.env` seems ignored:** an environment variable with the same name wins. Check with
  `echo $env:OUTPUT_ROOT` (PowerShell) or `echo $OUTPUT_ROOT` (macOS).
- **`python` is not found, or opens the Microsoft Store:** use `pixi run python ...`; pixi's Python is not on PATH.
- **A Stata, R or Matlab script fails on its first line** ("file not found", "cannot open the connection",
  "Unrecognized function or variable 'project_paths'"): its working directory is not its own folder. See
  [helpers/README.md](../helpers/README.md).
- **`latexmk` fails on Windows with a Perl error:** install Strawberry Perl, or use TeX Live.
