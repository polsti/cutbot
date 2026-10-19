"""Weight-over-time chart rendered to PNG bytes (no files on disk)."""

import io
from datetime import datetime

import matplotlib

matplotlib.use("Agg")  # no screen on the server
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

LINE = "#2563eb"
TARGET = "#16a34a"
GRID = "#e5e7eb"
TEXT = "#374151"


def render_weight_chart(
    dates: list[datetime], weights: list[float], target_kg: float | None, weight_label: str, target_label: str, unit_label: str = "kg",
) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)

    ax.plot(dates, weights, color=LINE, linewidth=2.2, marker="o", markersize=5, label=weight_label)
    ax.annotate(
        f"{weights[-1]:g}", (dates[-1], weights[-1]), textcoords="offset points", xytext=(0, 9),
        ha="center", fontsize=10, fontweight="bold", color=LINE,
    )
    if target_kg is not None:
        ax.axhline(target_kg, color=TARGET, linestyle="--", linewidth=1.5, label=f"{target_label}: {target_kg:g}")

    # Keep the target visible and leave a little air above/below the line.
    values = weights + ([target_kg] if target_kg is not None else [])
    pad = max((max(values) - min(values)) * 0.15, 0.5)
    ax.set_ylim(min(values) - pad, max(values) + pad)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=8))
    ax.set_ylabel(unit_label, color=TEXT)
    ax.grid(axis="y", color=GRID)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=TEXT)
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    return buffer.getvalue()
