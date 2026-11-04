% Demo Matlab task: production function by OLS, without toolboxes.
% Runs through SCons or on its own, with this folder as the working directory (see helpers/README.md).
addpath(fullfile(pwd, "..", "..", "..", "helpers"));
paths = project_paths();

panel = readtable(fullfile(paths.task_output_root, "01_example_clean", "panel.csv"));
X = [ones(height(panel), 1), panel.log_capital, panel.log_labor];
beta = X \ panel.log_output;

coefficients = table(["const"; "log_capital"; "log_labor"], beta, 'VariableNames', {'term', 'estimate'});
disp(coefficients)
writetable(coefficients, fullfile(paths.task_output_dir, "coefficients.csv"));
