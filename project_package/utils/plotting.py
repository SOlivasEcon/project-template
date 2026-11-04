"""Figure helpers, so every task saves figures the same way."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def save_figure(fig: Figure, path: Path, dpi: int = 200) -> None:
    """Save `fig` to `path` with a tight bounding box and a fixed resolution, then close it.

    The matplotlib version stamp is left out of the file, so upgrading matplotlib alone does not change it.
    """
    fig.savefig(path, dpi=dpi, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
