#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing, monochrome ASCII-art SVG.

Each row wipes in left-to-right (a small block cursor rides the wipe edge),
staggered top to bottom. The whole portrait prints once and freezes.

Usage: python scripts/make_ascii_svg.py [source-prepped.png] [--cols N]
Writes: ascii-portrait.svg
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT / "source-prepped.png"
OUT_PATH = ROOT / "ascii-portrait.svg"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing

FILL = "#c9d1d9"
CURSOR = "#39d353"
BG = "#0d1117"
BORDER = "#30363d"

FONT_SIZE = 8.4
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
PAD = 16
CHAR_ASPECT = 0.5  # width/height of a monospace glyph, used to keep proportions sane


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_args():
    args = sys.argv[1:]
    cols = 100
    src = DEFAULT_SRC
    i = 0
    positional = []
    while i < len(args):
        if args[i] == "--cols":
            cols = int(args[i + 1])
            i += 2
        else:
            positional.append(args[i])
            i += 1
    if positional:
        src = Path(positional[0])
    return src, cols


def image_to_grid(src, cols):
    img = Image.open(src).convert("L")
    w, h = img.size
    rows = max(1, round(cols * (h / w) * CHAR_ASPECT))
    small = img.resize((cols, rows), Image.LANCZOS)
    return np.array(small), rows


def brightness_to_char(v):
    idx = round((255 - v) / 255 * (len(RAMP) - 1))
    return RAMP[idx]


def main():
    src, cols = parse_args()
    if not src.exists():
        print(f"Missing input image: {src}", file=sys.stderr)
        print("Run scripts/prep_photo.py <photo> first.", file=sys.stderr)
        sys.exit(1)

    pixels, rows = image_to_grid(src, cols)

    grid_w = cols * CHAR_W
    grid_h = rows * CHAR_H
    width = grid_w + PAD * 2
    height = grid_h + PAD * 2

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">'
    )
    parts.append(f"""
  <style>
    .card {{ fill: {BG}; stroke: {BORDER}; stroke-width: 1; }}
    text {{ font-family: Menlo, Consolas, 'SF Mono', monospace; font-size: {FONT_SIZE}px;
            fill: {FILL}; white-space: pre; }}
  </style>
""")
    parts.append(f'<rect class="card" x="0.5" y="0.5" width="{width - 1:.0f}" height="{height - 1:.0f}" rx="8"/>')

    row_dur = 0.35
    row_stagger = 0.045

    for r in range(rows):
        line = "".join(brightness_to_char(int(pixels[r, c])) for c in range(cols))
        y = PAD + (r + 1) * CHAR_H - CHAR_H * 0.25
        row_y_top = PAD + r * CHAR_H
        delay = r * row_stagger
        clip_id = f"rowclip{r}"

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="{PAD}" y="{row_y_top:.2f}" width="0" height="{CHAR_H:.2f}">'
            f'<animate attributeName="width" from="0" to="{grid_w:.2f}" '
            f'begin="{delay:.3f}s" dur="{row_dur}s" fill="freeze"/>'
            f"</rect>"
        )
        parts.append("</clipPath>")

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(f'<text x="{PAD}" y="{y:.2f}" xml:space="preserve">{esc(line)}</text>')
        parts.append("</g>")

        parts.append(
            f'<rect x="0" y="{row_y_top:.2f}" width="{CHAR_W:.2f}" height="{CHAR_H:.2f}" fill="{CURSOR}">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + grid_w:.2f}" '
            f'begin="{delay:.3f}s" dur="{row_dur}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.85;1" '
            f'begin="{delay:.3f}s" dur="{row_dur}s" fill="freeze"/>'
            f"</rect>"
        )

    parts.append("</svg>")

    OUT_PATH.write_text("\n".join(parts))
    print(f"Wrote {OUT_PATH} ({cols}x{rows} chars, {width:.0f}x{height:.0f}px)")


if __name__ == "__main__":
    main()
