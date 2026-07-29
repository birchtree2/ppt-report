#!/usr/bin/env python3
"""Render markdown table data as a styled PNG for PPT embedding.
Cross-platform CJK font detection included."""

import argparse, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Auto-detect CJK font
_CJK = None
for f in fm.fontManager.ttflist:
    name = f.name.lower()
    if any(k in name for k in ["yahei", "pingfang sc", "heiti sc", "noto sans cjk",
                                "source han sans sc", "wqy", "simsun"]):
        _CJK = f.name
        break
if _CJK:
    plt.rcParams["font.sans-serif"] = [_CJK, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def parse_table(data_str):
    lines = [l.strip() for l in data_str.strip().split("\n") if l.strip()]
    if not lines:
        return [], []
    headers = [h.strip() for h in lines[0].split("|")]
    rows = []
    for line in lines[1:]:
        cells = [c.strip() for c in line.split("|")]
        rows.append(cells)
    return headers, rows


def render(headers, rows, output, title=""):
    ncols, nrows = len(headers), len(rows) + 1
    fig, ax = plt.subplots(figsize=(max(4, ncols * 1.8), max(1.5, nrows * 0.5)))
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    data = [headers] + [row[:ncols] + [""] * (ncols - len(row)) for row in rows]
    table = ax.table(cellText=data, loc="center", cellLoc="center", colWidths=[0.2] * ncols)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)
    for j in range(ncols):
        c = table[0, j]
        c.set_facecolor("#4472C4")
        c.set_text_props(color="white", fontweight="bold")
        c.set_edgecolor("white")
    for i in range(1, nrows):
        for j in range(ncols):
            c = table[i, j]
            c.set_facecolor("#F2F2F2" if i % 2 == 0 else "white")
            c.set_edgecolor("#D9D9D9")
    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"Table saved: {output}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    h, r = parse_table(a.data)
    render(h, r, a.output, a.title)
