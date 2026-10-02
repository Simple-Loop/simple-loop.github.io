# /// script
# dependencies = ["Pillow"]
# ///
"""Render a geometric Simple Loop cover in the Hy research-card style.

Run: uv run scripts/render-social-card.py
The decorative wireframe follows the torus projection used in loop.js.
"""
from pathlib import Path
from math import sin, cos, pi, hypot
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SCALE = 3
BG = '#f5f5f7'
INK = '#202125'
FONT_OPTIONS = [
    (Path('/System/Library/Fonts/Supplemental/Arial.ttf'), Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')),
    (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')),
]
REGULAR, BOLD = next(pair for pair in FONT_OPTIONS if all(p.exists() for p in pair))
canvas = Image.new('RGB', (1200 * SCALE, 630 * SCALE), BG)
draw = ImageDraw.Draw(canvas)


def text(x, y, value, size, bold=False, color=INK):
    font = ImageFont.truetype(str(BOLD if bold else REGULAR), size * SCALE)
    assert draw.textlength(value, font=font) <= 1072 * SCALE
    draw.text((x * SCALE, y * SCALE), value, font=font, fill=color)


def project(u, v):
    radius, tube, turn, tilt = 315, 48, .22, 1.04
    x = (radius + tube * cos(v)) * cos(u)
    y = (radius + tube * cos(v)) * sin(u)
    z = tube * sin(v)
    ry, rz = y * cos(tilt) - z * sin(tilt), y * sin(tilt) + z * cos(tilt)
    rx, depth = x * cos(turn) + rz * sin(turn), -x * sin(turn) + rz * cos(turn)
    perspective = 1800 / (1800 + depth)
    return ((600 + rx * perspective) * SCALE,
            (239 + ry * perspective * .80) * SCALE)


def line(points, color, width=1):
    draw.line(points, fill=color, width=max(1, round(width * SCALE)), joint='curve')


# Faint construction axes and restrained mesh, with one clear closed path.
for x in range(180, 1020, 9):
    line([(x*SCALE,239*SCALE),((x+3)*SCALE,239*SCALE)], '#bfc2ca', .7)
for ring in range(8):
    line([project(step / 240 * 2 * pi, ring / 8 * 2 * pi) for step in range(241)], '#9ea2ac', .65)
for segment in range(32):
    line([project(segment / 32 * 2 * pi, step / 72 * 2 * pi) for step in range(73)], '#b2b5bd', .65)
route = [project(step / 240 * 2 * pi, .55) for step in range(241)]
line(route, INK, 1.7)
for angle, color in [(0.25, '#f2f7bd'), (2.0, '#d8f1f5'), (3.5, '#e7e6d9'), (5.05, '#d8f1f5')]:
    x, y = project(angle, .55)
    r = 7 * SCALE
    draw.ellipse((x-r, y-r, x+r, y+r), fill=color, outline=INK, width=round(1.3*SCALE))
# A small tangent arrow makes the loop direction readable without adding labels.
x,y = project(.95,.55)
x2,y2 = project(.98,.55)
dx,dy = x2-x,y2-y
length = hypot(dx,dy)
dx,dy = dx/length,dy/length
line([(x-8*SCALE*dx-4*SCALE*dy,y-8*SCALE*dy+4*SCALE*dx),(x,y),
      (x-8*SCALE*dx+4*SCALE*dy,y-8*SCALE*dy-4*SCALE*dx)], INK, 1.3)
logo = ImageOps.contain(Image.open(ROOT / 'assets/hy-logo.png').convert('RGBA'), (153 * SCALE, 29 * SCALE), Image.Resampling.LANCZOS)
canvas.paste(logo, (64 * SCALE, 40 * SCALE), logo)
text(64, 449, 'Simple Loop', 48, bold=True)
text(66, 514, 'A Simple and Scalable Framework for Scientific Discovery', 26, color='#555963')
text(66, 575, 'Hunyuan Team, Tencent', 17, color='#787c85')
output = ROOT / 'assets/social/simple-loop.png'
output.parent.mkdir(exist_ok=True)
canvas.resize((1200, 630), Image.Resampling.LANCZOS).save(output, optimize=True)
