* Demo Stata task: production function by OLS, then yearly means of the toy panel.
* Runs through SCons or on its own, with this folder as the working directory (see helpers/README.md).
version 18
clear all
set more off
run "../../../helpers/project_paths.do"

import delimited using "$TASK_OUTPUT_ROOT/01_example_clean/panel.csv", clear
regress log_output log_capital log_labor, vce(cluster firm_id)

collapse (mean) output capital labor, by(year)
export delimited using "$TASK_OUTPUT_DIR/means_by_year.csv", replace
