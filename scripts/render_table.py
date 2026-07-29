#!/usr/bin/env python3
"""Render tabular markdown data as a styled table PNG for embedding in PPT."""

import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Find CJK-capable font
_CJK_FONT = None
for f in fm.fontManager.ttflist:
    name_lower = f.name.lower()
    if 'pingfang sc' in name_lower or 'heiti sc' in name_lower:
        _CJK_FONT = f.name
        break
if _CJK_FONT:
    plt.rcParams["font.sans-serif"] = [_CJK_FONT, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def parse_table_data(data_str):
    """Parse 'Model|IoU|FPS\nA|0.97|30\nB|0.94|45' into headers and rows."""
    lines = [line.strip() for line in data_str.strip().split("\n") if line.strip()]
    if not lines:
        return [], []
    headers = [h.strip() for h in lines[0].split("|")]
    rows = []
    for line in lines[1:]:
        cells = [c.strip() for c in line.split("|")]
        rows.append(cells)
    return headers, rows


def render_table(headers, rows, output, title=""):
    ncols = len(headers)
    nrows = len(rows) + 1
    fig, ax = plt.subplots(figsize=(max(4, ncols * 1.8), max(1.5, nrows * 0.5)))
    ax.axis("off")

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)

    data_matrix = [headers] + [row[:ncols] + [""] * (ncols - len(row)) for row in rows]
    table = ax.table(
        cellText=data_matrix,
        loc="center",
        cellLoc="center",
        colWidths=[0.2] * ncols,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)

    for j in range(ncols):
        cell = table[0, j]
        cell.set_facecolor("#4472C4")
        cell.set_text_props(color="white", fontweight="bold")
        cell.set_edgecolor("white")

    for i in range(1, nrows):
        for j in range(ncols):
            cell = table[i, j]
            cell.set_facecolor("#F2F2F2" if i % 2 == 0 else "white")
            cell.set_edgecolor("#D9D9D9")

    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"Table saved: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render markdown table as image")
    parser.add_argument("--data", required=True, help="Markdown table data")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--title", default="", help="Table title")
    args = parser.parse_args()
    headers, rows = parse_table_data(args.data)
    render_table(headers, rows, args.output, args.title)
