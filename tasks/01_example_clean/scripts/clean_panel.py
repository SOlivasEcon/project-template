"""Clean the toy panel: drop rows with missing or non-positive values and add the logs used in estimation."""

import numpy as np
import pandas as pd

from project_package.paths import output_dir, upstream_output

VARIABLES = ["output", "capital", "labor"]


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Keep rows where every variable is present and positive; add log_<variable> columns."""
    keep = raw[VARIABLES].notna().all(axis=1) & (raw[VARIABLES] > 0).all(axis=1)
    df = raw.loc[keep].copy()
    for var in VARIABLES:
        df[f"log_{var}"] = np.log(df[var])
    return df


def main() -> None:
    raw = pd.read_csv(upstream_output("00_example_raw") / "raw_panel.csv")
    df = clean(raw)
    path = output_dir(__file__) / "panel.csv"
    df.to_csv(path, index=False, float_format="%.6f")
    print(f"Kept {len(df)} of {len(raw)} rows; wrote {path}")


if __name__ == "__main__":
    main()
