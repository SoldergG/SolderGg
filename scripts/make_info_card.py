#!/usr/bin/env python3
"""Hand-authored neofetch-style info-card.svg.

Lines fade + slide in on a short stagger, like they're printing next to the
portrait. Set STATIC=1 to emit a frozen frame (all lines visible, no
animation) for local Quick Look previews.
"""
import os
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "info-card.svg"

BG = "#0D1424"
BORDER = "#26304A"
HEADER = "#D9C7A7"
KEY_COLORS = ["#9DB5EE", "#D9C7A7", "#9DB5EE", "#D9C7A7"]
VALUE = "#F2F0EA"
DIM = "#A6B0C3"

WIDTH = 490
PAD_X = 22
TITLE_Y = 44
RULE_Y = 56
ROW_START_Y = 86
ROW_GAP = 30
FONT = "Menlo, Consolas, 'SF Mono', monospace"

ROWS = [
    ("Now", "Lunar · school assistant, iOS + web + Android"),
    ("Prev", "Portfolio redesign · soldergg.github.io"),
    ("Stack", "Swift/SwiftUI · Kotlin/Compose · React Native"),
    ("", "Next.js · Three.js · Supabase"),
    ("Shipped", "KebabLocator on the App Store · 36 public repos"),
]

STATIC = os.environ.get("STATIC") == "1"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    n_rows = len(ROWS) + 1  # + header row
    height = ROW_START_Y + (len(ROWS) - 1) * ROW_GAP + 34

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="{FONT}">'
    )

    anim_css = "" if STATIC else """
    .line { opacity: 0; transform-box: fill-box; transform-origin: left; animation: fadein 0.45s ease-out forwards; }
    @keyframes fadein {
      0%   { opacity: 0; transform: translateX(-6px); }
      100% { opacity: 1; transform: translateX(0); }
    }
"""
    parts.append(f"""
  <style>
    .card {{ fill: {BG}; stroke: {BORDER}; stroke-width: 1; }}
    .dot {{ opacity: 0.9; }}
    .title {{ fill: {HEADER}; font-size: 15px; font-weight: bold; }}
    .key {{ font-size: 13px; font-weight: bold; }}
    .value {{ fill: {VALUE}; font-size: 13px; }}
    .dim {{ fill: {DIM}; font-size: 12px; }}
    {anim_css.strip()}
  </style>
""")

    parts.append(f'<rect class="card" x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8"/>')

    # traffic-light window chrome
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle class="dot" cx="{PAD_X + i * 16}" cy="18" r="5" fill="{c}"/>')

    delay = 0.0
    step = 0.09

    def line(y, content_svg):
        nonlocal delay
        cls = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        delay += step
        return f'<g class="line"{cls}>{content_svg}</g>' if not STATIC else f'<g>{content_svg}</g>'

    parts.append(line(TITLE_Y, f'<text class="title" x="{PAD_X}" y="{TITLE_Y}">lucas@soldergg</text>'))
    rule = "-" * 34
    parts.append(line(RULE_Y, f'<text class="dim" x="{PAD_X}" y="{RULE_Y}">{rule}</text>'))

    x_value = PAD_X + max(len(k) for k, _ in ROWS if k) * 8 + 20

    y = ROW_START_Y
    key_i = 0
    for key, value in ROWS:
        if key:
            color = KEY_COLORS[key_i % len(KEY_COLORS)]
            key_i += 1
            row_svg = (
                f'<text x="{PAD_X}" y="{y}" class="key" fill="{color}">{esc(key)}:</text>'
                f'<text x="{x_value}" y="{y}" class="value">{esc(value)}</text>'
            )
        else:
            row_svg = f'<text x="{x_value}" y="{y}" class="value">{esc(value)}</text>'
        parts.append(line(y, row_svg))
        y += ROW_GAP

    parts.append("</svg>")

    OUT_PATH.write_text("\n".join(parts))
    mode = "static" if STATIC else "animated"
    print(f"Wrote {OUT_PATH} ({WIDTH}x{height}, {mode})")


if __name__ == "__main__":
    main()
