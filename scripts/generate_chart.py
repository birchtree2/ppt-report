#!/usr/bin/env python3
"""Generate matplotlib charts for PPT embedding."""

import argparse, re, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Use Microsoft YaHei for CJK (matches original PPT font strategy)
_CJK_FONTS = [f.name for f in fm.fontManager.ttflist
              if 'yahei' in f.name.lower() or 'microsoft ya' in f.name.lower()
              or 'pingfang sc' in f.name.lower() or 'heiti sc' in f.name.lower()]
if _CJK_FONTS:
    plt.rcParams["font.sans-serif"] = [_CJK_FONTS[0], "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

COLORS = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5", "#70AD47", "#264478", "#9B57A0"]


def parse_kv(s):
    items = [x.strip() for x in s.split(",")]
    labels, values = [], []
    for item in items:
        if ":" in item:
            k, v = item.split(":", 1)
            labels.append(k.strip())
            values.append(float(v.strip()))
    return labels, values


def bar_chart(labels, values, title, output, color=COLORS[0]):
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=color, width=0.5, edgecolor="white", linewidth=0.5)
    ax.set_ylim(0, 1.05 * max(values) if max(values) < 1 else 1.1 * max(values))
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f"{val:.3f}" if val < 1 else f"{val:.1f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=11)
    ax.tick_params(axis="y", labelsize=10)
    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)


def line_chart(labels, values, title, output):
    fig, ax = plt.subplots(figsize=(6, 3.5))
    x = np.arange(len(labels))
    ax.plot(x, values, color=COLORS[0], marker="o", linewidth=2, markersize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_ylim(min(values) * 0.95, max(values) * 1.05)
    for i, val in enumerate(values):
        ax.annotate(f"{val:.3f}" if val < 1 else f"{val:.1f}",
                    (x[i], val), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=10, fontweight="bold", color=COLORS[0])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["bar", "line"], default="bar")
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="")
    args = parser.parse_args()
    labels, values = parse_kv(args.data)
    if args.type == "bar":
        bar_chart(labels, values, args.title, args.output)
    else:
        line_chart(labels, values, args.title, args.output)
