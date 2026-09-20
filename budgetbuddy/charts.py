"""Saves charts as png files with matplotlib."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")   # no window needed, we only save files
import matplotlib.pyplot as plt


def category_chart(spent, budgets, month, out_dir="output"):
    """Bar chart: spent per category, with a marker for the budget."""
    Path(out_dir).mkdir(exist_ok=True)
    categories = list(spent.index)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(categories, list(spent.values), color="#4c9f70", label="Spent")
    for i, cat in enumerate(categories):
        if cat in budgets:
            ax.hlines(budgets[cat], i - 0.4, i + 0.4, colors="red", linestyles="--")
    ax.set_title(f"Spending by category - {month}  (red line = budget)")
    ax.set_ylabel("Amount (Rs)")
    plt.xticks(rotation=30)
    fig.tight_layout()
    path = Path(out_dir) / f"categories_{month}.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def trend_chart(monthly, out_dir="output"):
    """Line chart of total spending per month."""
    Path(out_dir).mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(list(monthly.index), list(monthly.values), marker="o", color="#2a6fdb")
    ax.set_title("Monthly spending trend")
    ax.set_ylabel("Total (Rs)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = Path(out_dir) / "monthly_trend.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
