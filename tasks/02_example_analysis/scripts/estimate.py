"""Estimate the toy production function and write a LaTeX table and a figure for the paper."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from project_package.paths import output_dir, upstream_output
from project_package.utils.plotting import save_figure

SPECIFICATIONS = {
    "Pooled OLS": "log_output ~ log_capital + log_labor",
    "Firm fixed effects": "log_output ~ log_capital + log_labor + C(firm_id)",
}
ROWS = {"log_capital": "Log capital", "log_labor": "Log labor"}


def estimate(df: pd.DataFrame) -> dict:
    """Fit each specification with standard errors clustered by firm."""
    return {
        name: smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df["firm_id"]})
        for name, formula in SPECIFICATIONS.items()
    }


def latex_table(results: dict) -> str:
    """Return a booktabs tabular: coefficients with standard errors below, then fixed effects, N and R^2."""
    n = len(results)
    lines = [rf"\begin{{tabular}}{{l{'c' * n}}}", r"\toprule"]
    lines.append(" & " + " & ".join(f"({i})" for i in range(1, n + 1)) + r" \\")
    lines.append(r"\midrule")
    for var, label in ROWS.items():
        lines.append(label + " & " + " & ".join(f"{r.params[var]:.3f}" for r in results.values()) + r" \\")
        lines.append(" & " + " & ".join(f"({r.bse[var]:.3f})" for r in results.values()) + r" \\")
    lines.append(r"\midrule")
    fixed_effects = ["Yes" if "C(firm_id)" in r.model.formula else "No" for r in results.values()]
    lines.append("Firm fixed effects & " + " & ".join(fixed_effects) + r" \\")
    lines.append("Observations & " + " & ".join(f"{int(r.nobs):,}" for r in results.values()) + r" \\")
    lines.append("$R^2$ & " + " & ".join(f"{r.rsquared:.3f}" for r in results.values()) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    return "\n".join(lines)


def scatter(df: pd.DataFrame):
    """Log output against log labor, with the OLS line."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.scatter(df["log_labor"], df["log_output"], s=8, alpha=0.5)
    slope, intercept = np.polyfit(df["log_labor"], df["log_output"], 1)
    x = np.linspace(df["log_labor"].min(), df["log_labor"].max(), 50)
    ax.plot(x, intercept + slope * x, color="black", linewidth=1)
    ax.set_xlabel("Log labor")
    ax.set_ylabel("Log output")
    return fig


def main() -> None:
    df = pd.read_csv(upstream_output("01_example_clean") / "panel.csv")
    results = estimate(df)
    for name, r in results.items():
        print(f"{name}: " + ", ".join(f"{v} = {r.params[v]:.3f} ({r.bse[v]:.3f})" for v in ROWS))

    out = output_dir(__file__)
    (out / "table_production.tex").write_text(latex_table(results), encoding="utf-8", newline="\n")
    save_figure(scatter(df), out / "fig_output_labor.png")


if __name__ == "__main__":
    main()
