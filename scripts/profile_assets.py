#!/usr/bin/env python3
"""Build the botanical hero GIF and check local README artwork references."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PALETTE = {
    "ivory": "#F6F3EC",
    "sand": "#E8E2D9",
    "plum": "#806784",
    "rose": "#C99AA9",
    "sage": "#91B7AE",
    "terracotta": "#B98E79",
    "charcoal": "#292725",
}
WIDTH, HEIGHT = 540, 330
SCALE = 2
FRAME_COUNT = 20


def cubic(p0, p1, p2, p3, t):
    """Return one point on a cubic Bezier curve."""
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
    )


def rgba(hex_colour, alpha=255):
    value = hex_colour.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def draw_leaf(draw, anchor, angle, length, width, fill, line):
    """Draw a pointed oval leaf, its outline, and a fine centre vein."""
    from math import cos, radians, sin

    def point(x, y):
        theta = radians(angle)
        return (
            (anchor[0] + x * cos(theta) - y * sin(theta)) * SCALE,
            (anchor[1] + x * sin(theta) + y * cos(theta)) * SCALE,
        )

    outline = [point(0, 0), point(length * 0.42, -width), point(length, 0), point(length * 0.46, width)]
    draw.polygon(outline, fill=fill)
    draw.line(outline + [outline[0]], fill=line, width=2 * SCALE, joint="curve")
    draw.line([point(0, 0), point(length * 0.84, 0)], fill=line, width=SCALE)


def render_frame(frame_index):
    """Draw one antialiased frame using Pillow's built-in drawing primitives."""
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("GIF generation needs Pillow. Install it with: python -m pip install Pillow") from exc

    from math import cos, pi, sin

    canvas = Image.new("RGBA", (WIDTH * SCALE, HEIGHT * SCALE), rgba(PALETTE["ivory"]))
    draw = ImageDraw.Draw(canvas, "RGBA")
    # A quiet paper grain, plus two low-contrast organic colour fields.
    texture = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    for y in range(12, HEIGHT, 18):
        for x in range(12, WIDTH, 18):
            texture_draw.ellipse((x * SCALE, y * SCALE, (x + 1) * SCALE, (y + 1) * SCALE), fill=rgba(PALETTE["plum"], 10))
    texture_draw.ellipse((270 * SCALE, 12 * SCALE, 520 * SCALE, 262 * SCALE), fill=rgba(PALETTE["sage"], 30))
    texture_draw.ellipse((296 * SCALE, 42 * SCALE, 504 * SCALE, 250 * SCALE), fill=rgba(PALETTE["rose"], 25))
    canvas.alpha_composite(texture)
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Layered sand shapes at the foot of the illustration.
    hill_segments = (
        ((18, 264), (88, 222), (139, 302), (205, 267)),
        ((205, 267), (275, 232), (322, 288), (386, 258)),
        ((386, 258), (438, 239), (477, 231), (522, 226)),
    )
    hill_line = []
    for segment in hill_segments:
        hill_line.extend(cubic(*segment, step / 24) for step in range(25))
    hill_points = [(x * SCALE, y * SCALE) for x, y in hill_line]
    draw.polygon(hill_points + [(522 * SCALE, 328 * SCALE), (18 * SCALE, 328 * SCALE)], fill=rgba(PALETTE["sand"]))
    contour = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    contour_draw = ImageDraw.Draw(contour)
    contour_draw.line([(x * SCALE, y * SCALE) for x, y in (cubic((40, 278), (160, 240), (250, 317), (515, 244), step / 40) for step in range(41))],
                      fill=rgba(PALETTE["rose"], 105), width=2 * SCALE)
    canvas.alpha_composite(contour)

    # Small plum sunburst in the open left side.
    cx, cy = 84 * SCALE, 78 * SCALE
    for ray in range(12):
        angle = 2 * pi * ray / 12
        start, end = 13 * SCALE, (28 if ray % 2 == 0 else 23) * SCALE
        draw.line((cx + cos(angle) * start, cy + sin(angle) * start,
                   cx + cos(angle) * end, cy + sin(angle) * end), fill=rgba(PALETTE["plum"], 220), width=2 * SCALE)
    draw.ellipse((cx - 3 * SCALE, cy - 3 * SCALE, cx + 3 * SCALE, cy + 3 * SCALE), fill=rgba(PALETTE["plum"]))

    # A gentle two-degree sway makes the motion noticeable without dominating.
    sway = 2.2 * sin(2 * pi * frame_index / FRAME_COUNT)
    curve = ( (320, 280), (366, 232), (377, 138), (474, 48) )
    branch = []
    for index in range(49):
        x, y = cubic(*curve, index / 48)
        branch.append((x * SCALE, y * SCALE))
    # Shift the branch subtly around its base to make a clean, looping motion.
    branch = [(x + sway * SCALE * ((HEIGHT * SCALE - y) / (HEIGHT * SCALE)), y) for x, y in branch]
    draw.line(branch, fill=rgba(PALETTE["plum"], 235), width=3 * SCALE, joint="curve")

    # Alternate leaves along the stem. Their small independent drift adds depth.
    leaves = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    leaf_draw = ImageDraw.Draw(leaves, "RGBA")
    for index, t in enumerate((0.22, 0.38, 0.54, 0.69, 0.83)):
        base = cubic(*curve, t)
        tangent = cubic(*curve, min(0.99, t + 0.01))
        from math import atan2, degrees
        branch_angle = degrees(atan2(tangent[1] - base[1], tangent[0] - base[0]))
        side = 1 if index % 2 == 0 else -1
        leaf_angle = branch_angle + side * (48 + 2.0 * sin(2 * pi * frame_index / FRAME_COUNT + index))
        anchor = (base[0] + sway * (HEIGHT - base[1]) / HEIGHT, base[1])
        colour = (PALETTE["sage"], PALETTE["rose"], PALETTE["sage"], PALETTE["terracotta"], PALETTE["rose"])[index]
        draw_leaf(leaf_draw, anchor, leaf_angle, 49 if index < 4 else 42, 14, rgba(colour, 170), rgba(PALETTE["plum"], 205))
    canvas.alpha_composite(leaves)

    # A few fixed accents; the pulse is intentionally very slight.
    pulse = 1.0 + 0.12 * sin(2 * pi * frame_index / FRAME_COUNT)
    for x, y, radius, colour in ((486, 45, 5, "plum"), (474, 69, 2.5, "rose"),
                                 (342, 89, 2, "terracotta"), (500, 157, 2, "rose")):
        r = radius * (pulse if radius == 5 else 1)
        draw.ellipse(((x - r) * SCALE, (y - r) * SCALE, (x + r) * SCALE, (y + r) * SCALE),
                     fill=rgba(PALETTE[colour], 220))

    # Round the artwork's corners, then reduce to its final display size.
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((1, 1, canvas.width - 2, canvas.height - 2), radius=24 * SCALE, fill=255)
    canvas.putalpha(mask)
    return canvas.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def build_hero():
    from PIL import Image

    output = ROOT / "assets" / "hero" / "botanical-loop.gif"
    output.parent.mkdir(parents=True, exist_ok=True)
    palette = render_frame(0).convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    frames = [render_frame(index).quantize(palette=palette, dither=Image.Dither.NONE) for index in range(FRAME_COUNT)]
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=2)
    print(f"Wrote {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")


