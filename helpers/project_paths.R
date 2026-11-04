# Project folders for an R script in tasks/<task>/scripts/, which must be the working directory. SCons sets it;
# in RStudio use Session > Set Working Directory > To Source File Location.
#
# Usage, at the top of a script:
#   source("../../../helpers/project_paths.R")
#   paths <- project_paths()
#
# paths$task_output_dir    OUTPUT_ROOT/tasks/<task>/, this task's output folder (created)
# paths$task_output_root   OUTPUT_ROOT/tasks/, to read other tasks' outputs
# paths$data_root          the raw data folder (NA if not set)
# Settings come from environment variables when set, otherwise from .env in the repo root (see .env.example).

project_paths <- function() {
  scripts <- normalizePath(getwd(), winslash = "/")
  task_dir <- dirname(scripts)
  root <- dirname(dirname(task_dir))
  if (basename(scripts) != "scripts" || !file.exists(file.path(root, "SConstruct"))) {
    stop("Working directory is ", scripts, ". Change it to the script's folder (tasks/<task>/scripts/) first.")
  }

  settings <- read_env(file.path(root, ".env"))
  setting <- function(name) {
    value <- Sys.getenv(name)  # an environment variable wins over .env
    if (!nzchar(value) && name %in% names(settings)) value <- settings[[name]]
    resolve_path(value, root)
  }
  output_root <- setting("OUTPUT_ROOT")
  if (is.na(output_root)) stop("OUTPUT_ROOT not set. Add it to ", file.path(root, ".env"), " (see .env.example).")

  task_output_root <- file.path(output_root, "tasks")
  task_output_dir <- file.path(task_output_root, basename(task_dir))
  dir.create(task_output_dir, recursive = TRUE, showWarnings = FALSE)
  list(task_output_dir = task_output_dir, task_output_root = task_output_root, data_root = setting("DATA_ROOT"))
}

# Read .env: lines NAME=value; # starts a comment; quotes around the value are dropped.
read_env <- function(path) {
  if (!file.exists(path)) return(character())
  lines <- trimws(readLines(path, warn = FALSE))
  lines <- lines[grepl("=", lines) & !startsWith(lines, "#")]
  values <- gsub("^[\"']|[\"']$", "", trimws(sub("^[^=]*=", "", lines)))
  setNames(values, trimws(sub("=.*", "", lines)))
}

# `~` is the home folder; relative paths start at the repo root. Returns NA for an empty value.
resolve_path <- function(value, root) {
  if (!nzchar(value)) return(NA_character_)
  value <- gsub("\\\\", "/", value)
  if (startsWith(value, "~")) {
    home <- Sys.getenv(if (.Platform$OS.type == "windows") "USERPROFILE" else "HOME")
    value <- paste0(gsub("\\\\", "/", home), substring(value, 2))
  }
  if (!grepl("^([A-Za-z]:)?/", value)) value <- file.path(root, value)
  value
}
