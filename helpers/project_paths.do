* Project folders for a do-file in tasks/<task>/scripts/, which must be the working directory. SCons sets it;
* interactively, open Stata by double-clicking the do-file, or `cd` to the do-file's folder first.
*
* Usage, at the top of a do-file:
*     run "../../../helpers/project_paths.do"
*
* Sets these globals (with forward slashes, which Stata accepts on every system):
*     $TASK_OUTPUT_DIR    OUTPUT_ROOT/tasks/<task>, this task's output folder (created)
*     $TASK_OUTPUT_ROOT   OUTPUT_ROOT/tasks, to read other tasks' outputs
*     $DATA_ROOT          the raw data folder (empty if not set)
* Settings come from environment variables when set, otherwise from .env in the repo root (see .env.example).

local scripts = subinstr("`c(pwd)'", "\", "/", .)
mata: st_local("folder", pathbasename(st_local("scripts")))
mata: st_local("task_dir", pathgetparent(st_local("scripts")))
mata: st_local("task", pathbasename(st_local("task_dir")))
mata: st_local("root", pathgetparent(pathgetparent(st_local("task_dir"))))
capture confirm file "`root'/SConstruct"
if _rc | "`folder'" != "scripts" {
    display as error "Working directory is `scripts'."
    display as error "Change it to the do-file's folder (tasks/<task>/scripts/) first."
    exit 601
}

* Read OUTPUT_ROOT and DATA_ROOT from .env: lines NAME=value; # starts a comment.
local env_OUTPUT_ROOT ""
local env_DATA_ROOT ""
capture confirm file "`root'/.env"
if !_rc {
    tempname fh
    file open `fh' using "`root'/.env", read text
    file read `fh' line
    while !r(eof) {
        local line = strtrim(`"`macval(line)'"')
        local eq = strpos(`"`macval(line)'"', "=")
        if `eq' > 1 & substr(`"`macval(line)'"', 1, 1) != "#" {
            local key = strtrim(substr(`"`macval(line)'"', 1, `eq' - 1))
            local value = strtrim(substr(`"`macval(line)'"', `eq' + 1, .))
            if inlist(substr(`"`macval(value)'"', 1, 1), char(34), char(39)) {
                local value = substr(`"`macval(value)'"', 2, strlen(`"`macval(value)'"') - 2)
            }
            if inlist("`key'", "OUTPUT_ROOT", "DATA_ROOT") local env_`key' `"`macval(value)'"'
        }
        file read `fh' line
    }
    file close `fh'
}

* An environment variable wins over .env. `~` is the home folder; relative paths start at the repo root.
foreach name in OUTPUT_ROOT DATA_ROOT {
    local value : env `name'
    if `"`value'"' == "" local value `"`env_`name''"'
    local value = subinstr(`"`value'"', "\", "/", .)
    if substr(`"`value'"', 1, 1) == "~" {
        local home : env USERPROFILE
        if "`home'" == "" local home : env HOME
        local value = subinstr("`home'", "\", "/", .) + substr(`"`value'"', 2, .)
    }
    if `"`value'"' != "" {
        mata: st_local("absolute", strofreal(pathisabs(st_local("value"))))
        if !`absolute' local value "`root'/`value'"
    }
    local `name' `"`value'"'
}
if `"`OUTPUT_ROOT'"' == "" {
    display as error "OUTPUT_ROOT not set. Add it to `root'/.env (see .env.example)."
    exit 198
}

global TASK_OUTPUT_ROOT "`OUTPUT_ROOT'/tasks"
global TASK_OUTPUT_DIR "$TASK_OUTPUT_ROOT/`task'"
global DATA_ROOT "`DATA_ROOT'"
capture mkdir "`OUTPUT_ROOT'"
capture mkdir "$TASK_OUTPUT_ROOT"
capture mkdir "$TASK_OUTPUT_DIR"
