* Demo Stata task: production function by OLS, then yearly means of the toy panel.
* Run it through SCons (`python -m SCons example_stata`), which sets TASK_OUTPUT_ROOT and TASK_OUTPUT_DIR.
version 18
clear all
set more off

local upstream : env TASK_OUTPUT_ROOT
local out : env TASK_OUTPUT_DIR
if "`upstream'" == "" | "`out'" == "" {
    display as error "TASK_OUTPUT_ROOT / TASK_OUTPUT_DIR not set: run this do-file through SCons."
    exit 198
}

import delimited using "`upstream'/01_example_clean/panel.csv", clear
regress log_output log_capital log_labor, vce(cluster firm_id)

collapse (mean) output capital labor, by(year)
export delimited using "`out'/means_by_year.csv", replace
