# Project folders for a Julia script in tasks/<task>/scripts/.
#
# Usage, at the top of a script (works from any working directory):
#   include(joinpath(@__DIR__, "..", "..", "..", "helpers", "project_paths.jl"))
#   paths = project_paths(@__DIR__)
#
# paths.task_output_dir    OUTPUT_ROOT/tasks/<task>/, this task's output folder (created)
# paths.task_output_root   OUTPUT_ROOT/tasks/, to read other tasks' outputs
# paths.data_root          the raw data folder ("" if not set)
# Settings come from environment variables when set, otherwise from .env in the repo root (see .env.example).

function project_paths(script_dir::AbstractString)
    scripts = normpath(abspath(script_dir))
    scripts = rstrip(scripts, ['/', '\\'])
    task_dir = dirname(scripts)
    root = dirname(dirname(task_dir))
    if basename(scripts) != "scripts" || !isfile(joinpath(root, "SConstruct"))
        error("$scripts is not a tasks/<task>/scripts/ folder; pass @__DIR__ from a task script.")
    end

    settings = read_env(joinpath(root, ".env"))
    setting(name) = resolve_path(get(ENV, name, "") == "" ? get(settings, name, "") : ENV[name], root)
    output_root = setting("OUTPUT_ROOT")
    isempty(output_root) && error("OUTPUT_ROOT not set. Add it to $(joinpath(root, ".env")) (see .env.example).")

    task_output_root = joinpath(output_root, "tasks")
    task_output_dir = joinpath(task_output_root, basename(task_dir))
    mkpath(task_output_dir)
    return (task_output_dir=task_output_dir, task_output_root=task_output_root, data_root=setting("DATA_ROOT"))
end

# Read .env: lines NAME=value; # starts a comment; quotes around the value are dropped.
function read_env(path::AbstractString)
    settings = Dict{String,String}()
    isfile(path) || return settings
    for line in strip.(readlines(path))
        (isempty(line) || startswith(line, "#") || !occursin('=', line)) && continue
        key, value = strip.(split(line, '='; limit=2))
        settings[key] = strip(value, ['"', '\''])
    end
    return settings
end

# `~` is the home folder; relative paths start at the repo root. Returns "" for an empty value.
function resolve_path(value::AbstractString, root::AbstractString)
    isempty(value) && return ""
    value = expanduser(value)
    return isabspath(value) ? value : joinpath(root, value)
end
