# Demo R task: production function by OLS, with base R only.
# Runs through SCons or on its own, with this folder as the working directory (see helpers/README.md).
source("../../../helpers/project_paths.R")
paths <- project_paths()

panel <- read.csv(file.path(paths$task_output_root, "01_example_clean", "panel.csv"))
fit <- lm(log_output ~ log_capital + log_labor, data = panel)
print(summary(fit))

coefficients <- data.frame(term = names(coef(fit)), estimate = unname(coef(fit)))
write.csv(coefficients, file.path(paths$task_output_dir, "coefficients.csv"), row.names = FALSE)
