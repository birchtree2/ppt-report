#!/usr/bin/env python3
"""Generate matplotlib charts (bar/line) as PNG for PPT embedding.
Auto-detects available CJK fonts for cross-platform compatibility."""

import argparse, re, os, sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Auto-detect CJK font (portable across devices)
_CJK = None
for f in fm.fontManager.ttflist:
    name = f.name.lower()
    if any(k in name for k in ["yahei", "pingfang sc", "heiti sc", "noto sans cjk",
                                "source han sans sc", "wqy", "simsun", "microsoft yahei"]):
        _CJK = f.name
        break
if _CJK:
    plt.rcParams["font.sans-serif"] = [_CJK, "DejaVu Sans"]
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


def bar_chart(labels, values, title, output):
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=COLORS[0], width=0.5, edgecolor="white", linewidth=0.5)
    ymax = max(values)
    ax.set_ylim(0, ymax * 1.08 if ymax < 1 else ymax * 1.12)
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + ymax * 0.01,
                f"{val:.3f}" if val < 1 else f"{val:.1f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=11)
    ax.tick_params(axis="y", labelsize=10)
    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {output}")


def line_chart(labels, values, title, output):
    fig, ax = plt.subplots(figsize=(6, 3.5))
    x = np.arange(len(labels))
    ax.plot(x, values, color=COLORS[0], marker="o", linewidth=2, markersize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    margin = (max(values) - min(values)) * 0.1 or 0.05
    ax.set_ylim(min(values) - margin, max(values) + margin)
    for i, val in enumerate(values):
        ax.annotate(f"{val:.3f}" if val < 1 else f"{val:.1f}",
                    (x[i], val), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=10, fontweight="bold", color=COLORS[0])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {output}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["bar", "line"], default="bar")
    ap.add_argument("--data", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    labels, values = parse_kv(a.data)
    (bar_chart if a.type == "bar" else line_chart)(labels, values, a.title, a.output)
