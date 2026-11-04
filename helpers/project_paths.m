function paths = project_paths()
%PROJECT_PATHS Project folders for a Matlab script in tasks/<task>/scripts/, which must be the working directory.
%   SCons sets it; in the Matlab desktop, choose "Change Folder" when Matlab asks, or cd to the script's folder.
%
%   Usage, at the top of a script:
%       addpath(fullfile(pwd, "..", "..", "..", "helpers"));
%       paths = project_paths();
%
%   paths.task_output_dir    OUTPUT_ROOT/tasks/<task>/, this task's output folder (created)
%   paths.task_output_root   OUTPUT_ROOT/tasks/, to read other tasks' outputs
%   paths.data_root          the raw data folder ("" if not set)
%   Settings come from environment variables when set, otherwise from .env in the repo root (see .env.example).

scripts = string(pwd);
[task_dir, folder] = fileparts(scripts);
root = fileparts(fileparts(task_dir));
if folder ~= "scripts" || ~isfile(fullfile(root, "SConstruct"))
    error("Working directory is %s. Change it to the script's folder (tasks/<task>/scripts/) first.", scripts);
end

settings = read_env(fullfile(root, ".env"));
output_root = setting("OUTPUT_ROOT", settings, root);
if output_root == ""
    error("OUTPUT_ROOT not set. Add it to %s (see .env.example).", fullfile(root, ".env"));
end

[~, task] = fileparts(task_dir);
paths.task_output_root = fullfile(output_root, "tasks");
paths.task_output_dir = fullfile(paths.task_output_root, task);
paths.data_root = setting("DATA_ROOT", settings, root);
if ~isfolder(paths.task_output_dir)
    mkdir(paths.task_output_dir);
end
end


function settings = read_env(path)
% Read .env: lines NAME=value; # starts a comment; quotes around the value are dropped.
settings = containers.Map('KeyType', 'char', 'ValueType', 'char');
if ~isfile(path)
    return
end
for line = strtrim(splitlines(string(fileread(path))))'
    if line == "" || startsWith(line, "#") || ~contains(line, "=")
        continue
    end
    value = strip(strip(strtrim(extractAfter(line, "=")), '"'), "'");
    settings(char(strtrim(extractBefore(line, "=")))) = char(value);
end
end


function value = setting(name, settings, root)
% An environment variable wins over .env. `~` is the home folder; relative paths start at the repo root.
value = string(getenv(name));
if value == "" && isKey(settings, name)
    value = string(settings(name));
end
if value == ""
    return
end
if startsWith(value, "~")
    home = string(getenv("USERPROFILE"));
    if home == ""
        home = string(getenv("HOME"));
    end
    value = home + extractAfter(value, 1);
end
if isempty(regexp(value, '^([A-Za-z]:)?[\\/]', 'once'))
    value = fullfile(root, value);
end
end
