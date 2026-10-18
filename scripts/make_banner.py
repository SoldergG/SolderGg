#!/usr/bin/env python3
"""banner.svg: the profile header, in the portfolio's Porcelana palette (night variant).

Navy ground, cream type, the cobalt lifted for contrast. App icons are embedded so
GitHub's image proxy renders them. Lines rise in on a short stagger; STATIC=1 freezes it.
"""
import base64, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "banner.svg"
STATIC = os.environ.get("STATIC") == "1"

BG, LINE = "#0D1424", "#26304A"
INK, INK2, COBALT, SAND = "#F2F0EA", "#A6B0C3", "#9DB5EE", "#D9C7A7"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', Menlo, Consolas, monospace"
W, H = 860, 300
APPS = ["lunar", "solarcalc", "teeup", "podcasthelper", "kebablocator", "groupmemo"]


def icon(name):
    return "data:image/png;base64," + base64.b64encode((ROOT / "assets/icons" / f"{name}.png").read_bytes()).decode()


def main():
    anim = "" if STATIC else """
    .r { opacity: 0; animation: rise .7s cubic-bezier(.16,1,.3,1) forwards; }
    @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
    .d1 { animation-delay: .05s } .d2 { animation-delay: .15s } .d3 { animation-delay: .25s } .d4 { animation-delay: .4s } .d5 { animation-delay: .55s }
    .dot { animation: pulse 2.6s ease-out infinite; transform-box: fill-box; transform-origin: center; }
    @keyframes pulse { 0% { opacity: .55; transform: scale(1) } 70%, 100% { opacity: 0; transform: scale(2.6) } }"""
    icons = "".join(
        f'<clipPath id="c{i}"><rect x="{40 + i * 52}" y="214" width="40" height="40" rx="9"/></clipPath>'
        f'<image href="{icon(n)}" x="{40 + i * 52}" y="214" width="40" height="40" clip-path="url(#c{i})"/>'
        f'<rect x="{40.5 + i * 52}" y="214.5" width="39" height="39" rx="9" fill="none" stroke="{LINE}"/>'
        for i, n in enumerate(APPS))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Lucas Salvador, iOS and full-stack developer in Lisbon. I build apps people open every day. Portfolio at soldergg.github.io">
  <style>{anim}
  </style>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{BG}" stroke="{LINE}"/>
  <g class="r d1"><text x="40" y="56" font-family="{MONO}" font-size="13" fill="{INK2}">// ios · full-stack · lisbon, pt</text></g>
  <g class="r d2"><text x="40" y="110" font-family="{SANS}" font-size="44" font-weight="500" letter-spacing="-1.4" fill="{INK}">I build apps people <tspan fill="{COBALT}">open every day.</tspan></text></g>
  <g class="r d3"><text x="40" y="150" font-family="{SANS}" font-size="17" fill="{INK2}">Lucas Salvador · native iOS in SwiftUI and full-stack web with Next.js and Supabase,</text>
  <text x="40" y="174" font-family="{SANS}" font-size="17" fill="{INK2}">from the first sketch to the App Store.</text></g>
  <g class="r d4">{icons}</g>
  <g class="r d5">
    <rect x="586" y="214" width="234" height="40" rx="20" fill="{INK}"/>
    <text x="703" y="239" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="500" fill="{BG}">soldergg.github.io  →</text>
    <circle cx="806" cy="44" r="4.5" fill="#5FBF86"/><circle class="dot" cx="806" cy="44" r="4.5" fill="#5FBF86"/>
    <text x="794" y="48" text-anchor="end" font-family="{MONO}" font-size="12" fill="{SAND}">open to projects</text>
  </g>
</svg>
'''
    OUT.write_text(svg)
    print("wrote", OUT, len(svg) // 1024, "KB")


if __name__ == "__main__":
    main()
