"""Root build file: `python -m SCons` (or `pixi run build`) runs every task in dependency order.

    python -m SCons                    # build everything registered (a second run does nothing)
    python -m SCons -j 4               # build in parallel
    python -m SCons 01_example_clean   # build one task (and what it depends on)
    python -m SCons -c                 # delete all task outputs and logs

Each task folder tasks/<task>/ has an SConscript that declares which files its scripts read and write.
SCons uses those declarations to decide what to rerun after a script or an input changes.

A builder runs one script with the script's own folder as the working directory and writes everything it
prints to tasks/<task>/logs/<script>.log, which is a target too (so `-c` removes it).

Layout and SCons design inspired by shihhsuanhsu/project-template
(https://github.com/shihhsuanhsu/project-template).
"""

import os
import subprocess
import sys

from SCons.Script import Action, Builder, Default, Environment, Glob, SConscript

from project_package.config import required_path
from project_package.paths import task_output_dir

# Files of the shared package that every script imports; each script's build depends on them.
SHARED_SOURCES = ["#/project_package/__init__.py", "#/project_package/config.py", "#/project_package/paths.py"]


def log_node(script):
    """Return the node for tasks/<task>/logs/<script>.log, given the node of tasks/<task>/scripts/<script>."""
    return script.dir.up().Dir("logs").File(os.path.splitext(script.name)[0] + ".log")


def run_logged(command, script, log):
    """Run `command` from the script's folder, writing its output to `log`; return the exit code.

    On failure, prints the end of the log so the error shows in the terminal.
    """
    os.makedirs(os.path.dirname(log), exist_ok=True)
    child_env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8"}
    with open(log, "w", encoding="utf-8") as f:
        code = subprocess.run(
            command, check=False, cwd=os.path.dirname(script), env=child_env, stdout=f, stderr=subprocess.STDOUT
        ).returncode
    if code:
        print(f"*** {script} failed (exit code {code}). Last lines of {log}:")
        with open(log, encoding="utf-8", errors="replace") as f:
            print("".join(f.readlines()[-15:]))
    return code


def run_python(target, source, env):
    """Run the first source (a .py file) with the Python running SCons. Further sources only declare inputs."""
    script = source[0]
    return run_logged([sys.executable, script.name], script.abspath, log_node(script).abspath)


def add_log_and_shared(target, source, env):
    """Add the script's log as a target and the shared package files as sources."""
    return list(target) + [log_node(source[0])], list(source) + [env.File(s) for s in SHARED_SOURCES]


# tools=[]: no compiler detection, which is slow on Windows and not needed here.
env = Environment(ENV=os.environ, tools=[])
# Hash a file only when its timestamp changed; avoids re-hashing large raw files on every build.
env.Decider("MD5-timestamp")
env.Append(BUILDERS={
    "Python": Builder(action=Action(run_python, "python $SOURCE"), emitter=add_log_and_shared),
})

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


env.AddMethod(register, "Register")
env.AddMethod(own_output, "Out")
env.AddMethod(upstream, "Upstream")
env.AddMethod(raw_data, "Data")

# One SConscript per task, in folder-name order.
SConscript(sorted(Glob("tasks/*/SConscript"), key=str), exports="env")

Default(env.Alias("build_all", default_targets))