def check_assets():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    local_paths = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', readme, flags=re.IGNORECASE)
    local_paths.extend(re.findall(r'\]\((assets/[^)]+)\)', readme, flags=re.IGNORECASE))
    local_paths.extend(re.findall(r'<a\b[^>]*\bhref="(assets/[^"]+)"', readme, flags=re.IGNORECASE))
    for relative in local_paths:
        if re.match(r"https?://", relative):
            continue
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"README image is missing: {relative}")
        if path.suffix.lower() == ".svg":
            ElementTree.parse(path)
        print(f"OK  {relative}")

    allowed_colours = {value.upper() for value in PALETTE.values()}
    for svg_path in sorted((ROOT / "assets").rglob("*.svg")):
        ElementTree.parse(svg_path)
        used = {value.upper() for value in re.findall(r"#[0-9A-Fa-f]{6}", svg_path.read_text(encoding="utf-8"))}
        unexpected = used - allowed_colours
        if unexpected:
            raise RuntimeError(f"Unexpected palette colour in {svg_path.relative_to(ROOT)}: {', '.join(sorted(unexpected))}")
        print(f"OK  {svg_path.relative_to(ROOT)} SVG and palette")

    try:
        from PIL import Image
    except ImportError:
        print("NOTE  Pillow unavailable; skipped GIF dimension and frame checks.")
    else:
        gif_path = ROOT / "assets" / "hero" / "botanical-loop.gif"
        with Image.open(gif_path) as gif:
            if gif.size != (WIDTH, HEIGHT) or gif.n_frames != FRAME_COUNT:
                raise RuntimeError(f"Unexpected hero GIF: {gif.size}, {gif.n_frames} frames")
            if gif_path.stat().st_size > 750_000:
                raise RuntimeError("Hero GIF exceeds the 750 KB size budget")
            print(f"OK  hero GIF: {gif.width}x{gif.height}, {gif.n_frames} frames, {gif_path.stat().st_size:,} bytes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check", "all"), nargs="?", default="all")
    args = parser.parse_args()
    try:
        if args.action in ("build", "all"):
            build_hero()
        if args.action in ("check", "all"):
            check_assets()
    except (OSError, RuntimeError, ElementTree.ParseError) as error:
        print(f"ERROR  {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
