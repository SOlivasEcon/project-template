"""Simulate the toy raw data: a firm-year panel from a Cobb-Douglas production function, with a few bad rows.

Stands in for raw data that a real project reads from DATA_ROOT (see `project_package.paths.data_dir`).
"""

import numpy as np
import pandas as pd

from project_package.paths import output_dir

N_FIRMS = 50
YEARS = range(2010, 2025)
SEED = 20261104


def simulate(rng: np.random.Generator) -> pd.DataFrame:
    """Return the panel; output = exp(firm effect) * capital^0.35 * labor^0.6 * noise."""
    firm = np.repeat(np.arange(1, N_FIRMS + 1), len(YEARS))
    year = np.tile(np.array(YEARS), N_FIRMS)
    firm_effect = rng.normal(0, 0.5, N_FIRMS)[firm - 1]
    capital = np.exp(rng.normal(3, 0.8, firm.size))
    labor = np.exp(rng.normal(2, 0.6, firm.size))
    noise = rng.normal(0, 0.2, firm.size)
    output = np.exp(1 + firm_effect + 0.35 * np.log(capital) + 0.6 * np.log(labor) + noise)
    df = pd.DataFrame({"firm_id": firm, "year": year, "output": output, "capital": capital, "labor": labor})

    # Bad rows for the clean task to drop: missing capital and zero output.
    bad = rng.choice(len(df), 20, replace=False)
    df.loc[bad[:10], "capital"] = np.nan
    df.loc[bad[10:], "output"] = 0.0
    return df


def main() -> None:
    df = simulate(np.random.default_rng(SEED))
    path = output_dir(__file__) / "raw_panel.csv"
    df.to_csv(path, index=False, float_format="%.6f")
    print(f"Wrote {len(df)} rows to {path}")


if __name__ == "__main__":
    main()
