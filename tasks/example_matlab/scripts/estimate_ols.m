% Demo Matlab task: production function by OLS, without toolboxes.
% Run it through SCons (`python -m SCons example_matlab`), which sets TASK_OUTPUT_ROOT and TASK_OUTPUT_DIR.

upstream = getenv("TASK_OUTPUT_ROOT");
out = getenv("TASK_OUTPUT_DIR");
if isempty(upstream) || isempty(out)
    error("TASK_OUTPUT_ROOT / TASK_OUTPUT_DIR not set: run this script through SCons.");
end

panel = readtable(fullfile(upstream, "01_example_clean", "panel.csv"));
X = [ones(height(panel), 1), panel.log_capital, panel.log_labor];
beta = X \ panel.log_output;

coefficients = table(["const"; "log_capital"; "log_labor"], beta, 'VariableNames', {'term', 'estimate'});
disp(coefficients)
writetable(coefficients, fullfile(out, "coefficients.csv"));
