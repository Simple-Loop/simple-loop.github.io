# /// script
# dependencies = ["Pillow"]
# ///
"""Render the existing Simple Loop identity for link previews.

Run: uv run scripts/render-social-card.py
The wireframe follows the torus projection used in loop.js.
"""
from pathlib import Path
from math import sin, cos, pi
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SCALE = 2
FONT_OPTIONS = [
    (Path('/System/Library/Fonts/Supplemental/Arial.ttf'), Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')),
    (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')),
]
REGULAR, BOLD = next(pair for pair in FONT_OPTIONS if all(p.exists() for p in pair))
canvas = Image.new('RGB', (1200 * SCALE, 630 * SCALE), '#f7f7f9')
draw = ImageDraw.Draw(canvas)


def text(x, y, value, size, bold=False, color='#1a1a1a'):
    font = ImageFont.truetype(str(BOLD if bold else REGULAR), size * SCALE)
    draw.text((x * SCALE, y * SCALE), value, font=font, fill=color)


def project(u, v):
    radius, tube, turn, tilt = 205, 45, .30, .87
    x = (radius + tube * cos(v)) * cos(u)
    y = (radius + tube * cos(v)) * sin(u)
    z = tube * sin(v)
    ry, rz = y * cos(tilt) - z * sin(tilt), y * sin(tilt) + z * cos(tilt)
    rx, depth = x * cos(turn) + rz * sin(turn), -x * sin(turn) + rz * cos(turn)
    perspective = 1400 / (1400 + depth)
    return ((902 + (rx * .98 - ry * .19) * perspective) * SCALE,
            (330 + (rx * .19 + ry * .98) * perspective) * SCALE)


for ring in range(12):
    draw.line([project(step / 144 * 2 * pi, ring / 12 * 2 * pi) for step in range(145)], fill='#bec9da', width=1)
for segment in range(48):
    draw.line([project(segment / 48 * 2 * pi, step / 32 * 2 * pi) for step in range(33)], fill='#ced6e2', width=1)
for dot in range(4):
    x, y = project(.7 + dot * pi / 2, dot * 1.7)
    r = 3 * SCALE
    draw.ellipse((x-r, y-r, x+r, y+r), fill='#467bc9')
logo = ImageOps.contain(Image.open(ROOT / 'assets/hy-logo.png').convert('RGBA'), (190 * SCALE, 36 * SCALE), Image.Resampling.LANCZOS)
canvas.paste(logo, (56 * SCALE, 44 * SCALE), logo)
text(56, 203, 'Simple Loop', 78, bold=True)
text(56, 311, 'A Simple and Scalable Framework', 30, color='#464750')
text(56, 355, 'for Scientific Discovery', 30, color='#464750')
text(56, 557, 'Hunyuan Team, Tencent', 21, color='#65666f')
output = ROOT / 'assets/social/simple-loop.png'
output.parent.mkdir(exist_ok=True)
canvas.resize((1200, 630), Image.Resampling.LANCZOS).save(output, optimize=True)
