#!/usr/bin/env python3
"""Render data/contributions.json into an animated contrib-heatmap.svg.

Rounded boxes slide down diagonally on load, then freeze (no looping).
No JS, no inline <style> stripped by GitHub's README sanitizer — the
animation lives entirely inside this SVG file, referenced via <img>.
"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "contributions.json"
OUT_PATH = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none      ->                                          brightest (level 5: neon top end, best day only)

BG = "#0d1117"
BORDER = "#30363d"
TEXT_MUTED = "#8b949e"
TEXT_BRIGHT = "#c9d1d9"
GREEN = "#39d353"

CELL = 11
GAP = 3
PITCH = CELL + GAP
LEFT_LABEL_W = 28
TOP_LABEL_H = 20
PAD = 16
LEGEND_H = 20
FOOTER_H = 24

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOW_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # row index, Sunday = row 0


def build_weeks(days):
    first = date.fromisoformat(days[0]["date"])
    pad = (first.weekday() + 1) % 7  # Sunday = 0
    cells = [None] * pad + days

    weeks = []
    week = []
    for cell in cells:
        week.append(cell)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        week += [None] * (7 - len(week))
        weeks.append(week)
    return weeks


def month_labels(weeks):
    labels = []
    seen_month = None
    for col, week in enumerate(weeks):
        for cell in week:
            if cell is None:
                continue
            d = date.fromisoformat(cell["date"])
            if d.day <= 7 and d.month != seen_month:
                labels.append((col, MONTH_NAMES[d.month - 1]))
                seen_month = d.month
            break
    return labels


def main():
    payload = json.loads(DATA_PATH.read_text())
    days = payload["days"]
    stats = payload["stats"]
    best_date = stats["best_day"]["date"] if stats["best_day"] else None

    weeks = build_weeks(days)
    n_cols = len(weeks)

    grid_w = n_cols * PITCH - GAP
    grid_h = 7 * PITCH - GAP
    width = LEFT_LABEL_W + grid_w + PAD * 2
    height = PAD + TOP_LABEL_H + grid_h + LEGEND_H + FOOTER_H + PAD

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Menlo, Consolas, \'SF Mono\', monospace">'
    )
    parts.append(f"""
  <style>
    .card {{ fill: {BG}; stroke: {BORDER}; stroke-width: 1; }}
    .dow, .month {{ fill: {TEXT_MUTED}; font-size: 10px; }}
    .footer {{ fill: {TEXT_BRIGHT}; font-size: 11px; }}
    .footer-dim {{ fill: {TEXT_MUTED}; font-size: 11px; }}
    .day {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      animation: reveal 0.5s ease-out forwards;
    }}
    @keyframes reveal {{
      0%   {{ opacity: 0; transform: translateY(-8px); }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
""")

    parts.append(f'<rect class="card" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="6"/>')

    grid_x = LEFT_LABEL_W + PAD
    grid_y = PAD + TOP_LABEL_H

    for col, name in month_labels(weeks):
        x = grid_x + col * PITCH
        parts.append(f'<text class="month" x="{x}" y="{PAD + 12}">{name}</text>')

    for row, label in DOW_LABELS.items():
        y = grid_y + row * PITCH + CELL - 2
        parts.append(f'<text class="dow" x="{PAD}" y="{y}">{label}</text>')

    for col, week in enumerate(weeks):
        for row, cell in enumerate(week):
            if cell is None:
                continue
            level = cell["level"]
            color = PALETTE[5] if (best_date and cell["date"] == best_date and level > 0) else PALETTE[level]
            x = grid_x + col * PITCH
            y = grid_y + row * PITCH
            delay = col * 0.014 + row * 0.03
            title = f'{cell["count"]} contributions on {cell["date"]}'
            parts.append(
                f'<rect class="day" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" style="animation-delay:{delay:.3f}s"><title>{title}</title></rect>'
            )

    legend_y = grid_y + grid_h + 16
    legend_x_end = width - PAD
    parts.append(f'<text class="dow" x="{legend_x_end - 150}" y="{legend_y + 8}">Less</text>')
    for i, color in enumerate(PALETTE[:5]):
        x = legend_x_end - 118 + i * (CELL + 3)
        parts.append(f'<rect x="{x}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    parts.append(f'<text class="dow" x="{legend_x_end - 118 + 5 * (CELL + 3) + 6}" y="{legend_y + 8}">More</text>')

    footer_y = legend_y + LEGEND_H + 6
    total = payload["total_last_year"]
    streak = stats["current_streak"]
    longest = stats["longest_streak"]
    footer = (
        f'<tspan fill="{GREEN}">{total}</tspan><tspan class="footer-dim"> contributions in the last year'
        f'  ·  current streak </tspan><tspan fill="{GREEN}">{streak}</tspan>'
        f'<tspan class="footer-dim"> days  ·  longest streak </tspan><tspan fill="{GREEN}">{longest}</tspan>'
        f'<tspan class="footer-dim"> days</tspan>'
    )
    parts.append(f'<text class="footer" x="{PAD}" y="{footer_y}">{footer}</text>')

    parts.append("</svg>")

    OUT_PATH.write_text("\n".join(parts))
    print(f"Wrote {OUT_PATH} ({width}x{height}, {n_cols} weeks)")


if __name__ == "__main__":
    main()
