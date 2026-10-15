#!/usr/bin/env python3
"""Draws Olympus's emblem (a Greek temple inside a ring of Greek key, white
on black, a sibling of Sparta's helmet) and makes every icon from it:

    packaging/emblem.png               1024 x 1024, transparent
    packaging/icon.png                 256 x 256, on a black rounded square
    packaging/macos/Olympus.icns       (macOS only: needs iconutil)
    packaging/android/res/mipmap-*/    adaptive foreground and monochrome,
                                       legacy square and round icons

Needs Pillow. The icons are committed, so a build does not run this; run it
again after changing the drawing.

    python3 packaging/make_icons.py
"""
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SIZE = 1024
SS = 4  # drawn this many times larger, then scaled down smoothly
WHITE = (255, 255, 255, 255)


def emblem():
    n = SIZE * SS
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    k = n / 1024  # the drawing is laid out on a 1024 grid

    # The ring: two circles with a Greek key (meander) between them.
    outer, inner = 470 * k, 350 * k
    width = 16 * k
    d.ellipse((c - outer, c - outer, c + outer, c + outer), outline=WHITE, width=int(width))
    d.ellipse((c - inner, c - inner, c + inner, c + inner), outline=WHITE, width=int(width))
    units = 28
    band_in, band_out = inner + 22 * k, outer - 22 * k
    depth = band_out - band_in

    def polar(angle, radius):
        return c + radius * math.cos(angle), c + radius * math.sin(angle)

    # One key unit in (along, across) fractions of its cell: a square spiral.
    key = [(0.0, 0.0), (0.0, 1.0), (0.8, 1.0), (0.8, 0.25), (0.35, 0.25), (0.35, 0.65), (0.55, 0.65)]
    for u in range(units):
        start = 2 * math.pi * u / units
        span = 2 * math.pi / units
        points = []
        for along, across in key:
            # Many small steps along each side so straight parts follow the circle.
            points.append((start + along * span, band_in + across * depth))
        pixels = []
        for (a0, r0), (a1, r1) in zip(points, points[1:]):
            steps = max(2, int(abs(a1 - a0) / span * 12) + 1)
            for i in range(steps + 1):
                t = i / steps
                pixels.append(polar(a0 + (a1 - a0) * t, r0 + (r1 - r0) * t))
        d.line(pixels, fill=WHITE, width=int(18 * k), joint='curve')
        # The base line joining one unit to the next.
        d.line([polar(start + 0.8 * span, band_in + 0.0 * depth), polar(start + span, band_in)], fill=WHITE,
               width=int(18 * k))
        d.line([polar(start, band_in), polar(start + 0.8 * span, band_in)], fill=WHITE, width=int(18 * k))

    # The temple: steps, four columns, an architrave and a pediment.
    def box(x0, y0, x1, y1):
        d.rectangle((c + x0 * k, c + y0 * k, c + x1 * k, c + y1 * k), fill=WHITE)

    box(-230, 175, 230, 205)   # lowest step
    box(-205, 145, 205, 170)   # second step
    box(-185, -85, 185, -55)   # architrave
    for x in (-160, -70, 40, 130):
        box(x, -45, x + 30, 140)        # column shaft
        box(x - 10, -55, x + 40, -45)   # capital
        box(x - 10, 135, x + 40, 145)   # base
    d.polygon([(c - 215 * k, c - 95 * k), (c, c - 215 * k), (c + 215 * k, c - 95 * k)], fill=WHITE)
    # The pediment's hollow, so it reads as a gable.
    d.polygon([(c - 150 * k, c - 115 * k), (c, c - 180 * k), (c + 150 * k, c - 115 * k)], fill=(0, 0, 0, 0))
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def on_square(picture, size, radius=0.18):
    """The emblem on a black rounded square, as Sparta's icon is."""
    n = size * SS
    square = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(square).rounded_rectangle((0, 0, n - 1, n - 1), radius=int(n * radius), fill=(0, 0, 0, 255))
    inner = picture.resize((int(n * 0.86), int(n * 0.86)), Image.LANCZOS)
    square.alpha_composite(inner, ((n - inner.size[0]) // 2, (n - inner.size[1]) // 2))
    return square.resize((size, size), Image.LANCZOS)


def on_circle(picture, size):
    n = size * SS
    disc = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(disc).ellipse((0, 0, n - 1, n - 1), fill=(0, 0, 0, 255))
    inner = picture.resize((int(n * 0.86), int(n * 0.86)), Image.LANCZOS)
    disc.alpha_composite(inner, ((n - inner.size[0]) // 2, (n - inner.size[1]) // 2))
    return disc.resize((size, size), Image.LANCZOS)


def android(picture, res):
    for density, scale in (('mdpi', 1), ('hdpi', 1.5), ('xhdpi', 2), ('xxhdpi', 3), ('xxxhdpi', 4)):
        folder = res / f'mipmap-{density}'
        folder.mkdir(parents=True, exist_ok=True)
        layer, inner, legacy = round(108 * scale), round(72 * scale), round(48 * scale)
        # Adaptive foreground: the emblem inside the 72 dp the launcher's mask keeps.
        foreground = Image.new('RGBA', (layer, layer), (0, 0, 0, 0))
        small = picture.resize((inner, inner), Image.LANCZOS)
        foreground.alpha_composite(small, ((layer - inner) // 2, (layer - inner) // 2))
        foreground.save(folder / 'ic_launcher_foreground.png')
        # Monochrome: the emblem's shape in white, for themed icons.
        mono = Image.new('RGBA', (layer, layer), (255, 255, 255, 0))
        mono.putalpha(foreground.getchannel('A'))
        mono.save(folder / 'ic_launcher_monochrome.png')
        on_square(picture, legacy).save(folder / 'ic_launcher.png')
        on_circle(picture, legacy).save(folder / 'ic_launcher_round.png')


def macos(picture, out):
    if not shutil.which('iconutil'):
        print('no iconutil: the .icns is left as it is')
        return
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / 'Olympus.iconset'
        iconset.mkdir()
        for size in (16, 32, 128, 256, 512):
            on_square(picture, size).save(iconset / f'icon_{size}x{size}.png')
            on_square(picture, size * 2).save(iconset / f'icon_{size}x{size}@2x.png')
        subprocess.run(['iconutil', '-c', 'icns', str(iconset), '-o', str(out)], check=True)


def main():
    picture = emblem()
    picture.save(HERE / 'emblem.png')
    on_square(picture, 256).save(HERE / 'icon.png')
    android(picture, HERE / 'android' / 'res')
    (HERE / 'macos').mkdir(exist_ok=True)
    macos(picture, HERE / 'macos' / 'Olympus.icns')
    return 0


if __name__ == '__main__':
    sys.exit(main())
