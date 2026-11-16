"""Root build file: `python -m SCons` (or `pixi run build`) runs every task in dependency order.

    python -m SCons                    # build everything registered (a second run does nothing)
    python -m SCons -j 4               # build in parallel
    python -m SCons 01_example_clean   # build one task (and what it depends on)
    python -m SCons -c                 # delete all task outputs and logs

Each task folder tasks/<task>/ has an SConscript that declares which files its scripts read and write.
SCons uses those declarations to decide what to rerun after a script or an input changes.

Builders: env.Python, env.Stata, env.R, env.Matlab, env.Julia. Each runs one script with the script's own folder
as the working directory and writes everything it prints to tasks/<task>/logs/<script>.log, which is a target
too (so `-c` removes it). Scripts find their folders themselves, from `.env`: Python through
`project_package.paths`, the other languages through helpers/project_paths.* (see helpers/README.md). So a script
runs the same through SCons and on its own. Stata, R, Matlab and Julia come from STATA_EXE, R_EXE, MATLAB_EXE and
JULIA_EXE in `.env`, or from PATH.

Layout and SCons design inspired by shihhsuanhsu/project-template
(https://github.com/shihhsuanhsu/project-template).
"""

import os
import re
import shutil
import subprocess
import sys

from SCons.Script import Action, Builder, Default, Environment, Glob, SConscript

from project_package.config import PROGRAMS, program_path, required_path
from project_package.paths import task_output_dir

# Files every script relies on to find its folders; each script's build depends on them.
SHARED_SOURCES = ["#/project_package/__init__.py", "#/project_package/config.py", "#/project_package/paths.py"]
HELPERS = {
    "stata": "#/helpers/project_paths.do",
    "r": "#/helpers/project_paths.R",
    "matlab": "#/helpers/project_paths.m",
    "julia": "#/helpers/project_paths.jl",
}

# Language name (as in project_package.config.PROGRAMS) -> name shown in messages.
LANGUAGES = {"python": "Python", "stata": "Stata", "r": "R", "matlab": "Matlab", "julia": "Julia"}


def log_node(script):
    """Return the node for tasks/<task>/logs/<script>.log, given the node of tasks/<task>/scripts/<script>."""
    return script.dir.up().Dir("logs").File(os.path.splitext(script.name)[0] + ".log")


def command_for(language, executable, script_name):
    """Return the command line that runs `script_name` in batch mode, from the script's folder."""
    if language == "python":
        return [executable, script_name]
    if language == "stata":
        # Batch mode: Stata writes <script>.log next to the script and returns 0 even when the do-file fails.
        return [executable, "/e" if sys.platform == "win32" else "-b", "do", script_name]
    if language == "r":
        return [executable, script_name]
    if language == "matlab":
        # -batch (R2019a+): no desktop, exits when done, non-zero exit code on an error.
        return [executable, "-batch", f"run('{script_name}')"]
    if language == "julia":
        return [executable, script_name]
    raise ValueError(f"unknown language {language}")


def stata_failed(script, log):
    """Move Stata's own log (<script>.log next to the script) into `log`; return True if it shows an error.

    Stata reports an error as a line like `r(601);` and stops the do-file there.
    """
    stata_log = os.path.splitext(script)[0] + ".log"
    if not os.path.isfile(stata_log):
        with open(log, "a", encoding="utf-8") as f:
            f.write("\nStata wrote no log: the do-file did not run.\n")
        return True
    shutil.move(stata_log, log)
    with open(log, encoding="utf-8", errors="replace") as f:
        return re.search(r"^r\(\d+\);\s*$", f.read(), re.MULTILINE) is not None


def run_script(target, source, env, language):
    """Run the first source with the program for `language`. Further sources only declare inputs.

    Returns the exit code; on failure, prints the end of the log so the error shows in the terminal.
    """
    script, log = source[0], log_node(source[0]).abspath
    executable = sys.executable if language == "python" else program_path(language)
    if executable is None:
        print(f"*** {LANGUAGES[language]} not found: set {PROGRAMS[language][0]} in .env (see .env.example).")
        return 1

    os.makedirs(os.path.dirname(log), exist_ok=True)
    # Python: write figures without a window, print in order (unbuffered), and on a hard crash write the Python
    # traceback to the log (faulthandler) instead of exiting silently.
    child_env = {
        **os.environ,
        "MPLBACKEND": "Agg",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1",
        "PYTHONFAULTHANDLER": "1",
    }
    with open(log, "w", encoding="utf-8") as f:
        code = subprocess.run(
            command_for(language, executable, script.name),
            check=False, cwd=script.dir.abspath, env=child_env, stdout=f, stderr=subprocess.STDOUT,
        ).returncode
    if language == "stata" and stata_failed(script.abspath, log):
        code = code or 1
    if code:
        print(f"*** {script} failed (exit code {code}). Last lines of {log}:")
        with open(log, encoding="utf-8", errors="replace") as f:
            print("".join(f.readlines()[-15:]))
    return code


def make_builder(language):
    """Builder that runs a script in `language`; prints e.g. 'stata tasks/x/scripts/y.do' when it runs.

    Adds the script's log as a target, and the shared package files (plus the language's paths helper)
    as sources.
    """
    shared = SHARED_SOURCES + ([HELPERS[language]] if language in HELPERS else [])

    def action(target, source, env):
        return run_script(target, source, env, language)

    def emitter(target, source, env):
        return list(target) + [log_node(source[0])], list(source) + [env.File(s) for s in shared]

    return Builder(action=Action(action, f"{language} $SOURCE"), emitter=emitter)


# tools=[]: no compiler detection, which is slow on Windows and not needed here.
env = Environment(ENV=os.environ, tools=[])
# Hash a file only when its timestamp changed; avoids re-hashing large raw files on every build.
env.Decider("MD5-timestamp")
env.Append(BUILDERS={name: make_builder(language) for language, name in LANGUAGES.items()})

# Targets that make up the default build. Tasks add theirs with `env.Register(targets)`; tasks that never
# register (work in progress, on-demand outputs) are built only when named: `python -m SCons <task>`.
default_targets = []


def register(env, targets):
    """Add `targets` to the default build and to an alias named after the task (`python -m SCons <task>`)."""
    default_targets.extend(targets)
    env.Alias(env.Dir(".").name, targets)
    return targets


def own_output(env, *names):
    """Files in the calling task's output folder, OUTPUT_ROOT/tasks/<task>/ (outside the repo)."""
    return [env.File(str(task_output_dir(env.Dir(".").name) / name)) for name in names]


def upstream(env, task, *names):
    """Files in another task's output folder, to declare as sources of the calling task."""
    return [env.File(str(task_output_dir(task) / name)) for name in names]


def raw_data(env, *parts):
    """A raw input file under DATA_ROOT, e.g. env.Data('BLS', 'raw', 'ppi.csv'), to declare as a source."""
    return env.File(str(required_path("DATA_ROOT").joinpath(*parts)))


def check_program(env, language):
    """Return True if the program for `language` is found; otherwise say that the calling task is skipped."""
    if program_path(language):
        return True
    variable = PROGRAMS[language][0]
    print(f"{env.Dir('.').name}: skipped, {LANGUAGES[language]} not found (set {variable} in .env to run it)")
    return False


env.AddMethod(register, "Register")
env.AddMethod(own_output, "Out")
env.AddMethod(upstream, "Upstream")
env.AddMethod(raw_data, "Data")
env.AddMethod(check_program, "CheckProgram")

# One SConscript per task, in folder-name order.
SConscript(sorted(Glob("tasks/*/SConscript"), key=str), exports="env")

Default(env.Alias("build_all", default_targets))
