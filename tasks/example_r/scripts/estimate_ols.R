# Demo R task: production function by OLS, with base R only.
# Run it through SCons (`python -m SCons example_r`), which sets TASK_OUTPUT_ROOT and TASK_OUTPUT_DIR.

upstream <- Sys.getenv("TASK_OUTPUT_ROOT")
out <- Sys.getenv("TASK_OUTPUT_DIR")
if (!nzchar(upstream) || !nzchar(out)) {
  stop("TASK_OUTPUT_ROOT / TASK_OUTPUT_DIR not set: run this script through SCons.")
}

panel <- read.csv(file.path(upstream, "01_example_clean", "panel.csv"))
fit <- lm(log_output ~ log_capital + log_labor, data = panel)
print(summary(fit))

coefficients <- data.frame(term = names(coef(fit)), estimate = unname(coef(fit)))
write.csv(coefficients, file.path(out, "coefficients.csv"), row.names = FALSE)
