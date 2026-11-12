"""生成趋势图表（英文标签，避免环境缺中文字体导致乱码）。"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import storage

REPORT_PATH = storage.DATA_DIR / "report.png"


def render(events: list[dict]) -> Path | None:
    if not events:
        return None

    dates = [e["date"] for e in events]
    mood_self = [e["mood_self"] for e in events]
    mood_other = [e["mood_other"] for e in events]

    counts: dict[str, int] = {}
    for e in events:
        counts[e["interaction"]] = counts.get(e["interaction"], 0) + 1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    ax1.plot(dates, mood_self, marker="o", label="Your mood", color="#3b82f6")
    ax1.plot(dates, mood_other, marker="o", label="Observed other mood", color="#f59e0b")
    ax1.axhline(0, color="#999", linewidth=0.8, linestyle="--")
    ax1.set_ylim(-2.5, 2.5)
    ax1.set_title("Mood trend")
    ax1.set_ylabel("-2 ~ 2")
    ax1.legend()
    ax1.tick_params(axis="x", rotation=45)

    ax2.bar(list(counts.keys()), list(counts.values()), color="#10b981")
    ax2.set_title("Interaction types")
    ax2.set_ylabel("count")

    fig.tight_layout()
    fig.savefig(REPORT_PATH, dpi=120)
    plt.close(fig)
    return REPORT_PATH
