#!/usr/bin/env python3
"""Build the combined, contrast-enhanced Pingpong art sheet with Pillow.

This single, self-contained script renders every category and packs them into
one 1060 x 600 RGBA sheet:

  * dreamy-sky background: one 800 x 600 fully opaque frame
  * ball-bubble: 4 idle bubbles (64 x 64) and 4 trail bubbles (60 x 24)
  * bubble-pop: 8 burst frames (64 x 64)
  * paddle-cloud: cloud_idle and cloud_hit (48 x 360)

The four deterministic renderers are embedded below and run in isolated
namespaces. This revision deepens the mid-sky and paddle lanes, adds
blue-lavender cloud shadows and gives the bubble and cloud sprites stronger
rims so they read at 800 x 600. The bubble-pop frames continue the same
iridescent soap-film style below the original sprite block. No PNG input,
external asset, font, or random source is used. The output is written next to
this script as ``pingpong-art.png``; the whitespace-delimited frame/animation manifest is
written as ``pingpong-art.spritepos`` from the same tables.

Existing frame coordinates and pixels are unchanged: the background is
appended to the right of the original 259 x 450 sprite sheet, separated by a
1 px transparent gutter at x=259, and the eight pop frames occupy the formerly
empty x=0..258, y=451..579 area. y=450 and y=515 remain 1 px transparent
separator rows, and x=64, 129 and 194 remain 1 px transparent gutters.

Run from anywhere:

    python3 assets/pingpong-art/build.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

SHEET_W, SHEET_H = 1060, 600
OUTPUT = Path(__file__).resolve().parent / "pingpong-art.png"
SPRITEPOS = Path(__file__).resolve().parent / "pingpong-art.spritepos"

# Bubble-pop frames occupy the formerly unused panel below the original
# sprite sheet. Two 64 px rows are separated by y=450 and y=515, with 1 px
# transparent gutters at x=64, 129 and 194.
POP_FRAMES = (
    ("pop_1", 0, 451, 64, 64),
    ("pop_2", 65, 451, 64, 64),
    ("pop_3", 130, 451, 64, 64),
    ("pop_4", 195, 451, 64, 64),
    ("pop_5", 0, 516, 64, 64),
    ("pop_6", 65, 516, 64, 64),
    ("pop_7", 130, 516, 64, 64),
    ("pop_8", 195, 516, 64, 64),
)

# Frame layout in the combined sheet: (name, x, y, w, h). The original eleven
# entries stay first and unchanged; the pop frames are appended in play order.
FRAMES = (
    ("bubble_1", 0, 0, 64, 64),
    ("bubble_2", 65, 0, 64, 64),
    ("bubble_3", 130, 0, 64, 64),
    ("bubble_4", 195, 0, 64, 64),
    ("trail_1", 0, 65, 60, 24),
    ("trail_2", 61, 65, 60, 24),
    ("trail_3", 122, 65, 60, 24),
    ("trail_4", 183, 65, 60, 24),
    ("cloud_idle", 81, 90, 48, 360),
    ("cloud_hit", 130, 90, 48, 360),
    ("background", 260, 0, 800, 600),
    *POP_FRAMES,
)

# Animation clips written into pingpong-art.spritepos.
# (clip name, fps, loop|once, frame names in play order)
ANIMATIONS = (
    ("ball.idle", 8, "loop", ("bubble_1", "bubble_2", "bubble_3", "bubble_4")),
    ("ball.trail", 8, "loop", ("trail_1", "trail_2", "trail_3", "trail_4")),
    ("ball.pop", 13, "once", tuple(frame[0] for frame in POP_FRAMES)),
    ("paddle.idle", 8, "loop", ("cloud_idle",)),
    ("paddle.hit", 8, "once", ("cloud_hit",)),
)

# ---------------------------------------------------------------------------
# Embedded deterministic renderers (contrast-enhanced, no file output)

BALL_RENDERER = r'''#!/usr/bin/env python3
"""Build the deterministic, contrast-enhanced ball-bubble sprite sheet.

The artwork is drawn at 4x resolution and downsampled with Lanczos so the
vector-like curves, rim colour transitions, and translucent glows stay smooth
at the 64 px and 60 px game sizes. A deep blue inner rim, a crisp ice pinline
and a soft lower-right shadow keep the bubble legible on the deeper sky.

Run from anywhere:

    python3 assets/ball-bubble/build.py

Only Pillow is required. There is no randomness, and the output has no
timestamp or platform metadata, so repeated runs are byte-for-byte stable.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# Output and palette

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "ball-bubble.png"

SHEET_W, SHEET_H = 259, 89
S = 4  # supersampling factor

WHITE = (247, 254, 255)      # #F7FEFF
CYAN = (143, 233, 255)       # #8FE9FF
AQUA = (94, 214, 255)        # #5ED6FF
LAVENDER = (205, 185, 255)   # #CDB9FF
PEACH = (255, 214, 232)      # #FFD6E8
DEEP_SHADOW = (60, 127, 181) # #3C7FB5
BLUE_RIM = (46, 127, 184)    # #2E7FB8
STEEL_BLUE = (60, 111, 168)  # #3C6FA8
PERI_BLUE = (94, 127, 184)   # #5E7FB8
SPARKLE = (255, 246, 201)    # #FFF6C9

# Sheet layout, exactly as consumed by the game.
FRAMES = (
    ("bubble_1", 0, 0, 64, 64, "idle"),
    ("bubble_2", 65, 0, 64, 64, "idle"),
    ("bubble_3", 130, 0, 64, 64, "idle"),
    ("bubble_4", 195, 0, 64, 64, "idle"),
    ("trail_1", 0, 65, 60, 24, "trail"),
    ("trail_2", 61, 65, 60, 24, "trail"),
    ("trail_3", 122, 65, 60, 24, "trail"),
    ("trail_4", 183, 65, 60, 24, "trail"),
)

# Four very gentle squash/stretch keys. The visible changes are deliberately
# small enough for an 8 fps idle loop, while still reading as a wobble.
BUBBLE_KEYS = (
    dict(cx=32.0, cy=31.9, rx=27.15, ry=26.15, rot=-0.8, phase=0.20,
         hi=(21.6, 20.3, 4.85, 2.00, -36.0),
         spark_a=(47.6, 18.6, 2.45, 8.0),
         spark_b=(15.4, 45.6, 1.35, -12.0)),
    dict(cx=31.8, cy=32.1, rx=27.55, ry=25.70, rot=0.55, phase=1.65,
         hi=(22.15, 20.85, 5.10, 1.85, -41.0),
         spark_a=(48.1, 19.2, 2.15, 21.0),
         spark_b=(16.1, 45.2, 1.15, -4.0)),
    dict(cx=32.1, cy=31.8, rx=26.70, ry=26.65, rot=-0.35, phase=3.05,
         hi=(21.05, 19.90, 4.55, 2.20, -33.0),
         spark_a=(47.0, 18.3, 2.65, -8.0),
         spark_b=(15.0, 45.9, 1.50, 16.0)),
    dict(cx=32.0, cy=32.15, rx=27.35, ry=26.05, rot=0.85, phase=4.55,
         hi=(21.65, 20.65, 4.95, 1.95, -39.0),
         spark_a=(47.9, 19.5, 2.30, 14.0),
         spark_b=(15.7, 45.3, 1.25, -20.0)),
)

# Four elongated, wobbling trail bubbles. They all stay centred on the frame
# so a game can anchor them by the frame centre.
TRAIL_KEYS = (
    dict(cx=30.1, cy=12.0, rx=23.0, ry=6.10, rot=-1.7, phase=0.4,
         hi=(22.7, 8.80, 6.30, 1.60, -4.0),
         spark=(49.2, 7.0, 1.55, 10.0)),
    dict(cx=29.8, cy=12.1, rx=23.8, ry=6.40, rot=0.6, phase=1.7,
         hi=(22.2, 9.00, 6.10, 1.75, 3.0),
         spark=(49.6, 7.4, 1.40, -14.0)),
    dict(cx=30.3, cy=11.9, rx=22.7, ry=6.70, rot=-0.5, phase=3.0,
         hi=(23.1, 8.55, 6.55, 1.65, -7.0),
         spark=(48.6, 7.2, 1.65, 18.0)),
    dict(cx=30.0, cy=12.15, rx=23.5, ry=6.20, rot=1.5, phase=4.4,
         hi=(22.5, 8.95, 6.20, 1.70, 1.0),
         spark=(49.3, 7.6, 1.50, -6.0)),
)


# ---------------------------------------------------------------------------
# Small colour / mask helpers


def layer(size: tuple[int, int]) -> Image.Image:
    """Transparent high-resolution layer.

    The hidden RGB is white rather than black. That keeps Lanczos resampling
    from producing dark fringes around faint, translucent edges.
    """

    return Image.new("RGBA", (size[0] * S, size[1] * S), (255, 255, 255, 0))


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float
        ) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lerp_stops(stops: Sequence[tuple[float, tuple[int, int, int]]],
               position: float) -> tuple[int, int, int]:
    """Linear RGB interpolation through sorted (0..1, colour) stops."""

    position = position % 1.0
    for index in range(len(stops) - 1):
        start_pos, start_col = stops[index]
        end_pos, end_col = stops[index + 1]
        if start_pos <= position <= end_pos:
            span = end_pos - start_pos
            amount = 0.0 if span == 0 else (position - start_pos) / span
            return mix(start_col, end_col, amount)
    return stops[-1][1]


def vertical_gradient(size: tuple[int, int],
                      stops: Sequence[tuple[float, tuple[int, int, int]]]
                      ) -> Image.Image:
    """Full-frame RGB gradient; stops are top-to-bottom fractions."""

    width, height = size[0] * S, size[1] * S
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        position = y / max(1, height - 1)
        draw.line((0, y, width, y), fill=lerp_stops(stops, position))
    return image


def angular_colour(size: tuple[int, int], centre: tuple[float, float],
                   stops: Sequence[tuple[float, tuple[int, int, int]]]
                   ) -> Image.Image:
    """Smooth RGB colour wheel used for the iridescent soap film.

    Pillow measures arc angles clockwise from 3 o'clock. Stop angles use the
    same convention: 225 is upper-left, 315 upper-right, 45 lower-right.
    """

    width, height = size[0] * S, size[1] * S
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)
    cx, cy = centre[0] * S, centre[1] * S
    radius = math.hypot(width, height) * 1.1
    bounds = (cx - radius, cy - radius, cx + radius, cy + radius)
    steps = 720
    for index in range(steps):
        start = index * 360.0 / steps
        end = (index + 1) * 360.0 / steps + 0.55
        colour = lerp_stops(stops, ((start + end) * 0.5 % 360.0) / 360.0)
        draw.pieslice(bounds, start, end, fill=colour)
    # A very small blur hides the wedge seams without making the rim fuzzy.
    return image.filter(ImageFilter.GaussianBlur(0.9 * S))


def colour_alpha(colour: tuple[int, int, int] | Image.Image, mask: Image.Image,
                 opacity: int = 255) -> Image.Image:
    """Return an RGBA layer with per-pixel alpha from an L mask."""

    if isinstance(colour, tuple):
        rgb = Image.new("RGB", mask.size, colour)
    else:
        rgb = colour.convert("RGB")
    if opacity != 255:
        mask = mask.point(lambda value: (value * opacity + 127) // 255)
    return Image.merge("RGBA", (*rgb.split(), mask))


def soft_mask(mask: Image.Image, final_radius: float) -> Image.Image:
    return mask.filter(ImageFilter.GaussianBlur(final_radius * S))


def body_mask(size: tuple[int, int], cx: float, cy: float, rx: float, ry: float,
              *, inset: float = 0.0, rotation: float = 0.0,
              phase: float = 0.0, wobble: float = 0.0) -> Image.Image:
    """Anti-aliased-by-downsampling ellipse with an optional soap wobble."""

    mask = Image.new("L", (size[0] * S, size[1] * S), 0)
    draw = ImageDraw.Draw(mask)
    points = []
    radians = math.radians(rotation)
    cos_r, sin_r = math.cos(radians), math.sin(radians)
    actual_rx = max(0.15, rx - inset)
    actual_ry = max(0.15, ry - inset)
    count = 720
    for index in range(count):
        theta = math.tau * index / count
        ripple = 1.0
        if wobble:
            ripple += wobble * (
                0.62 * math.sin(3.0 * theta + phase)
                + 0.38 * math.sin(5.0 * theta + phase * 1.7 + 0.8)
            )
        x = actual_rx * math.cos(theta) * ripple
        y = actual_ry * math.sin(theta) * ripple
        xr = x * cos_r - y * sin_r
        yr = x * sin_r + y * cos_r
        points.append(((cx + xr) * S, (cy + yr) * S))
    draw.polygon(points, fill=255)
    return mask


def clipped(layer_image: Image.Image, mask: Image.Image) -> Image.Image:
    result = layer_image.copy()
    alpha = ImageChops.multiply(result.getchannel("A"), mask)
    result.putalpha(alpha)
    return result


def radial_mask(size: tuple[int, int], cx: float, cy: float, rx: float,
                ry: float) -> Image.Image:
    """Soft radial rise from zero in the middle to full at the rim."""

    target = Image.new("L", (size[0] * S, size[1] * S), 0)
    width = max(2, round(2 * rx * S))
    height = max(2, round(2 * ry * S))
    # Pillow's gradient reaches 181/255 at an axis, so normalise that to 255
    # before it is multiplied by the (irregular) bubble mask.
    gradient = Image.radial_gradient("L").resize(
        (width, height), Image.Resampling.BILINEAR
    ).point(lambda value: min(255, round(value * 255 / 181)))
    left = round((cx - rx) * S)
    top = round((cy - ry) * S)
    target.paste(gradient, (left, top))
    return target


def rotated_ellipse_points(cx: float, cy: float, rx: float, ry: float,
                           rotation: float) -> list[tuple[float, float]]:
    radians = math.radians(rotation)
    cos_r, sin_r = math.cos(radians), math.sin(radians)
    points = []
    for index in range(180):
        theta = math.tau * index / 180
        x = rx * math.cos(theta)
        y = ry * math.sin(theta)
        points.append((
            (cx + x * cos_r - y * sin_r) * S,
            (cy + x * sin_r + y * cos_r) * S,
        ))
    return points


def add_rotated_oval(target: Image.Image, cx: float, cy: float, rx: float,
                     ry: float, rotation: float, colour: tuple[int, int, int],
                     alpha: int = 255, blur: float = 0.0) -> None:
    local = layer((target.width // S, target.height // S))
    draw = ImageDraw.Draw(local)
    draw.polygon(
        rotated_ellipse_points(cx, cy, rx, ry, rotation),
        fill=(*colour, alpha),
    )
    if blur:
        local = local.filter(ImageFilter.GaussianBlur(blur * S))
    target.alpha_composite(local)


def add_sparkle(target: Image.Image, cx: float, cy: float, radius: float,
                rotation: float = 0.0, alpha: int = 215) -> None:
    """Warm-white four-point glint with a small coloured halo."""

    size = (target.width // S, target.height // S)
    radians = math.radians(rotation)
    cos_r, sin_r = math.cos(radians), math.sin(radians)

    def point(distance: float, angle: float) -> tuple[float, float]:
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        return ((cx + x * cos_r - y * sin_r) * S,
                (cy + x * sin_r + y * cos_r) * S)

    # Halo first, so it sits behind the crisp needle points.
    halo = layer(size)
    hdraw = ImageDraw.Draw(halo)
    hdraw.ellipse(
        ((cx - radius * 2.15) * S, (cy - radius * 2.15) * S,
         (cx + radius * 2.15) * S, (cy + radius * 2.15) * S),
        fill=(*SPARKLE, 48),
    )
    halo = halo.filter(ImageFilter.GaussianBlur(radius * 1.25 * S))
    target.alpha_composite(halo)

    star = layer(size)
    sdraw = ImageDraw.Draw(star)
    inner = 0.19
    vertices = []
    for index in range(8):
        angle = math.radians(90 + index * 45)
        distance = radius if index % 2 == 0 else radius * inner
        vertices.append(point(distance, angle))
    sdraw.polygon(vertices, fill=(*SPARKLE, alpha))
    # A tiny white core keeps the sparkle luminous rather than beige.
    sdraw.ellipse(
        ((cx - radius * 0.27) * S, (cy - radius * 0.27) * S,
         (cx + radius * 0.27) * S, (cy + radius * 0.27) * S),
        fill=(*WHITE, min(255, alpha + 35)),
    )
    star = star.filter(ImageFilter.GaussianBlur(0.16 * S))
    target.alpha_composite(star)


def rim_stops() -> list[tuple[float, tuple[int, int, int]]]:
    # Clockwise around the film. White/cyan on the lit upper-left, aqua and
    # lavender around the sides, warm peach at the lower-right reflection.
    return [
        (0.0, mix(LAVENDER, WHITE, 0.32)),
        (45.0 / 360.0, mix(PEACH, WHITE, 0.12)),
        (90.0 / 360.0, mix(PEACH, LAVENDER, 0.52)),
        (135.0 / 360.0, mix(AQUA, LAVENDER, 0.34)),
        (180.0 / 360.0, mix(AQUA, WHITE, 0.12)),
        (225.0 / 360.0, WHITE),
        (270.0 / 360.0, mix(WHITE, CYAN, 0.48)),
        (315.0 / 360.0, mix(CYAN, LAVENDER, 0.42)),
        (360.0, mix(LAVENDER, WHITE, 0.32)),
    ]


# ---------------------------------------------------------------------------
# Soap-bubble painting


def paint_bubble(target: Image.Image, *, cx: float, cy: float, rx: float,
                 ry: float, rotation: float, phase: float,
                 highlight: tuple[float, float, float, float, float],
                 sparkles: Iterable[tuple[float, float, float, float]]
                 ) -> None:
    """Paint one translucent soap bubble into an RGBA high-res canvas."""

    size = (target.width // S, target.height // S)
    large = max(rx, ry) >= 10.0
    wobble = 0.0065 if large else 0.010
    outer = body_mask(
        size, cx, cy, rx, ry,
        rotation=rotation, phase=phase, wobble=wobble,
    )
    inner_rim = body_mask(
        size, cx, cy, rx, ry, inset=2.35,
        rotation=rotation, phase=phase, wobble=wobble,
    )
    wide_rim = body_mask(
        size, cx, cy, rx, ry, inset=5.1 if large else 3.7,
        rotation=rotation, phase=phase, wobble=wobble,
    )

    # ---- soft atmospheric halo -------------------------------------------------
    halo = soft_mask(outer, 2.0 if large else 1.25)
    halo = ImageChops.multiply(halo, outer.point(lambda value: 255))
    halo_colour = vertical_gradient(
        size,
        [(0.0, mix(CYAN, WHITE, 0.20)),
         (0.50, mix(CYAN, LAVENDER, 0.45)),
         (1.0, mix(PEACH, LAVENDER, 0.35))],
    )
    target.alpha_composite(colour_alpha(halo_colour, halo, 36 if large else 31))

    # A separate, barely-there lower-right bloom gives the bubble some weight.
    lower = layer(size)
    lower_draw = ImageDraw.Draw(lower)
    lower_draw.ellipse(
        ((cx - rx * 0.78) * S, (cy - ry * 0.10) * S,
         (cx + rx * 0.96) * S, (cy + ry * 1.16) * S),
        fill=(*mix(LAVENDER, PEACH, 0.42), 30),
    )
    lower = lower.filter(ImageFilter.GaussianBlur((2.7 if large else 1.6) * S))
    lower = clipped(lower, outer)
    target.alpha_composite(lower)

    # ---- transparent luminous interior ----------------------------------------
    target.alpha_composite(colour_alpha(WHITE, outer, 23 if large else 19))
    radial = ImageChops.multiply(outer, radial_mask(size, cx, cy, rx, ry))
    interior_tint = vertical_gradient(
        size,
        [(0.0, mix(CYAN, WHITE, 0.50)),
         (0.45, mix(CYAN, LAVENDER, 0.48)),
         (0.75, mix(LAVENDER, WHITE, 0.18)),
         (1.0, mix(PEACH, LAVENDER, 0.34))],
    )
    target.alpha_composite(colour_alpha(interior_tint, radial, 47 if large else 40))

    film_colour = angular_colour(size, (cx, cy), rim_stops())

    # Wide inner film glow, then the readable rim, then the wet highlight edge.
    soft_rim = ImageChops.subtract(outer, wide_rim)
    soft_rim = ImageChops.multiply(soft_mask(soft_rim, 0.75), outer)
    target.alpha_composite(colour_alpha(film_colour, soft_rim, 48))

    rim = ImageChops.subtract(outer, inner_rim)
    rim = rim.filter(ImageFilter.GaussianBlur(0.18 * S))
    target.alpha_composite(colour_alpha(film_colour, rim, 232))

    # A crisp ice-white outer pinline catches the light before the deeper
    # inner rim begins, so the edge reads as luminous glass rather than ink.
    bright_outer = ImageChops.subtract(outer, body_mask(
        size, cx, cy, rx, ry, inset=1.16,
        rotation=rotation, phase=phase, wobble=wobble,
    ))
    bright_outer = ImageChops.multiply(bright_outer, outer)
    bright_outer = bright_outer.filter(ImageFilter.GaussianBlur(0.12 * S))
    bright_tint = vertical_gradient(
        size,
        [(0.0, mix(WHITE, CYAN, 0.12)),
         (0.62, mix(WHITE, CYAN, 0.38)),
         (1.0, mix(WHITE, LAVENDER, 0.22))],
    )
    target.alpha_composite(colour_alpha(bright_tint, bright_outer, 232))

    # A deeper blue inner rim gives the translucent film an unmistakable edge
    # on the pale sky. It stays inside the existing silhouette, so the visible
    # bubble never grows past its transparent safe margin.
    deep_rim = ImageChops.subtract(
        body_mask(
            size, cx, cy, rx, ry, inset=1.10,
            rotation=rotation, phase=phase, wobble=wobble,
        ),
        body_mask(
            size, cx, cy, rx, ry, inset=3.35,
            rotation=rotation, phase=phase, wobble=wobble,
        ),
    )
    deep_rim = ImageChops.multiply(deep_rim, outer)
    deep_rim = deep_rim.filter(ImageFilter.GaussianBlur(0.22 * S))
    deep_tint = vertical_gradient(
        size,
        [(0.0, mix(CYAN, PERI_BLUE, 0.50)),
         (0.52, mix(PERI_BLUE, BLUE_RIM, 0.46)),
         (1.0, mix(BLUE_RIM, LAVENDER, 0.16))],
    )
    target.alpha_composite(colour_alpha(deep_tint, deep_rim, 150))

    edge = ImageChops.subtract(outer, body_mask(
        size, cx, cy, rx, ry, inset=0.72,
        rotation=rotation, phase=phase, wobble=wobble,
    ))
    edge = edge.filter(ImageFilter.GaussianBlur(0.10 * S))
    pale_film = Image.blend(
        film_colour,
        Image.new("RGB", film_colour.size, WHITE),
        0.52,
    )
    target.alpha_composite(colour_alpha(pale_film, edge, 216))

    # ---- lower-right lavender / peach reflection ------------------------------
    reflection = layer(size)
    rdraw = ImageDraw.Draw(reflection)
    width = (2.2 if large else 1.8) * S
    bbox_outer = (
        (cx - rx * 0.86) * S, (cy - ry * 0.86) * S,
        (cx + rx * 0.86) * S, (cy + ry * 0.86) * S,
    )
    bbox_inner = (
        (cx - rx * 0.79) * S, (cy - ry * 0.79) * S,
        (cx + rx * 0.79) * S, (cy + ry * 0.79) * S,
    )
    rdraw.arc(bbox_outer, 18, 105, fill=(*DEEP_SHADOW, 58), width=round(width * 1.4))
    rdraw.arc(bbox_outer, 20, 102, fill=(*BLUE_RIM, 34), width=round(width * 1.05))
    rdraw.arc(bbox_outer, 22, 99, fill=(*PEACH, 150), width=round(width))
    rdraw.arc(bbox_inner, 38, 121, fill=(*LAVENDER, 140), width=round(width * 1.05))
    # A short warm glint on the inside of the lower-right rim.
    add_rotated_oval(
        reflection,
        cx + rx * 0.34, cy + ry * 0.67,
        (2.1 if large else 1.6), 0.72,
        math.degrees(rotation) - 23.0,
        mix(PEACH, WHITE, 0.62), 135, blur=0.25,
    )
    reflection = clipped(reflection, outer)
    reflection = reflection.filter(ImageFilter.GaussianBlur(0.32 * S))
    target.alpha_composite(reflection)

    # ---- upper-left curved sheen and crisp specular highlight ------------------
    curve = layer(size)
    cdraw = ImageDraw.Draw(curve)
    cdraw.arc(
        ((cx - rx * 0.82) * S, (cy - ry * 0.82) * S,
         (cx + rx * 0.82) * S, (cy + ry * 0.82) * S),
        203, 259,
        fill=(*WHITE, 118 if large else 102),
        width=round((1.35 if large else 1.05) * S),
    )
    curve = clipped(curve, outer)
    curve = curve.filter(ImageFilter.GaussianBlur(0.34 * S))
    target.alpha_composite(curve)

    hx, hy, hrx, hry, hrot = highlight
    # Broad bloom under the hard highlight.
    bloom = layer(size)
    bdraw = ImageDraw.Draw(bloom)
    bdraw.polygon(
        rotated_ellipse_points(hx, hy, hrx * 1.75, hry * 1.90, hrot),
        fill=(*WHITE, 52),
    )
    bloom = bloom.filter(ImageFilter.GaussianBlur((1.7 if large else 1.2) * S))
    bloom = clipped(bloom, outer)
    target.alpha_composite(bloom)

    glint = layer(size)
    gdraw = ImageDraw.Draw(glint)
    gdraw.polygon(
        rotated_ellipse_points(hx, hy, hrx, hry, hrot),
        fill=(*WHITE, 226),
    )
    # Secondary pin-point moves with the highlight, like light on wet film.
    gdraw.polygon(
        rotated_ellipse_points(
            hx + hrx * 0.98, hy + hry * 1.10,
            hrx * 0.25, hry * 0.40, hrot,
        ),
        fill=(*WHITE, 172),
    )
    glint = glint.filter(ImageFilter.GaussianBlur(0.22 * S))
    glint = clipped(glint, outer)
    target.alpha_composite(glint)

    # Faint iridescent side light: stops the body reading as an empty ring.
    side = layer(size)
    sdraw = ImageDraw.Draw(side)
    sdraw.arc(
        ((cx - rx * 0.65) * S, (cy - ry * 0.65) * S,
         (cx + rx * 0.65) * S, (cy + ry * 0.65) * S),
        118, 171,
        fill=(*mix(CYAN, WHITE, 0.35), 57),
        width=round((1.1 if large else 0.9) * S),
    )
    side = clipped(side, outer)
    side = side.filter(ImageFilter.GaussianBlur(0.65 * S))
    target.alpha_composite(side)

    # ---- tiny warm-white sparkles ---------------------------------------------
    for sx, sy, sr, srot in sparkles:
        add_sparkle(target, sx, sy, sr, srot, alpha=210 if large else 195)


def render_bubble(index: int) -> Image.Image:
    key = BUBBLE_KEYS[index]
    target = layer((64, 64))
    paint_bubble(
        target,
        cx=key["cx"], cy=key["cy"], rx=key["rx"], ry=key["ry"],
        rotation=key["rot"], phase=key["phase"],
        highlight=key["hi"],
        sparkles=(
            key["spark_a"],
            key["spark_b"],
            # A very small third glint, kept inside the upper-right quadrant.
            (49.0, 30.8, 0.85, 28.0),
        ),
    )
    return target


def render_trail(index: int) -> Image.Image:
    key = TRAIL_KEYS[index]
    target = layer((60, 24))
    paint_bubble(
        target,
        cx=key["cx"], cy=key["cy"], rx=key["rx"], ry=key["ry"],
        rotation=key["rot"], phase=key["phase"],
        highlight=key["hi"],
        sparkles=(key["spark"],),
    )
    return target


# ---------------------------------------------------------------------------
# Assembly


def compose_sheet() -> Image.Image:
    sheet = Image.new("RGBA", (SHEET_W * S, SHEET_H * S), (255, 255, 255, 0))
    for index, (name, x, y, width, height, kind) in enumerate(FRAMES):
        if kind == "idle":
            frame = render_bubble(index)
        else:
            frame = render_trail(index - 4)
        if frame.size != (width * S, height * S):
            raise RuntimeError(
                f"{name}: rendered {frame.size}, expected {(width * S, height * S)}"
            )
        sheet.alpha_composite(frame, (x * S, y * S))
    return sheet.resize((SHEET_W, SHEET_H), Image.Resampling.LANCZOS)


def finalize(image: Image.Image, margin: int = 2) -> Image.Image:
    """Guarantee the promised transparent margin and clean hidden RGB.

    A tiny amount of sub-1%-alpha halo is allowed to paint outside the visual
    bubble so the edge feels airy. The final pass trims that at the requested
    transparent margin, then makes every fully transparent pixel white. White
    hidden colour is important for a texture that will be GPU-scaled: it stops
    transparent texels producing a dark fringe around the bubble.
    """

    keep = Image.new("L", image.size, 0)
    keep_draw = ImageDraw.Draw(keep)
    for _name, x, y, width, height, _kind in FRAMES:
        keep_draw.rectangle(
            (x + margin, y + margin, x + width - margin - 1, y + height - margin - 1),
            fill=255,
        )
    alpha = ImageChops.multiply(image.getchannel("A"), keep)

    rgb = image.convert("RGB")
    clear = alpha.point(lambda value: 255 if value == 0 else 0)
    rgb.paste(WHITE, (0, 0), clear)
    return Image.merge("RGBA", (*rgb.split(), alpha))


def main() -> None:
    image = finalize(compose_sheet())
    if image.mode != "RGBA" or image.size != (SHEET_W, SHEET_H):
        raise RuntimeError(f"Unexpected output format: {image.mode} {image.size}")
    image.save(OUTPUT, format="PNG", compress_level=9, optimize=False)
    print(f"Wrote {OUTPUT} ({image.width}x{image.height}, RGBA)")


if __name__ == "__main__":
    main()'''

POP_RENDERER = r'''#!/usr/bin/env python3
"""Deterministic renderer for the eight 64 x 64 bubble-pop frames.

The frames continue the dreamy soap-bubble language of the idle ball: an
iridescent white / cyan / lavender film rim, a deeper blue inner edge, crisp
white specular highlights, warm-white sparkles, and a translucent centre. The
burst is drawn at 4x and reduced with LANCZOS, so it stays smooth and reads as
broad shapes at the 32 x 32 game size. Nothing here is random or loaded from
disk; the sequence is a fixed procedural recipe.

Frame order:
  1 swollen intact bubble, bright rim swell
  2 rim cracks, first arcs separate
  3 arcs pull apart, small droplets appear
  4 expanding ring, droplets move out
  5 thinner ring, droplets beyond the original bubble
  6 ring dissipates, extra sparkles
  7 last droplets and sparkles
  8 faint sparkle residue
"""

from __future__ import annotations

import math
from typing import Sequence

from PIL import Image, ImageChops, ImageDraw, ImageFilter

FRAME_W, FRAME_H = 64, 64
S = 4  # supersampling factor
WHITE = (247, 254, 255)
CYAN = (143, 233, 255)
AQUA = (94, 214, 255)
LAVENDER = (205, 185, 255)
PEACH = (255, 214, 232)
DEEP_SHADOW = (60, 127, 181)
BLUE_RIM = (46, 127, 184)
PERI_BLUE = (94, 127, 184)
SPARKLE = (255, 246, 201)


def layer() -> Image.Image:
    return Image.new("RGBA", (FRAME_W * S, FRAME_H * S), (255, 255, 255, 0))


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lerp_stops(stops: Sequence[tuple[float, tuple[int, int, int]]],
               position: float) -> tuple[int, int, int]:
    position = position % 1.0
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= position <= p1:
            span = p1 - p0
            return mix(c0, c1, 0.0 if span == 0 else (position - p0) / span)
    return stops[-1][1]


def rim_stops() -> list[tuple[float, tuple[int, int, int]]]:
    return [
        (0.0, mix(LAVENDER, WHITE, 0.32)),
        (45.0 / 360.0, mix(PEACH, WHITE, 0.12)),
        (90.0 / 360.0, mix(PEACH, LAVENDER, 0.52)),
        (135.0 / 360.0, mix(AQUA, LAVENDER, 0.34)),
        (180.0 / 360.0, mix(AQUA, WHITE, 0.12)),
        (225.0 / 360.0, WHITE),
        (270.0 / 360.0, mix(WHITE, CYAN, 0.48)),
        (315.0 / 360.0, mix(CYAN, LAVENDER, 0.42)),
        (360.0, mix(LAVENDER, WHITE, 0.32)),
    ]


def angular_colour(centre: tuple[float, float] = (32.0, 32.0)) -> Image.Image:
    width, height = FRAME_W * S, FRAME_H * S
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)
    cx, cy = centre[0] * S, centre[1] * S
    radius = math.hypot(width, height) * 1.1
    bounds = (cx - radius, cy - radius, cx + radius, cy + radius)
    stops = rim_stops()
    steps = 720
    for index in range(steps):
        start = index * 360.0 / steps
        end = (index + 1) * 360.0 / steps + 0.55
        colour = lerp_stops(stops, ((start + end) * 0.5 % 360.0) / 360.0)
        draw.pieslice(bounds, start, end, fill=colour)
    return image.filter(ImageFilter.GaussianBlur(0.9 * S))


def colour_alpha(colour: tuple[int, int, int] | Image.Image, mask: Image.Image,
                 opacity: int = 255) -> Image.Image:
    if isinstance(colour, tuple):
        rgb = Image.new("RGB", mask.size, colour)
    else:
        rgb = colour.convert("RGB")
    if opacity != 255:
        mask = mask.point(lambda value: (value * opacity + 127) // 255)
    return Image.merge("RGBA", (*rgb.split(), mask))


def soft_mask(mask: Image.Image, final_radius: float) -> Image.Image:
    return mask.filter(ImageFilter.GaussianBlur(final_radius * S))


def ellipse_mask(cx: float, cy: float, rx: float, ry: float, *,
                 inset: float = 0.0, rotation: float = 0.0,
                 phase: float = 0.0, wobble: float = 0.0) -> Image.Image:
    mask = Image.new("L", (FRAME_W * S, FRAME_H * S), 0)
    draw = ImageDraw.Draw(mask)
    points = []
    radians = math.radians(rotation)
    cos_r, sin_r = math.cos(radians), math.sin(radians)
    actual_rx = max(0.15, rx - inset)
    actual_ry = max(0.15, ry - inset)
    count = 720
    for index in range(count):
        theta = math.tau * index / count
        ripple = 1.0
        if wobble:
            ripple += wobble * (
                0.62 * math.sin(3.0 * theta + phase)
                + 0.38 * math.sin(5.0 * theta + phase * 1.7 + 0.8)
            )
        x = actual_rx * math.cos(theta) * ripple
        y = actual_ry * math.sin(theta) * ripple
        xr = x * cos_r - y * sin_r
        yr = x * sin_r + y * cos_r
        points.append(((cx + xr) * S, (cy + yr) * S))
    draw.polygon(points, fill=255)
    return mask


def clipped(image: Image.Image, mask: Image.Image) -> Image.Image:
    result = image.copy()
    result.putalpha(ImageChops.multiply(result.getchannel("A"), mask))
    return result


def radial_mask(cx: float, cy: float, rx: float, ry: float) -> Image.Image:
    target = Image.new("L", (FRAME_W * S, FRAME_H * S), 0)
    width = max(2, round(2 * rx * S))
    height = max(2, round(2 * ry * S))
    gradient = Image.radial_gradient("L").resize(
        (width, height), Image.Resampling.BILINEAR
    ).point(lambda value: min(255, round(value * 255 / 181)))
    target.paste(gradient, (round((cx - rx) * S), round((cy - ry) * S)))
    return target


def rotated_ellipse_points(cx: float, cy: float, rx: float, ry: float,
                           rotation: float) -> list[tuple[float, float]]:
    radians = math.radians(rotation)
    cos_r, sin_r = math.cos(radians), math.sin(radians)
    points = []
    for index in range(180):
        theta = math.tau * index / 180
        x = rx * math.cos(theta)
        y = ry * math.sin(theta)
        points.append((
            (cx + x * cos_r - y * sin_r) * S,
            (cy + x * sin_r + y * cos_r) * S,
        ))
    return points


def add_rotated_oval(target: Image.Image, cx: float, cy: float, rx: float,
                     ry: float, rotation: float, colour: tuple[int, int, int],
                     alpha: int = 255, blur: float = 0.0) -> None:
    local = layer()
    draw = ImageDraw.Draw(local)
    draw.polygon(rotated_ellipse_points(cx, cy, rx, ry, rotation),
                 fill=(*colour, alpha))
    if blur:
        local = local.filter(ImageFilter.GaussianBlur(blur * S))
    target.alpha_composite(local)


def add_sparkle(target: Image.Image, cx: float, cy: float, radius: float,
                rotation: float = 0.0, alpha: int = 215) -> None:
    radians = math.radians(rotation)
    cos_r, sin_r = math.cos(radians), math.sin(radians)

    def point(distance: float, angle: float) -> tuple[float, float]:
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        return ((cx + x * cos_r - y * sin_r) * S,
                (cy + x * sin_r + y * cos_r) * S)

    halo = layer()
    hdraw = ImageDraw.Draw(halo)
    hdraw.ellipse(
        ((cx - radius * 2.15) * S, (cy - radius * 2.15) * S,
         (cx + radius * 2.15) * S, (cy + radius * 2.15) * S),
        fill=(*SPARKLE, min(255, round(alpha * 0.21))),
    )
    halo = halo.filter(ImageFilter.GaussianBlur(max(0.5, radius * 1.15) * S))
    target.alpha_composite(halo)

    star = layer()
    sdraw = ImageDraw.Draw(star)
    inner = 0.19
    vertices = []
    for index in range(8):
        angle = math.radians(90 + index * 45)
        distance = radius if index % 2 == 0 else radius * inner
        vertices.append(point(distance, angle))
    sdraw.polygon(vertices, fill=(*SPARKLE, alpha))
    sdraw.ellipse(
        ((cx - radius * 0.27) * S, (cy - radius * 0.27) * S,
         (cx + radius * 0.27) * S, (cy + radius * 0.27) * S),
        fill=(*WHITE, min(255, alpha + 35)),
    )
    star = star.filter(ImageFilter.GaussianBlur(0.16 * S))
    target.alpha_composite(star)


def add_droplet(target: Image.Image, cx: float, cy: float, radius: float,
                colour: tuple[int, int, int], alpha: int = 225) -> None:
    halo = layer()
    hdraw = ImageDraw.Draw(halo)
    hdraw.ellipse(
        ((cx - radius * 2.2) * S, (cy - radius * 2.2) * S,
         (cx + radius * 2.2) * S, (cy + radius * 2.2) * S),
        fill=(*mix(colour, WHITE, 0.35), 54),
    )
    halo = halo.filter(ImageFilter.GaussianBlur(max(0.55, radius * 1.0) * S))
    target.alpha_composite(halo)

    drop = layer()
    ddraw = ImageDraw.Draw(drop)
    bbox = ((cx - radius) * S, (cy - radius) * S,
            (cx + radius) * S, (cy + radius) * S)
    ddraw.ellipse(bbox, fill=(*colour, alpha),
                  outline=(*BLUE_RIM, min(255, round(alpha * 0.45))),
                  width=max(1, round(0.7 * S)))
    ddraw.ellipse(
        ((cx - radius * 0.66) * S, (cy - radius * 0.72) * S,
         (cx - radius * 0.02) * S, (cy - radius * 0.08) * S),
        fill=(*WHITE, min(255, round(alpha * 0.92))),
    )
    drop = drop.filter(ImageFilter.GaussianBlur(0.12 * S))
    target.alpha_composite(drop)


def add_flash(target: Image.Image, cx: float, cy: float, radius: float,
              alpha: int = 180, rays: bool = True) -> None:
    halo = layer()
    hdraw = ImageDraw.Draw(halo)
    hdraw.ellipse(
        ((cx - radius * 2.4) * S, (cy - radius * 2.4) * S,
         (cx + radius * 2.4) * S, (cy + radius * 2.4) * S),
        fill=(*mix(SPARKLE, CYAN, 0.32), min(255, round(alpha * 0.28))),
    )
    if rays:
        ray_layer = layer()
        rdraw = ImageDraw.Draw(ray_layer)
        for angle_deg in (35.0, 125.0, 215.0, 305.0):
            angle = math.radians(angle_deg)
            inner = radius * 0.75
            outer = radius * 1.95
            half = max(0.30, radius * 0.09)
            ux, uy = math.cos(angle), math.sin(angle)
            px, py = -uy, ux
            poly = [
                ((cx + ux * inner + px * half) * S, (cy + uy * inner + py * half) * S),
                ((cx + ux * outer) * S, (cy + uy * outer) * S),
                ((cx + ux * inner - px * half) * S, (cy + uy * inner - py * half) * S),
            ]
            rdraw.polygon(poly, fill=(*mix(WHITE, CYAN, 0.18), min(255, round(alpha * 0.55))))
        ray_layer = ray_layer.filter(ImageFilter.GaussianBlur(0.18 * S))
        halo.alpha_composite(ray_layer)
    halo = halo.filter(ImageFilter.GaussianBlur(max(0.55, radius * 0.40) * S))
    target.alpha_composite(halo)

    star = layer()
    sdraw = ImageDraw.Draw(star)
    vertices = []
    for index in range(8):
        angle = math.radians(90 + index * 45)
        distance = radius if index % 2 == 0 else radius * 0.22
        vertices.append(((cx + distance * math.cos(angle)) * S,
                         (cy + distance * math.sin(angle)) * S))
    sdraw.polygon(vertices, fill=(*SPARKLE, alpha))
    sdraw.ellipse(
        ((cx - radius * 0.30) * S, (cy - radius * 0.30) * S,
         (cx + radius * 0.30) * S, (cy + radius * 0.30) * S),
        fill=(*WHITE, min(255, alpha + 45)),
    )
    star = star.filter(ImageFilter.GaussianBlur(0.14 * S))
    target.alpha_composite(star)


def arc_mask(cx: float, cy: float, rx: float, ry: float, start: float,
             end: float, thickness: float) -> Image.Image:
    mask = Image.new("L", (FRAME_W * S, FRAME_H * S), 0)
    draw = ImageDraw.Draw(mask)
    bbox = ((cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S)
    width = max(1, round(thickness * S))
    draw.arc(bbox, start, end, fill=255, width=width)
    mid_rx = max(0.1, rx - thickness * 0.5)
    mid_ry = max(0.1, ry - thickness * 0.5)
    cap = thickness * 0.5
    for angle_deg in (start, end):
        angle = math.radians(angle_deg)
        px = cx + mid_rx * math.cos(angle)
        py = cy + mid_ry * math.sin(angle)
        draw.ellipse(((px - cap) * S, (py - cap) * S,
                      (px + cap) * S, (py + cap) * S), fill=255)
    return mask


def paint_arc(target: Image.Image, film: Image.Image, cx: float, cy: float,
              rx: float, ry: float, start: float, end: float,
              thickness: float, alpha: int = 232, glow: bool = True,
              deep: bool = True, bright: bool = True) -> None:
    mask = arc_mask(cx, cy, rx, ry, start, end, thickness)
    if glow:
        glow_mask = arc_mask(cx, cy, rx + 0.35, ry + 0.35, start, end,
                             thickness + 1.7)
        glow_mask = soft_mask(glow_mask, 0.85)
        target.alpha_composite(colour_alpha(mix(CYAN, LAVENDER, 0.45),
                                            glow_mask, 42))
    target.alpha_composite(colour_alpha(film, mask, alpha))
    if bright:
        outer = arc_mask(cx, cy, rx, ry, start, end, min(0.85, thickness * 0.42))
        pale = Image.new("RGB", (FRAME_W * S, FRAME_H * S), mix(WHITE, CYAN, 0.20))
        target.alpha_composite(colour_alpha(pale, outer, min(255, alpha + 8)))
    if deep and thickness > 0.9:
        inner_r = max(0.3, rx - thickness + 0.55)
        inner_mask = arc_mask(cx, cy, inner_r, max(0.25, ry - thickness + 0.55),
                              start, end, min(0.85, thickness * 0.36))
        deep_tint = Image.new("RGB", (FRAME_W * S, FRAME_H * S),
                              mix(PERI_BLUE, BLUE_RIM, 0.48))
        target.alpha_composite(colour_alpha(deep_tint, inner_mask, 118))


def paint_intact(target: Image.Image, film: Image.Image, *,
                 cx: float, cy: float, rx: float, ry: float,
                 rotation: float, phase: float,
                 highlight: tuple[float, float, float, float, float],
                 swell: bool = False) -> None:
    wobble = 0.0055
    outer = ellipse_mask(cx, cy, rx, ry, rotation=rotation, phase=phase,
                         wobble=wobble)
    inner_rim = ellipse_mask(cx, cy, rx, ry, inset=2.35, rotation=rotation,
                             phase=phase, wobble=wobble)
    wide_rim = ellipse_mask(cx, cy, rx, ry, inset=5.0, rotation=rotation,
                            phase=phase, wobble=wobble)

    # Airy outer bloom. The swell frame gets a brighter halo just beyond the
    # silhouette, which reads as the film stretching before it breaks.
    halo = soft_mask(outer, 2.1)
    target.alpha_composite(colour_alpha(mix(CYAN, LAVENDER, 0.44), halo,
                                        34 if swell else 28))
    if swell:
        outer_halo = ellipse_mask(cx, cy, rx + 1.7, ry + 1.7, rotation=rotation,
                                  phase=phase, wobble=wobble)
        ring = ImageChops.subtract(outer_halo, outer)
        ring = soft_mask(ring, 0.55)
        target.alpha_composite(colour_alpha(mix(WHITE, CYAN, 0.22), ring, 82))

    lower = layer()
    lower_draw = ImageDraw.Draw(lower)
    lower_draw.ellipse(
        ((cx - rx * 0.78) * S, (cy - ry * 0.10) * S,
         (cx + rx * 0.96) * S, (cy + ry * 1.16) * S),
        fill=(*mix(LAVENDER, PEACH, 0.42), 30),
    )
    lower = lower.filter(ImageFilter.GaussianBlur(2.7 * S))
    lower = clipped(lower, outer)
    target.alpha_composite(lower)

    target.alpha_composite(colour_alpha(WHITE, outer, 23))
    radial = ImageChops.multiply(outer, radial_mask(cx, cy, rx, ry))
    interior_tint = Image.new("RGB", (FRAME_W * S, FRAME_H * S),
                              mix(CYAN, LAVENDER, 0.48))
    target.alpha_composite(colour_alpha(interior_tint, radial, 42))

    soft_rim = ImageChops.subtract(outer, wide_rim)
    soft_rim = ImageChops.multiply(soft_mask(soft_rim, 0.75), outer)
    target.alpha_composite(colour_alpha(film, soft_rim, 46))

    rim = ImageChops.subtract(outer, inner_rim)
    rim = rim.filter(ImageFilter.GaussianBlur(0.18 * S))
    target.alpha_composite(colour_alpha(film, rim, 232))

    bright_outer = ImageChops.subtract(outer, ellipse_mask(
        cx, cy, rx, ry, inset=1.05, rotation=rotation, phase=phase,
        wobble=wobble,
    ))
    bright_outer = ImageChops.multiply(bright_outer, outer)
    bright_outer = bright_outer.filter(ImageFilter.GaussianBlur(0.12 * S))
    target.alpha_composite(colour_alpha(
        mix(WHITE, CYAN, 0.30), bright_outer, 236,
    ))

    deep_rim = ImageChops.subtract(
        ellipse_mask(cx, cy, rx, ry, inset=1.10, rotation=rotation,
                     phase=phase, wobble=wobble),
        ellipse_mask(cx, cy, rx, ry, inset=3.35, rotation=rotation,
                     phase=phase, wobble=wobble),
    )
    deep_rim = ImageChops.multiply(deep_rim, outer)
    deep_rim = deep_rim.filter(ImageFilter.GaussianBlur(0.22 * S))
    target.alpha_composite(colour_alpha(
        mix(PERI_BLUE, BLUE_RIM, 0.50), deep_rim, 158,
    ))

    edge = ImageChops.subtract(outer, ellipse_mask(
        cx, cy, rx, ry, inset=0.72, rotation=rotation, phase=phase,
        wobble=wobble,
    ))
    edge = edge.filter(ImageFilter.GaussianBlur(0.10 * S))
    pale_film = Image.blend(film, Image.new("RGB", film.size, WHITE), 0.52)
    target.alpha_composite(colour_alpha(pale_film, edge, 216))

    reflection = layer()
    rdraw = ImageDraw.Draw(reflection)
    width = 2.2 * S
    bbox_outer = ((cx - rx * 0.86) * S, (cy - ry * 0.86) * S,
                  (cx + rx * 0.86) * S, (cy + ry * 0.86) * S)
    bbox_inner = ((cx - rx * 0.79) * S, (cy - ry * 0.79) * S,
                  (cx + rx * 0.79) * S, (cy + ry * 0.79) * S)
    rdraw.arc(bbox_outer, 18, 105, fill=(*DEEP_SHADOW, 58), width=round(width * 1.4))
    rdraw.arc(bbox_outer, 20, 102, fill=(*BLUE_RIM, 34), width=round(width * 1.05))
    rdraw.arc(bbox_outer, 22, 99, fill=(*PEACH, 150), width=round(width))
    rdraw.arc(bbox_inner, 38, 121, fill=(*LAVENDER, 140), width=round(width * 1.05))
    add_rotated_oval(reflection, cx + rx * 0.34, cy + ry * 0.67, 2.1, 0.72,
                     math.degrees(rotation) - 23.0, mix(PEACH, WHITE, 0.62),
                     135, blur=0.25)
    reflection = clipped(reflection, outer)
    reflection = reflection.filter(ImageFilter.GaussianBlur(0.32 * S))
    target.alpha_composite(reflection)

    curve = layer()
    cdraw = ImageDraw.Draw(curve)
    cdraw.arc(
        ((cx - rx * 0.82) * S, (cy - ry * 0.82) * S,
         (cx + rx * 0.82) * S, (cy + ry * 0.82) * S),
        203, 259, fill=(*WHITE, 118), width=round(1.35 * S),
    )
    curve = clipped(curve, outer)
    curve = curve.filter(ImageFilter.GaussianBlur(0.34 * S))
    target.alpha_composite(curve)

    hx, hy, hrx, hry, hrot = highlight
    bloom = layer()
    bdraw = ImageDraw.Draw(bloom)
    bdraw.polygon(rotated_ellipse_points(hx, hy, hrx * 1.75, hry * 1.90, hrot),
                  fill=(*WHITE, 52))
    bloom = bloom.filter(ImageFilter.GaussianBlur(1.7 * S))
    bloom = clipped(bloom, outer)
    target.alpha_composite(bloom)

    glint = layer()
    gdraw = ImageDraw.Draw(glint)
    gdraw.polygon(rotated_ellipse_points(hx, hy, hrx, hry, hrot),
                  fill=(*WHITE, 226))
    gdraw.polygon(rotated_ellipse_points(
        hx + hrx * 0.98, hy + hry * 1.10, hrx * 0.25, hry * 0.40, hrot,
    ), fill=(*WHITE, 172))
    glint = glint.filter(ImageFilter.GaussianBlur(0.22 * S))
    glint = clipped(glint, outer)
    target.alpha_composite(glint)


def polar(angle_deg: float, distance: float) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    return 32.0 + math.cos(angle) * distance, 32.0 + math.sin(angle) * distance


def render_frame(index: int) -> Image.Image:
    target = layer()
    film = angular_colour()

    if index == 0:
        paint_intact(
            target, film, cx=32.0, cy=32.0, rx=28.25, ry=27.20,
            rotation=-0.6, phase=0.4,
            highlight=(21.6, 20.3, 4.85, 2.00, -36.0),
            swell=True,
        )
        add_sparkle(target, 47.6, 18.6, 2.25, 8.0, 210)
        add_sparkle(target, 15.4, 45.6, 1.30, -12.0, 195)
        add_sparkle(target, 49.0, 30.8, 0.85, 28.0, 160)
        add_flash(target, 48.4, 17.2, 1.55, alpha=115, rays=False)

    elif index == 1:
        for i, (rx, ry, start, end, thick) in enumerate((
            (28.50, 27.55, 14.0, 76.0, 2.75),
            (27.55, 26.90, 92.0, 157.0, 2.60),
            (28.80, 27.35, 170.0, 232.0, 2.45),
            (27.25, 26.55, 246.0, 303.0, 2.55),
            (28.35, 27.20, 315.0, 351.0, 2.25),
        )):
            paint_arc(target, film, 32.0, 32.0, rx, ry, start, end, thick,
                      alpha=232 if i != 4 else 220)
        # Detached rim flecks and the first freed droplets.
        paint_arc(target, film, 32.0, 32.0, 24.80, 24.10, 54.0, 62.0, 1.65,
                  alpha=205, glow=False, deep=False)
        paint_arc(target, film, 32.0, 32.0, 25.60, 24.80, 120.0, 127.0, 1.45,
                  alpha=195, glow=False, deep=False)
        paint_arc(target, film, 32.0, 32.0, 24.40, 23.90, 250.0, 257.0, 1.40,
                  alpha=190, glow=False, deep=False)
        add_droplet(target, 53.2, 39.4, 1.80, mix(CYAN, WHITE, 0.25), 225)
        add_droplet(target, 35.8, 27.2, 1.00, mix(LAVENDER, WHITE, 0.25), 195)
        add_flash(target, 43.8, 21.4, 4.2, alpha=215)
        add_sparkle(target, 16.2, 19.4, 1.45, 16.0, 190)
        add_sparkle(target, 46.8, 49.6, 1.05, -18.0, 170)

    elif index == 2:
        for i, (rx, ry, start, end, thick) in enumerate((
            (28.90, 27.80, 21.0, 65.0, 2.10),
            (27.45, 26.70, 84.0, 130.0, 1.95),
            (29.00, 27.90, 149.0, 192.0, 2.00),
            (26.95, 26.25, 212.0, 248.0, 1.85),
            (28.65, 27.50, 269.0, 316.0, 1.95),
            (27.55, 26.60, 333.0, 353.0, 1.75),
        )):
            paint_arc(target, film, 32.0, 32.0, rx, ry, start, end, thick,
                      alpha=215 if i % 2 == 0 else 195)
        paint_arc(target, film, 32.0, 32.0, 25.20, 24.40, 70.0, 78.0, 1.30,
                  alpha=180, glow=False, deep=False)
        paint_arc(target, film, 32.0, 32.0, 24.80, 24.10, 258.0, 266.0, 1.25,
                  alpha=170, glow=False, deep=False)
        for angle, distance, radius, colour in (
            (68.0, 26.4, 2.00, mix(PEACH, WHITE, 0.18)),
            (123.0, 26.8, 1.80, mix(LAVENDER, WHITE, 0.22)),
            (205.0, 26.2, 1.65, mix(CYAN, WHITE, 0.22)),
            (302.0, 26.6, 1.70, mix(AQUA, WHITE, 0.30)),
        ):
            dx, dy = polar(angle, distance)
            add_droplet(target, dx, dy, radius, colour, 210)
        add_flash(target, 42.8, 21.0, 3.40, alpha=180)
        add_sparkle(target, 19.2, 17.6, 1.45, 12.0, 180)
        add_sparkle(target, 48.6, 44.4, 1.05, -22.0, 165)

    elif index == 3:
        for i, (rx, ry, start, end, thick) in enumerate((
            (28.05, 27.20, 0.0, 76.0, 1.55),
            (27.35, 26.65, 92.0, 174.0, 1.45),
            (28.25, 27.35, 188.0, 260.0, 1.50),
            (27.15, 26.50, 276.0, 348.0, 1.40),
        )):
            paint_arc(target, film, 32.0, 32.0, rx, ry, start, end, thick,
                      alpha=212 if i % 2 == 0 else 200)
        for angle, distance, radius, colour in (
            (55.0, 27.0, 2.10, mix(CYAN, WHITE, 0.22)),
            (145.0, 27.2, 1.90, mix(LAVENDER, WHITE, 0.20)),
            (235.0, 26.8, 1.70, mix(PEACH, WHITE, 0.20)),
            (325.0, 27.4, 1.85, mix(AQUA, WHITE, 0.34)),
        ):
            dx, dy = polar(angle, distance)
            add_droplet(target, dx, dy, radius, colour, 220)
        add_flash(target, 32.0, 32.0, 1.30, alpha=85, rays=False)
        add_sparkle(target, 49.6, 15.8, 1.55, 18.0, 185)
        add_sparkle(target, 14.4, 48.6, 1.15, -14.0, 165)

    elif index == 4:
        for i, (rx, ry, start, end, thick) in enumerate((
            (28.40, 27.60, 5.0, 57.0, 1.20),
            (27.70, 26.90, 78.0, 132.0, 1.10),
            (28.55, 27.65, 154.0, 197.0, 1.15),
            (27.50, 26.80, 223.0, 274.0, 1.05),
            (28.30, 27.45, 300.0, 345.0, 1.10),
        )):
            paint_arc(target, film, 32.0, 32.0, rx, ry, start, end, thick,
                      alpha=180 if i % 2 == 0 else 155)
        for angle, distance, radius, colour in (
            (42.0, 27.4, 2.00, mix(CYAN, WHITE, 0.26)),
            (139.0, 27.6, 1.85, mix(LAVENDER, WHITE, 0.22)),
            (232.0, 27.0, 1.65, mix(PEACH, WHITE, 0.22)),
            (315.0, 27.8, 1.75, mix(AQUA, WHITE, 0.32)),
        ):
            dx, dy = polar(angle, distance)
            add_droplet(target, dx, dy, radius, colour, 205)
        add_sparkle(target, 49.4, 14.8, 1.60, 20.0, 180)
        add_sparkle(target, 14.8, 49.2, 1.25, -10.0, 160)

    elif index == 5:
        for rx, ry, start, end, thick, alpha in (
            (28.10, 27.30, 10.0, 63.0, 1.05, 110),
            (27.45, 26.70, 108.0, 151.0, 1.00, 95),
            (28.30, 27.40, 196.0, 244.0, 1.00, 105),
            (27.30, 26.55, 282.0, 329.0, 0.95, 90),
        ):
            paint_arc(target, film, 32.0, 32.0, rx, ry, start, end, thick,
                      alpha=alpha, glow=False, deep=False, bright=False)
        for angle, distance, radius, colour in (
            (48.0, 27.6, 1.85, mix(CYAN, WHITE, 0.30)),
            (134.0, 27.8, 1.70, mix(LAVENDER, WHITE, 0.28)),
            (226.0, 27.0, 1.50, mix(PEACH, WHITE, 0.30)),
            (318.0, 27.6, 1.60, mix(AQUA, WHITE, 0.40)),
        ):
            dx, dy = polar(angle, distance)
            add_droplet(target, dx, dy, radius, colour, 185)
        add_sparkle(target, 45.6, 18.8, 1.90, 16.0, 195)
        add_sparkle(target, 17.8, 44.2, 1.45, -18.0, 170)
        add_sparkle(target, 50.0, 50.0, 1.00, 24.0, 145)

    elif index == 6:
        for rx, ry, start, end in (
            (27.60, 26.85, 18.0, 55.0),
            (28.10, 27.25, 126.0, 158.0),
            (27.30, 26.60, 244.0, 279.0),
        ):
            paint_arc(target, film, 32.0, 32.0, rx, ry, start, end, 0.95,
                      alpha=72, glow=False, deep=False, bright=False)
        add_droplet(target, 52.2, 44.0, 1.55, mix(LAVENDER, WHITE, 0.28), 160)
        add_sparkle(target, 22.2, 22.8, 2.35, 12.0, 200)
        add_sparkle(target, 43.6, 20.6, 1.90, -16.0, 185)
        add_sparkle(target, 35.2, 47.8, 2.05, 20.0, 180)
        add_sparkle(target, 50.6, 41.4, 1.35, -8.0, 150)
        add_sparkle(target, 15.2, 36.0, 1.10, 18.0, 135)

    elif index == 7:
        # Faint residue: two warm sparkles and a couple of pale cyan specks.
        add_sparkle(target, 34.8, 28.4, 1.45, 14.0, 115)
        add_sparkle(target, 27.2, 36.6, 1.00, -18.0, 88)
        add_droplet(target, 38.6, 37.2, 0.70, mix(CYAN, WHITE, 0.48), 105)
        add_droplet(target, 30.2, 23.0, 0.55, mix(LAVENDER, WHITE, 0.50), 82)

    return target


def finalize_frame(image: Image.Image) -> Image.Image:
    out = image.resize((FRAME_W, FRAME_H), Image.Resampling.LANCZOS)
    px = out.load()
    for y in range(FRAME_H):
        for x in range(FRAME_W):
            if x < 2 or x >= FRAME_W - 2 or y < 2 or y >= FRAME_H - 2:
                px[x, y] = (255, 255, 255, 0)
            elif px[x, y][3] == 0:
                px[x, y] = (255, 255, 255, 0)
    return out'''

CLOUD_RENDERER = r'''#!/usr/bin/env python3
"""Deterministic Pillow renderer for the paddle-cloud sprite sheet.

Run from anywhere:

    python3 assets/paddle-cloud/build.py

The script writes paddle-cloud.png beside itself. There are no external
assets, no fonts, and no random calls; the sprite is a fixed procedural
recipe, rendered at 4x and LANCZOS-downsampled for clean edges.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# Fixed output layout / palette
# ---------------------------------------------------------------------------

FRAME_W = 48
FRAME_H = 360
GAP = 1
SHEET_W = FRAME_W * 2 + GAP
SHEET_H = FRAME_H
SS = 4  # supersampling factor

W = FRAME_W * SS
H = FRAME_H * SS

HERE = Path(__file__).resolve().parent
OUT_PATH = HERE / "paddle-cloud.png"

WHITE = (255, 255, 255)
ICE = (234, 249, 255)
SKY = (185, 232, 255)
LAVENDER = (216, 204, 255)
BLUSH = (255, 217, 236)
WARM = (255, 241, 184)
SHADOW = (110, 143, 199)
DEEP_OUTLINE = (94, 127, 184)  # #5E7FB8

# ---------------------------------------------------------------------------
# Small colour helpers
# ---------------------------------------------------------------------------


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def smoothstep(t: float) -> float:
    t = clamp(t)
    return t * t * (3.0 - 2.0 * t)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = clamp(t)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def rgba(color: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], int(clamp(alpha, 0, 255))


# ---------------------------------------------------------------------------
# Masks, gradients and compositing
# ---------------------------------------------------------------------------


def new_mask() -> Image.Image:
    return Image.new("L", (W, H), 0)


def alpha_mask(mask: Image.Image, alpha: int) -> Image.Image:
    alpha = int(clamp(alpha, 0, 255))
    if alpha == 255:
        return mask
    lut = [round(v * alpha / 255.0) for v in range(256)]
    return mask.point(lut)


def blurred(mask: Image.Image, radius: float) -> Image.Image:
    if radius <= 0:
        return mask
    return mask.filter(ImageFilter.GaussianBlur(radius))


def radial_mask(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    blur: float = 0.0,
) -> Image.Image:
    mask = new_mask()
    ImageDraw.Draw(mask).ellipse(
        (
            (cx - rx) * SS,
            (cy - ry) * SS,
            (cx + rx) * SS,
            (cy + ry) * SS,
        ),
        fill=255,
    )
    return blurred(mask, blur)


def rounded_mask(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    radius: float,
    blur: float = 0.0,
) -> Image.Image:
    mask = new_mask()
    ImageDraw.Draw(mask).rounded_rectangle(
        (x0 * SS, y0 * SS, x1 * SS, y1 * SS),
        radius=radius * SS,
        fill=255,
    )
    return blurred(mask, blur)


def vertical_gradient(stops: list[tuple[float, tuple[int, int, int, int]]]) -> Image.Image:
    stops = sorted(stops, key=lambda item: item[0])
    column = Image.new("RGBA", (1, H))
    pixels = column.load()
    for y in range(H):
        t = y / (H - 1)
        left, right = stops[0], stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                left, right = stops[i], stops[i + 1]
                break
        span = right[0] - left[0]
        local = 0.0 if span <= 0 else (t - left[0]) / span
        local = smoothstep(local)
        c0, c1 = left[1], right[1]
        pixels[0, y] = tuple(
            round(c0[i] + (c1[i] - c0[i]) * local) for i in range(4)
        )
    return column.resize((W, H), Image.Resampling.NEAREST)


def horizontal_gradient(stops: list[tuple[float, tuple[int, int, int, int]]]) -> Image.Image:
    stops = sorted(stops, key=lambda item: item[0])
    row = Image.new("RGBA", (W, 1))
    pixels = row.load()
    for x in range(W):
        t = x / (W - 1)
        left, right = stops[0], stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                left, right = stops[i], stops[i + 1]
                break
        span = right[0] - left[0]
        local = 0.0 if span <= 0 else (t - left[0]) / span
        local = smoothstep(local)
        c0, c1 = left[1], right[1]
        pixels[x, 0] = tuple(
            round(c0[i] + (c1[i] - c0[i]) * local) for i in range(4)
        )
    return row.resize((W, H), Image.Resampling.NEAREST)


def composite_color(
    base: Image.Image,
    color: tuple[int, int, int],
    mask: Image.Image,
    alpha: int = 255,
    blur: float = 0.0,
) -> None:
    m = alpha_mask(mask, alpha)
    if blur:
        m = blurred(m, blur)
    layer = Image.new("RGBA", (W, H), rgba(color, 255))
    layer.putalpha(m)
    base.alpha_composite(layer)


def composite_gradient(
    base: Image.Image,
    gradient: Image.Image,
    mask: Image.Image,
    alpha: int = 255,
    blur: float = 0.0,
) -> None:
    m = alpha_mask(mask, alpha)
    if blur:
        m = blurred(m, blur)
    layer = gradient.copy()
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), m))
    base.alpha_composite(layer)


# ---------------------------------------------------------------------------
# Unified cloud silhouette
# ---------------------------------------------------------------------------
# A narrow continuous heart keeps the figure connected. Large, strongly
# overlapping side puffs describe the long cloud edge; because every primitive
# is unioned into a single mask, no puff ever gets its own outline.
CORE_SHAPES = [
    (24.0, 29.0, 14.0, 23.0),
    (24.0, 70.0, 13.2, 26.0),
    (24.0, 112.0, 13.7, 27.0),
    (24.0, 154.0, 13.2, 28.0),
    (24.0, 198.0, 13.6, 30.0),
    (24.0, 244.0, 13.2, 29.0),
    (24.0, 289.0, 13.7, 27.0),
    (24.0, 330.0, 13.8, 21.0),
    (24.0, 16.5, 10.4, 11.2),
    (24.0, 31.0, 14.4, 13.0),
    (24.0, 346.0, 14.0, 9.8),
]

# Left-hand puffs; the right side is an exact mirror.
SIDE_PUFFS = [
    # y, x centre, x radius, y radius
    (48.0, 12.0, 8.4, 17.0),
    (80.0, 12.8, 9.2, 18.0),
    (112.0, 12.2, 8.2, 17.0),
    (145.0, 13.0, 9.4, 18.5),
    (178.0, 11.9, 8.0, 17.0),
    (211.0, 12.7, 8.8, 18.0),
    (244.0, 12.1, 8.2, 17.5),
    (277.0, 13.0, 9.3, 18.5),
    (307.0, 12.2, 8.5, 17.0),
    (332.0, 14.0, 9.0, 12.0),
    # a small crown shoulder on each side
    (27.0, 14.3, 8.2, 8.5),
]


def transformed_point(frame: str, x: float, y: float) -> tuple[float, float]:
    if frame == "idle":
        return x, y
    # A gentle inwards squash for the hit pose, about the frame centre.
    return 24.0 + (x - 24.0) * 0.90, 180.0 + (y - 180.0) * 0.962


def shape_mask(frame: str) -> Image.Image:
    mask = new_mask()
    draw = ImageDraw.Draw(mask)
    shapes = list(CORE_SHAPES)
    for y, x, rx, ry in SIDE_PUFFS:
        shapes.append((x, y, rx, ry))
        shapes.append((48.0 - x, y, rx, ry))

    for x, y, rx, ry in shapes:
        tx, ty = transformed_point(frame, x, y)
        sx = 1.0 if frame == "idle" else 0.90
        sy = 1.0 if frame == "idle" else 0.962
        draw.ellipse(
            (
                (tx - rx * sx) * SS,
                (ty - ry * sy) * SS,
                (tx + rx * sx) * SS,
                (ty + ry * sy) * SS,
            ),
            fill=255,
        )
    return mask


# ---------------------------------------------------------------------------
# The taut aqua "bounce bed"
# ---------------------------------------------------------------------------


def bed_geometry(frame: str) -> tuple[float, float, float, float, float]:
    x0, y0, x1, y1, rad = 14.9, 65.0, 33.1, 306.0, 7.0
    x0, y0 = transformed_point(frame, x0, y0)
    x1, y1 = transformed_point(frame, x1, y1)
    if frame == "hit":
        rad = 6.3
    return x0, y0, x1, y1, rad


def bed_masks(
    frame: str,
) -> tuple[Image.Image, Image.Image, Image.Image, tuple[float, float, float, float, float]]:
    x0, y0, x1, y1, rad = bed_geometry(frame)
    glow = rounded_mask(x0 - 2.7, y0 - 2.5, x1 + 2.7, y1 + 2.5, rad + 2.0, blur=7.5 * SS / 4.0)
    bed = rounded_mask(x0, y0, x1, y1, rad)
    inner = bed.filter(ImageFilter.MinFilter(9))
    rim = blurred(ImageChops.subtract(bed, inner), 1.6 * SS / 4.0)
    return glow, bed, rim, (x0, y0, x1, y1, rad)


# ---------------------------------------------------------------------------
# Sparkles
# ---------------------------------------------------------------------------


def star_points(cx: float, cy: float, radius: float, waist: float = 0.15) -> list[tuple[float, float]]:
    w = radius * waist
    return [
        (cx * SS, (cy - radius) * SS),
        ((cx + w) * SS, (cy - w) * SS),
        ((cx + radius) * SS, cy * SS),
        ((cx + w) * SS, (cy + w) * SS),
        (cx * SS, (cy + radius) * SS),
        ((cx - w) * SS, (cy + w) * SS),
        ((cx - radius) * SS, cy * SS),
        ((cx - w) * SS, (cy - w) * SS),
    ]


def draw_star(
    layer: Image.Image,
    frame: str,
    x: float,
    y: float,
    radius: float,
    alpha: int = 255,
) -> None:
    tx, ty = transformed_point(frame, x, y)
    r = radius * (1.12 if frame == "hit" else 1.0)

    halo_mask = new_mask()
    ImageDraw.Draw(halo_mask).ellipse(
        (
            (tx - r * 1.8) * SS,
            (ty - r * 1.8) * SS,
            (tx + r * 1.8) * SS,
            (ty + r * 1.8) * SS,
        ),
        fill=255,
    )
    halo_mask = alpha_mask(blurred(halo_mask, 4.0), 72 if frame == "hit" else 48)
    halo = Image.new("RGBA", (W, H), rgba(WARM, 255))
    halo.putalpha(halo_mask)
    layer.alpha_composite(halo)

    draw = ImageDraw.Draw(layer)
    draw.polygon(star_points(tx, ty, r), fill=rgba(WARM, alpha))
    draw.polygon(
        star_points(tx, ty, r * 0.36, waist=0.24),
        fill=rgba(WHITE, min(255, alpha + 10)),
    )
    draw.ellipse(
        (
            (tx - r * 0.16) * SS,
            (ty - r * 0.16) * SS,
            (tx + r * 0.16) * SS,
            (ty + r * 0.16) * SS,
        ),
        fill=rgba(WHITE, alpha),
    )


# ---------------------------------------------------------------------------
# Frame render
# ---------------------------------------------------------------------------


def render_frame(frame: str) -> Image.Image:
    hit = frame == "hit"
    mask = shape_mask(frame)

    # 1. Bright ice sky, white crown, a lavender undertone at the base.
    base = vertical_gradient(
        [
            (0.00, rgba(WHITE)),
            (0.10, rgba(mix(WHITE, ICE, 0.40))),
            (0.29, rgba(ICE)),
            (0.46, rgba(mix(ICE, SKY, 0.34))),
            (0.58, rgba(mix(ICE, SKY, 0.14))),
            (0.72, rgba(mix(ICE, LAVENDER, 0.34))),
            (0.86, rgba(mix(LAVENDER, ICE, 0.54))),
            (0.96, rgba(mix(LAVENDER, WHITE, 0.20))),
            (1.00, rgba(mix(LAVENDER, WHITE, 0.30))),
        ]
    )

    # 2. Soft colour weather inside the cloud. All of it is clipped by the
    # single silhouette at the end, so nothing looks like a separate shape.
    side_tint = horizontal_gradient(
        [
            (0.00, rgba(mix(SHADOW, LAVENDER, 0.42), 176)),
            (0.13, rgba(LAVENDER, 82)),
            (0.34, rgba(WHITE, 0)),
            (0.50, rgba(WHITE, 0)),
            (0.66, rgba(WHITE, 0)),
            (0.87, rgba(LAVENDER, 82)),
            (1.00, rgba(mix(SHADOW, LAVENDER, 0.42), 176)),
        ]
    )
    base.alpha_composite(side_tint)

    composite_color(base, LAVENDER, radial_mask(3.0, 292.0, 23.0, 88.0, blur=19.0), 118, 8.0)
    composite_color(base, LAVENDER, radial_mask(45.0, 292.0, 23.0, 88.0, blur=19.0), 118, 8.0)
    composite_color(base, SKY, radial_mask(2.0, 92.0, 19.0, 92.0, blur=18.0), 76, 8.0)
    composite_color(base, SKY, radial_mask(46.0, 92.0, 19.0, 92.0, blur=18.0), 76, 8.0)

    # The core of the cloud stays luminous and airy.
    composite_color(base, mix(ICE, WHITE, 0.62), radial_mask(24.0, 171.0, 17.0, 148.0, blur=15.0), 94, 8.0)
    top_light = vertical_gradient(
        [
            (0.00, rgba(WHITE, 156)),
            (0.17, rgba(WHITE, 76)),
            (0.38, rgba(WHITE, 0)),
            (1.00, rgba(WHITE, 0)),
        ]
    )
    composite_gradient(base, top_light, mask, 255)

    # Subtle highlights sit on the shoulders of several big puffs. They are
    # broad and borderless, like light caught inside the cloud, not rings.
    for cy in (87.0, 152.0, 249.0):
        composite_color(base, WHITE, radial_mask(17.4, cy - 8.0, 5.4, 15.0, blur=9.0), 58, 4.0)
        composite_color(base, WHITE, radial_mask(30.6, cy - 8.0, 5.4, 15.0, blur=9.0), 58, 4.0)
    # A cooler, softer shadow inside the lower side lobes.
    composite_color(
        base,
        mix(SHADOW, LAVENDER, 0.60),
        radial_mask(13.4, 282.0, 6.0, 30.0, blur=13.0),
        26,
        5.0,
    )
    composite_color(
        base,
        mix(SHADOW, LAVENDER, 0.60),
        radial_mask(34.6, 282.0, 6.0, 30.0, blur=13.0),
        26,
        5.0,
    )

    # Broad, borderless light on the top of each round side puff. These are
    # shading, not outlines; the silhouette itself remains one unified mask.
    for py, px, prx, pry in SIDE_PUFFS:
        for cx in (px, 48.0 - px):
            tx, ty = transformed_point(frame, cx, py - pry * 0.22)
            composite_color(
                base,
                WHITE,
                radial_mask(tx, ty, prx * 0.82, pry * 0.42, blur=7.0),
                64 if not hit else 70,
                4.0,
            )
            sx, sy = transformed_point(frame, cx, py + pry * 0.48)
            composite_color(
                base,
                mix(SHADOW, LAVENDER, 0.62),
                radial_mask(sx, sy, prx * 0.78, pry * 0.36, blur=9.0),
                30 if not hit else 25,
                4.0,
            )

    # 3. Volume around the scalloped contour.
    deep_edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(31)))
    composite_color(base, mix(LAVENDER, SHADOW, 0.10), deep_edge, 98 if not hit else 88, 8.0)

    rim_shadow = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(19)))
    composite_color(base, mix(SHADOW, LAVENDER, 0.60), rim_shadow, 88 if not hit else 72, 4.0)

    # A narrow, soft blue outline sits inside the silhouette. The white top
    # band and pale bed rim are painted afterwards, so the crown stays airy
    # while the sides and underside gain a readable 1..2 px edge at game size.
    contour = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(9)))
    composite_color(base, DEEP_OUTLINE, contour, 112 if not hit else 126, 1.5)

    under_shade = ImageChops.subtract(mask, ImageChops.offset(mask, 0, -42))
    composite_color(
        base,
        mix(SHADOW, LAVENDER, 0.32),
        under_shade,
        78 if not hit else 64,
        8.0,
    )
    bottom_band = ImageChops.subtract(mask, ImageChops.offset(mask, 0, -18))
    composite_color(
        base,
        mix(SHADOW, LAVENDER, 0.48),
        bottom_band,
        108 if not hit else 82,
        5.0,
    )

    rim = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(11)))
    composite_color(base, mix(ICE, WHITE, 0.52), rim, 106 if not hit else 148, 2.0)

    top_band = ImageChops.subtract(mask, ImageChops.offset(mask, 0, 14))
    composite_color(base, WHITE, top_band, 204 if not hit else 240, 3.2)
    broad_top = ImageChops.subtract(mask, ImageChops.offset(mask, 0, 31))
    composite_color(base, WHITE, broad_top, 44 if not hit else 64, 6.0)

    # A few tiny, crisp glints along the upper puffs.
    for gx, gy in ((9.0, 48.0), (39.0, 48.0), (8.7, 146.0), (39.3, 146.0), (9.8, 256.0), (38.2, 256.0)):
        tx, ty = transformed_point(frame, gx, gy)
        composite_color(base, WHITE, radial_mask(tx, ty, 1.25, 0.8, blur=1.1), 138, 0.3)
        composite_color(base, WHITE, radial_mask(tx, ty + 1.4, 0.55, 0.55, blur=0.8), 170, 0.2)

    # 4. Low, soft blush.
    for cx in (14.6, 33.4):
        tx, ty = transformed_point(frame, cx, 316.0)
        blush_mask = radial_mask(tx, ty, 5.4 if not hit else 4.9, 3.2, blur=3.1)
        composite_color(base, BLUSH, blush_mask, 118 if not hit else 138)

    # 5. Bounce bed and its pale aqua inner glow.
    glow, bed, bed_rim, (bx0, by0, bx1, by1, _rad) = bed_masks(frame)
    composite_color(base, SKY, glow, 110 if not hit else 150)
    bed_gradient = vertical_gradient(
        [
            (0.00, rgba(ICE, 0)),
            (0.17, rgba(mix(ICE, WHITE, 0.24), 92)),
            (0.28, rgba(mix(ICE, SKY, 0.42), 118)),
            (0.50, rgba(mix(ICE, SKY, 0.34), 122)),
            (0.71, rgba(mix(SKY, LAVENDER, 0.30), 98)),
            (0.86, rgba(mix(LAVENDER, SKY, 0.38), 80)),
            (1.00, rgba(LAVENDER, 0)),
        ]
    )
    composite_gradient(base, bed_gradient, bed, 255)
    # Soft inner shading around the taut panel.
    bed_shadow = ImageChops.subtract(bed, bed.filter(ImageFilter.MinFilter(17)))
    composite_color(base, mix(SHADOW, LAVENDER, 0.58), bed_shadow, 62 if not hit else 50, 3.0)
    composite_color(base, mix(ICE, WHITE, 0.62), bed_rim, 198 if not hit else 232, 0.8)

    # A glossier central sheen, hugging the top half of the bed.
    composite_color(
        base,
        WHITE,
        radial_mask((bx0 + bx1) / 2.0, 155.0, (bx1 - bx0) * 0.23, 69.0, blur=8.0),
        68 if not hit else 88,
    )

    # Woven transverse threads: intentionally quiet at game scale.
    thread_mask = new_mask()
    thread_draw = ImageDraw.Draw(thread_mask)
    for y in (98.0, 130.0, 162.0, 194.0, 226.0, 258.0, 290.0):
        ty = y if not hit else transformed_point(frame, 24.0, y)[1]
        rel = (ty - by0) / (by1 - by0)
        if rel <= 0.035 or rel >= 0.965:
            continue
        inset = 2.1
        x0 = bx0 + inset
        x1 = bx1 - inset
        # A barely perceptible downward bow gives the bed a little tension.
        mid = (x0 + x1) / 2.0
        bow = 0.7
        pts = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            x = x0 + (x1 - x0) * t
            yy = ty + math.sin(math.pi * t) * bow
            pts.append((x * SS, yy * SS))
        thread_draw.line(pts, fill=255, width=4, joint="curve")
    thread_mask = blurred(thread_mask, 0.8)
    composite_color(base, WHITE, thread_mask, 92 if not hit else 112)

    # A whisper of diagonal weave makes the bed read as a taut trampoline
    # surface rather than a plain glass capsule.
    weave_mask = new_mask()
    weave_draw = ImageDraw.Draw(weave_mask)
    for direction in (-1.0, 1.0):
        for offset in range(-260, 280, 26):
            # x = mid + direction * (y - mid) + offset, clipped to bed later
            x_at_top = (bx0 + bx1) / 2.0 + offset
            x_at_bottom = x_at_top + direction * (by1 - by0)
            weave_draw.line(
                (
                    x_at_top * SS,
                    (by0 - 10.0) * SS,
                    x_at_bottom * SS,
                    (by1 + 10.0) * SS,
                ),
                fill=255,
                width=2,
            )
    weave_mask = ImageChops.multiply(weave_mask, bed)
    weave_mask = blurred(weave_mask, 1.4)
    composite_color(base, WHITE, weave_mask, 20 if not hit else 28)

    # 6. Clip everything to the unified cloud.
    base.putalpha(mask)

    # 7. Star sparkles, with their own little halos, sit above the cloud.
    star_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x, y, radius in (
        (24.0, 43.0, 3.7),
        (12.4, 93.0, 2.3),
        (35.6, 93.0, 2.3),
        (24.0, 163.0, 2.7),
        (12.9, 235.0, 2.1),
        (35.1, 235.0, 2.1),
        (24.0, 286.0, 2.2),
    ):
        draw_star(star_layer, frame, x, y, radius)
    if hit:
        for x, y, radius, alpha in (
            (24.0, 70.0, 1.8, 240),
            (15.2, 120.0, 1.5, 225),
            (32.8, 120.0, 1.5, 225),
            (24.0, 210.0, 1.7, 230),
            (16.8, 306.0, 1.4, 220),
            (31.2, 306.0, 1.4, 220),
        ):
            draw_star(star_layer, frame, x, y, radius, alpha=alpha)
    base.alpha_composite(star_layer)

    # 8. A touch more white heat in the hit pose (clipped to the cloud).
    if hit:
        composite_color(base, WHITE, mask, 18)

    # 9. LANCZOS downsample and cleanup. Keep a genuinely transparent safe
    # margin in every frame so adjacent sprites never bleed together.
    out = base.resize((FRAME_W, FRAME_H), Image.Resampling.LANCZOS)
    alpha = out.getchannel("A").point(lambda value: 0 if value < 7 else value)
    out.putalpha(alpha)
    px = out.load()
    for y in range(FRAME_H):
        for x in range(FRAME_W):
            if x < 2 or x >= FRAME_W - 2 or y < 2 or y >= FRAME_H - 2:
                px[x, y] = (0, 0, 0, 0)
            elif px[x, y][3] == 0:
                px[x, y] = (255, 255, 255, 0)
    return out


def build() -> None:
    idle = render_frame("idle")
    hit = render_frame("hit")

    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    sheet.alpha_composite(idle, (0, 0))
    sheet.alpha_composite(hit, (FRAME_W + GAP, 0))

    assert sheet.size == (97, 360)
    gap_alpha = sheet.crop((FRAME_W, 0, FRAME_W + GAP, SHEET_H)).getchannel("A")
    assert gap_alpha.getbbox() is None, "the 1px frame gap must be transparent"
    for name, x in (("cloud_idle", 0), ("cloud_hit", 49)):
        alpha = sheet.crop((x, 0, x + FRAME_W, FRAME_H)).getchannel("A")
        bbox = alpha.getbbox()
        assert bbox is not None, f"{name} must contain visible pixels"
        left, top, right, bottom = bbox
        assert left >= 2 and top >= 2 and FRAME_W - right >= 2 and FRAME_H - bottom >= 2

    sheet.save(OUT_PATH, format="PNG", optimize=True)
    print(f"wrote {OUT_PATH} ({SHEET_W}x{SHEET_H}, RGBA)")


if __name__ == "__main__":
    build()'''


BACKGROUND_RENDERER = r'''#!/usr/bin/env python3
"""Build the deterministic 800 x 600 contrast-enhanced dreamy-sky background.

Pure Pillow raster art. Geometry and sprite-like details are rendered at 4x
(3200 x 2400) and reduced with LANCZOS for soft, vector-like edges. The top
stays bright cyan and the base stays pastel lavender, while a deeper
periwinkle mid-sky, soft side-band shading and blue-lavender cloud shadows
make the white ball and paddle clouds readable. There is no randomness, no
input image, no font and no external asset.

Run from anywhere:

    python3 build_background.py

The output is written next to this script as ``background.png``. The image is
RGBA with every alpha channel value equal to 255.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# Output / palette

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "background.png"

W, H = 800, 600
S = 4                    # 4x supersampling
CW, CH = W * S, H * S

# Shared reference palette for the Pingpong art family. The rainbow uses
# slightly deeper source hues below so it stays legible through its pastel
# alpha blend.
ICE = (234, 249, 255)       # #EAF9FF
WHITE = (255, 255, 255)     # #FFFFFF
SKY = (143, 231, 255)       # #8FE7FF
CYAN = (94, 214, 255)       # #5ED6FF
PERIWINKLE = (169, 200, 255)  # #A9C8FF
LAVENDER = (216, 204, 255)  # #D8CCFF
WARM = (255, 243, 196)      # #FFF3C4
CORAL = (255, 154, 174)     # #FF9AAE
MINT = (168, 240, 208)      # #A8F0D0
PEACH = (255, 201, 139)     # #FFC98B
LEMON = (255, 240, 168)     # #FFF0A8
RAIN_SKY = (158, 216, 255)  # #9ED8FF
RAIN_LAV = (201, 184, 255)  # #C9B8FF

# Sky: bright cyan at the top, medium periwinkle blue through the play band
# and a pastel lavender base. The middle stops are deliberately deeper than
# the white sprites so the bubble and cloud paddles keep a clear edge.
SKY_STOPS = (
    (0.00, (127, 224, 255)),
    (0.10, (127, 222, 254)),
    (0.24, (127, 206, 245)),
    (0.39, (120, 190, 234)),
    (0.52, (118, 182, 232)),
    (0.63, (118, 173, 230)),
    (0.73, (146, 183, 235)),
    (0.84, (176, 204, 242)),
    (0.93, (194, 212, 245)),
    (1.00, (210, 199, 245)),
)


# ---------------------------------------------------------------------------
# Small helpers


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def mix(a: Sequence[int], b: Sequence[int], t: float) -> tuple[int, int, int]:
    t = clamp(t)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lerp_stops(stops: Sequence[tuple[float, tuple[int, int, int]]],
               position: float) -> tuple[int, int, int]:
    position = clamp(position)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= position <= p1:
            if p1 == p0:
                return c1
            return mix(c0, c1, (position - p0) / (p1 - p0))
    return stops[-1][1]


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge0 == edge1:
        return float(x >= edge1)
    t = clamp((x - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def vertical_gradient(width: int, height: int,
                      stops: Sequence[tuple[float, tuple[int, int, int]]]
                      ) -> Image.Image:
    """Return an RGB vertical gradient image, drawn row by row."""

    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        draw.line((0, y, width, y), fill=lerp_stops(stops, t))
    return image


def transparent(size: tuple[int, int]) -> Image.Image:
    return Image.new("RGBA", size, (255, 255, 255, 0))


def shifted(mask: Image.Image, dx: int, dy: int) -> Image.Image:
    out = Image.new("L", mask.size, 0)
    out.paste(mask, (dx, dy))
    return out


def scaled_alpha(mask: Image.Image, amount: int | float) -> Image.Image:
    """Multiply an 8-bit mask by ``amount`` (0..255)."""

    factor = int(round(amount))
    if factor >= 255:
        return mask
    if factor <= 0:
        return Image.new("L", mask.size, 0)
    return mask.point(lambda value: (value * factor + 127) // 255)


def colour_mask(mask: Image.Image, colour: tuple[int, int, int],
                alpha: int = 255) -> Image.Image:
    """Build a solid-colour RGBA layer with per-pixel alpha from mask."""

    mask = scaled_alpha(mask, alpha)
    r, g, b = colour
    size = mask.size
    return Image.merge("RGBA", (
        Image.new("L", size, r),
        Image.new("L", size, g),
        Image.new("L", size, b),
        mask,
    ))


def composite_glow(canvas: Image.Image, mask: Image.Image,
                   colour: tuple[int, int, int], opacity: int) -> None:
    """Composite a full-canvas mask as a softly coloured glow."""

    if mask.size != canvas.size:
        mask = mask.resize(canvas.size, Image.Resampling.BICUBIC)
    canvas.alpha_composite(colour_mask(mask, colour, opacity))


def horizontal_band_mask(centre_y: float, sigma: float,
                         peak: int) -> Image.Image:
    """Broad, edgeless horizontal atmospheric band, built at 4x."""

    image = Image.new("L", (CW, CH), 0)
    draw = ImageDraw.Draw(image)
    for y in range(CH):
        yy = (y + 0.5) / S
        alpha = round(peak * math.exp(-0.5 * ((yy - centre_y) / sigma) ** 2))
        draw.line((0, y, CW, y), fill=alpha)
    return image


def radial_mask(cx: float, cy: float, rx: float, ry: float,
                power: float = 2.0) -> Image.Image:
    """Smooth elliptical falloff mask generated at review resolution.

    These are broad atmospheric gradients (sun halo, haze), not edge art, so
    creating them at 800 x 600 and upscaling keeps them perfectly smooth while
    the geometric art itself is still rendered at 4x.
    """

    image = Image.new("L", (W, H), 0)
    pixels = image.load()
    inv_rx = 1.0 / max(rx, 0.001)
    inv_ry = 1.0 / max(ry, 0.001)
    for y in range(H):
        dy = (y + 0.5 - cy) * inv_ry
        dy2 = dy * dy
        if dy2 >= 1.0:
            continue
        for x in range(W):
            dx = (x + 0.5 - cx) * inv_rx
            d2 = dx * dx + dy2
            if d2 < 1.0:
                pixels[x, y] = int(round(255.0 * (1.0 - d2) ** power))
    image = image.filter(ImageFilter.GaussianBlur(0.65))
    return image.resize((CW, CH), Image.Resampling.BICUBIC)


def linear_alpha(width: int, height: int,
                 stops: Sequence[tuple[float, int]]) -> Image.Image:
    """Vertical 0..255 alpha ramp in a local high-resolution layer."""

    image = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        alpha = 0
        for i in range(len(stops) - 1):
            p0, a0 = stops[i]
            p1, a1 = stops[i + 1]
            if p0 <= t <= p1:
                local = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                local = local * local * (3.0 - 2.0 * local)
                alpha = round(a0 + (a1 - a0) * local)
                break
        else:
            alpha = stops[-1][1]
        draw.line((0, y, width, y), fill=alpha)
    return image


def apply_alpha_opacity(image: Image.Image, opacity: int) -> Image.Image:
    if opacity >= 255:
        return image
    r, g, b, a = image.split()
    a = scaled_alpha(a, opacity)
    return Image.merge("RGBA", (r, g, b, a))


# ---------------------------------------------------------------------------
# Sky


def make_sky() -> Image.Image:
    base = vertical_gradient(CW, CH, SKY_STOPS).convert("RGBA")

    # A cool aqua breath in the upper-left, balancing the warm sun at the
    # upper-right without creating a visible circular edge.
    composite_glow(
        base,
        radial_mask(130, 5, 420, 300, power=2.6),
        (185, 245, 255), 30,
    )

    # A broad periwinkle air layer through the middle of the sky. It is almost
    # edgeless, deepens the space behind both paddle columns and lets the pale
    # sprites read clearly without a hard vignette edge.
    composite_glow(base, horizontal_band_mask(332, 150, 58),
                   (125, 165, 232), 255)
    composite_glow(
        base,
        radial_mask(400, 332, 520, 205, power=2.1),
        (135, 173, 235), 30,
    )

    # Diffuse pale-ice light around the horizon, adding airy depth.
    composite_glow(
        base,
        radial_mask(365, 410, 560, 155, power=2.4),
        (245, 253, 255), 26,
    )

    # Lilac weight in the extreme bottom corners only.
    composite_glow(
        base,
        radial_mask(-20, 620, 360, 235, power=2.3),
        LAVENDER, 42,
    )
    composite_glow(
        base,
        radial_mask(840, 620, 350, 225, power=2.3),
        LAVENDER, 36,
    )
    return base


# ---------------------------------------------------------------------------
# Sun and rays


def add_sun(canvas: Image.Image) -> None:
    cx, cy = 588, 94

    # Broad warm halo, then progressively brighter, tighter layers.
    glow_layers = (
        (335, 290, (255, 227, 158), 40, 2.3),
        (225, 195, (255, 235, 174), 55, 2.1),
        (145, 128, (255, 241, 190), 79, 2.0),
        (78, 70, (255, 246, 209), 108, 2.2),
        (31, 29, (255, 249, 222), 145, 1.4),
        (20, 19, (255, 248, 216), 178, 0.55),
    )
    for rx, ry, colour, alpha, power in glow_layers:
        composite_glow(canvas, radial_mask(cx, cy, rx, ry, power), colour,
                       alpha)

    # Subtle cream sun rays. They are drawn at 4x, then heavily softened.
    mask = Image.new("L", (CW, CH), 0)
    draw = ImageDraw.Draw(mask)
    scx, scy = cx * S, cy * S
    for i in range(14):
        # A deterministic, gently irregular pinwheel of broad rays.
        angle = -math.pi / 2.0 + i * (math.tau / 14.0)
        length = (238 + (i * 37) % 7 * 19) * S
        inner = 47 * S
        tip_width = (17 + (i * 13) % 5 * 3) * S
        root_width = 3.0 * S
        ux, uy = math.cos(angle), math.sin(angle)
        vx, vy = -uy, ux
        points = (
            (scx + ux * inner + vx * root_width,
             scy + uy * inner + vy * root_width),
            (scx + ux * length + vx * tip_width,
             scy + uy * length + vy * tip_width),
            (scx + ux * length - vx * tip_width,
             scy + uy * length - vy * tip_width),
            (scx + ux * inner - vx * root_width,
             scy + uy * inner - vy * root_width),
        )
        draw.polygon(points, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(7.5 * S))
    composite_glow(canvas, mask, (255, 242, 198), 34)


# ---------------------------------------------------------------------------
# Rainbow


def add_rainbow(canvas: Image.Image) -> None:
    # The circle centre is below the frame, so only a generous upper arc is
    # seen. Its lower tail is faded out before it reaches the paddle zones.
    cx, cy = 400.0, 660.0
    outer_radius = 500.0
    band_width = 14.0
    # Slightly more saturated input hues compensate for the natural softening
    # of alpha over aqua; the result on screen remains gentle and pastel.
    colours = (
        ((255, 126, 157), 148),
        ((255, 185, 119), 151),
        ((255, 229, 126), 158),
        ((137, 234, 192), 142),
        ((116, 204, 255), 134),
        ((180, 157, 255), 127),
    )

    # Vertical fade: full across the elegant crown, gone before the lower
    # sides reach the paddle band.
    fade = Image.new("L", (CW, CH), 0)
    fade_draw = ImageDraw.Draw(fade)
    for y in range(CH):
        yy = (y + 0.5) / S
        value = 1.0 - smoothstep(242.0, 330.0, yy)
        fade_draw.line((0, y, CW, y), fill=round(255 * value))

    # A barely-there milky under-halo separates the pastel bands from the
    # aqua sky and makes the whole arc feel lit from within.
    halo_radius_out = (outer_radius + 6.0) * S
    halo_radius_in = (outer_radius - len(colours) * band_width - 8.0) * S
    halo = Image.new("L", (CW, CH), 0)
    hdraw = ImageDraw.Draw(halo)
    hcx, hcy = cx * S, cy * S
    hdraw.ellipse(
        (hcx - halo_radius_out, hcy - halo_radius_out,
         hcx + halo_radius_out, hcy + halo_radius_out),
        fill=255,
    )
    hdraw.ellipse(
        (hcx - halo_radius_in, hcy - halo_radius_in,
         hcx + halo_radius_in, hcy + halo_radius_in),
        fill=0,
    )
    halo = halo.filter(ImageFilter.GaussianBlur(5.0 * S))
    halo = ImageChops.multiply(halo, fade)
    canvas.alpha_composite(colour_mask(halo, (250, 254, 255), 22))

    for i, (colour, alpha) in enumerate(colours):
        radius_out = (outer_radius - i * band_width) * S
        radius_in = (outer_radius - (i + 1) * band_width - 0.8) * S
        mask = Image.new("L", (CW, CH), 0)
        draw = ImageDraw.Draw(mask)
        cxh, cyh = cx * S, cy * S
        draw.ellipse(
            (cxh - radius_out, cyh - radius_out,
             cxh + radius_out, cyh + radius_out),
            fill=255,
        )
        draw.ellipse(
            (cxh - radius_in, cyh - radius_in,
             cxh + radius_in, cyh + radius_in),
            fill=0,
        )
        mask = mask.filter(ImageFilter.GaussianBlur(1.05 * S))
        mask = ImageChops.multiply(mask, fade)
        canvas.alpha_composite(colour_mask(mask, colour, alpha))


# ---------------------------------------------------------------------------
# Clouds


def cloud_bounds(lobes: Iterable[tuple[float, float, float, float]],
                 pad: float) -> tuple[int, int, int, int]:
    min_x = min(cx - rx for cx, cy, rx, ry in lobes)
    max_x = max(cx + rx for cx, cy, rx, ry in lobes)
    min_y = min(cy - ry for cx, cy, rx, ry in lobes)
    max_y = max(cy + ry for cx, cy, rx, ry in lobes)
    x0 = max(0, int(math.floor((min_x - pad) * S)))
    y0 = max(0, int(math.floor((min_y - pad) * S)))
    x1 = min(CW, int(math.ceil((max_x + pad) * S)))
    y1 = min(CH, int(math.ceil((max_y + pad) * S)))
    return x0, y0, x1, y1


def render_cloud(lobes: Sequence[tuple[float, float, float, float]],
                 *, opacity: int = 255,
                 shade_strength: float = 1.0,
                 warm_strength: float = 1.0,
                 sun_from_left: bool = False,
                 feather: float = 0.0) -> tuple[Image.Image, tuple[int, int]]:
    """Render one soft, rounded cloud at 4x into a local RGBA patch."""

    pad = 38.0
    x0, y0, x1, y1 = cloud_bounds(lobes, pad)
    lw, lh = max(1, x1 - x0), max(1, y1 - y0)
    ox, oy = x0 / S, y0 / S

    def local_ellipse(cx: float, cy: float, rx: float, ry: float) -> tuple:
        return (
            (cx - ox - rx) * S,
            (cy - oy - ry) * S,
            (cx - ox + rx) * S,
            (cy - oy + ry) * S,
        )

    mask = Image.new("L", (lw, lh), 0)
    mdraw = ImageDraw.Draw(mask)
    for cx, cy, rx, ry in lobes:
        mdraw.ellipse(local_ellipse(cx, cy, rx, ry), fill=255)

    visible = mask.getbbox()
    if visible is None:
        return transparent((lw, lh)), (x0, y0)
    shape_top, shape_bottom = visible[1], visible[3]
    shape_h = max(1, shape_bottom - shape_top)

    local = transparent((lw, lh))

    # 1. Cool drop shadow. A compact, slightly offset shade gives the mass
    #    real lift; a wide second halo keeps the edge airy.
    shadow_dx = int(round((5 if sun_from_left else -5) * S))
    shadow = shifted(mask, shadow_dx, int(round(7 * S)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(4.2 * S))
    local.alpha_composite(colour_mask(shadow, (104, 143, 210), 64))
    far_shadow = mask.filter(ImageFilter.GaussianBlur(8.0 * S))
    local.alpha_composite(colour_mask(far_shadow, (144, 183, 239), 25))

    # 2. Pastel ice rim, mostly just outside the silhouette.
    aura = mask.filter(ImageFilter.GaussianBlur(1.45 * S))
    local.alpha_composite(colour_mask(aura, (190, 237, 255), 34))

    # 3. Body gradient normalised to the actual silhouette, not to the padded
    #    working patch. This is what gives the cloud its clear white crown and
    #    lavender-blue base instead of a flat white cut-out.
    body_rgb = Image.new("RGB", (lw, lh))
    bdraw = ImageDraw.Draw(body_rgb)
    body_stops = (
        (0.00, (255, 255, 255)),
        (0.18, (255, 254, 249)),
        (0.40, (252, 254, 255)),
        (0.58, (241, 249, 255)),
        (0.75, (225, 238, 255)),
        (0.90, (207, 222, 255)),
        (1.00, (196, 210, 250)),
    )
    for y in range(lh):
        t = (y - shape_top) / shape_h
        bdraw.line((0, y, lw, y), fill=lerp_stops(body_stops, t))
    body = Image.merge("RGBA", (*body_rgb.split(), mask))
    local.alpha_composite(body)

    # 4. Cool underlight, strongest at the bottom edge. The very bottom gets a
    #    cooler violet wash, mirroring the paddle-cloud's lavender underside.
    under = linear_alpha(lw, lh, ((0.38, 0), (0.63, 42), (1.0, 172)))
    under = ImageChops.multiply(under, mask)
    under = under.filter(ImageFilter.GaussianBlur(3.4 * S))
    under = ImageChops.multiply(under, mask)
    local.alpha_composite(colour_mask(under, (153, 178, 233),
                                      round(108 * shade_strength)))

    # 5. Per-lobe volume: broad, soft cool crescents under each round puff.
    #    They are blurred widely so the result reads as one puffy mass rather
    #    than as a row of separate circles.
    lobe_shadow = Image.new("L", (lw, lh), 0)
    lobe_shadow_draw = ImageDraw.Draw(lobe_shadow)
    for cx, cy, rx, ry in lobes:
        if rx * ry < 500:
            continue
        lobe_shadow_draw.ellipse(local_ellipse(
            cx - (0.10 if sun_from_left else -0.10) * rx,
            cy + 0.43 * ry,
            0.74 * rx, 0.40 * ry,
        ), fill=255)
    lobe_shadow = lobe_shadow.filter(ImageFilter.GaussianBlur(7.4 * S))
    lobe_shadow = ImageChops.multiply(lobe_shadow, mask)
    local.alpha_composite(colour_mask(lobe_shadow, (139, 168, 231),
                                      round(55 * shade_strength)))

    # A few deeper, isolated under-puffs keep large banks from looking like
    # one undifferentiated white pillow.
    for index, (cx, cy, rx, ry) in enumerate(lobes):
        if index % 2:
            continue
        blob = Image.new("L", (lw, lh), 0)
        bd = ImageDraw.Draw(blob)
        bd.ellipse(local_ellipse(cx, cy + 0.25 * ry,
                                 0.58 * rx, 0.42 * ry), fill=255)
        blob = blob.filter(ImageFilter.GaussianBlur(7.0 * S))
        blob = ImageChops.multiply(blob, mask)
        local.alpha_composite(colour_mask(blob, (144, 171, 233),
                                          round(26 * shade_strength)))

    # 6. Warm crown wash plus a directional kiss of sunlight from above.
    crown = linear_alpha(lw, lh, ((0.0, 146), (0.29, 38), (0.55, 0)))
    crown = ImageChops.multiply(crown, mask)
    crown = crown.filter(ImageFilter.GaussianBlur(3.8 * S))
    crown = ImageChops.multiply(crown, mask)
    local.alpha_composite(colour_mask(crown, (255, 245, 211),
                                      round(148 * warm_strength)))

    light_x = 0.22 if sun_from_left else 0.78
    light = Image.new("L", (lw, lh), 0)
    ldraw = ImageDraw.Draw(light)
    top = min(cy - ry for cx, cy, rx, ry in lobes)
    bottom = max(cy + ry for cx, cy, rx, ry in lobes)
    left = min(cx - rx for cx, cy, rx, ry in lobes)
    right = max(cx + rx for cx, cy, rx, ry in lobes)
    lcx = left + (right - left) * light_x
    lcy = top + (bottom - top) * 0.28
    ldraw.ellipse(local_ellipse(lcx, lcy,
                                (right - left) * 0.45,
                                (bottom - top) * 0.34), fill=255)
    light = light.filter(ImageFilter.GaussianBlur(9.0 * S))
    light = ImageChops.multiply(light, mask)
    local.alpha_composite(colour_mask(light, (255, 250, 226),
                                      round(104 * warm_strength)))

    # 7. Luminous top rim. It is wide and low contrast, so the silhouette
    #    stays soft and vector-smooth.
    top_cap = ImageChops.subtract(mask, shifted(mask, 0, -int(9 * S)))
    top_cap = top_cap.filter(ImageFilter.GaussianBlur(3.0 * S))
    top_cap = ImageChops.multiply(top_cap, mask)
    local.alpha_composite(colour_mask(top_cap, (255, 255, 249), 176))

    # 8. Fine feathered quality for distant clouds; main clouds stay crisper.
    if feather > 0:
        local = local.filter(ImageFilter.GaussianBlur(feather * S))

    local = apply_alpha_opacity(local, opacity)
    return local, (x0, y0)


def place_cloud(canvas: Image.Image,
                lobes: Sequence[tuple[float, float, float, float]],
                **kwargs) -> None:
    layer, position = render_cloud(lobes, **kwargs)
    canvas.alpha_composite(layer, position)


# ---------------------------------------------------------------------------
# Sparkles


def add_sparkle(canvas: Image.Image, cx: float, cy: float, radius: float,
                angle_deg: float = 0.0, alpha: int = 224) -> None:
    """Tiny warm four-point twinkle with a diffuse halo."""

    r = radius
    glow = Image.new("L", (CW, CH), 0)
    gd = ImageDraw.Draw(glow)
    gr = int(math.ceil(r * 4.0))
    gx, gy = cx * S, cy * S
    gd.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(2.3 * S))
    composite_glow(canvas, glow, (255, 248, 212), max(30, alpha // 3))

    angle = math.radians(angle_deg)
    ca, sa = math.cos(angle), math.sin(angle)

    def point(x: float, y: float) -> tuple[float, float]:
        return (gx + (x * ca - y * sa) * S,
                gy + (x * sa + y * ca) * S)

    star = Image.new("L", (CW, CH), 0)
    sd = ImageDraw.Draw(star)
    long = r
    short = r * 0.50
    waist = r * 0.20
    points = (
        point(0, -long),
        point(waist, -waist),
        point(short, 0),
        point(waist, waist),
        point(0, long),
        point(-waist, waist),
        point(-short, 0),
        point(-waist, -waist),
    )
    sd.polygon(points, fill=255)
    star = star.filter(ImageFilter.GaussianBlur(0.16 * S))
    composite_glow(canvas, star, (255, 250, 226), alpha)


# ---------------------------------------------------------------------------
# Composition


def add_lane_shade(canvas: Image.Image) -> None:
    """Deepen the soft blue side bands behind the paddle columns.

    The veil is strongest through y=190..420, exactly where the 48 x 360
    paddle frames sit at game scale, and fades out before the cloud banks at
    the top and bottom edges. It is a broad atmospheric gradient, not a hard
    vignette, so the dreamy sky stays continuous.
    """

    shade = Image.new("L", (W, H), 0)
    pixels = shade.load()
    for y in range(H):
        yy = y + 0.5
        vertical = smoothstep(105.0, 195.0, yy) * (
            1.0 - smoothstep(420.0, 530.0, yy)
        )
        if vertical <= 0.0:
            continue
        for x in range(W):
            xx = x + 0.5
            left = math.exp(-0.5 * ((xx - 53.0) / 64.0) ** 2)
            right = math.exp(-0.5 * ((xx - 747.0) / 72.0) ** 2)
            pixels[x, y] = min(255, round(40.0 * (left + 0.92 * right) * vertical))
    shade = shade.resize((CW, CH), Image.Resampling.BICUBIC)
    composite_glow(canvas, shade, (54, 104, 168), 255)


def build() -> Image.Image:
    canvas = make_sky()
    add_sun(canvas)
    add_rainbow(canvas)

    # Distant wisps, deliberately pale and low-contrast. They add depth behind
    # the main banks without competing with the ball area.
    place_cloud(
        canvas,
        (
            (317, 134, 27, 16),
            (344, 121, 30, 21),
            (373, 129, 28, 16),
            (354, 141, 35, 14),
        ),
        opacity=132, feather=1.0, shade_strength=0.55,
        warm_strength=0.65, sun_from_left=False,
    )
    place_cloud(
        canvas,
        (
            (471, 155, 24, 12),
            (495, 144, 29, 16),
            (520, 153, 23, 11),
            (499, 163, 33, 11),
        ),
        opacity=94, feather=1.3, shade_strength=0.45,
        warm_strength=0.55, sun_from_left=True,
    )

    # Top-left cloud bank: the main, slightly heavier frame on the left.
    place_cloud(
        canvas,
        (
            (-64, 102, 92, 55),
            (-16, 78, 72, 52),
            (38, 58, 60, 47),
            (99, 50, 56, 44),
            (157, 64, 64, 49),
            (216, 88, 49, 38),
            (253, 111, 31, 25),
            (-12, 126, 102, 46),
            (70, 108, 103, 49),
            (155, 118, 92, 45),
            (221, 131, 50, 33),
        ),
        opacity=253, shade_strength=1.14, warm_strength=1.0,
        sun_from_left=False,
    )

    # Top-right bank: higher and a little airier, leaving the warm sun in the
    # open gap between the two banks.
    place_cloud(
        canvas,
        (
            (694, 88, 55, 35),
            (750, 51, 59, 49),
            (814, 38, 64, 48),
            (873, 64, 58, 48),
            (908, 100, 44, 38),
            (757, 103, 91, 48),
            (839, 113, 82, 44),
            (703, 116, 47, 29),
        ),
        opacity=250, shade_strength=1.0, warm_strength=1.12,
        sun_from_left=True,
    )

    # Bottom-left bank, cropped by the frame. It stays below the paddle band.
    place_cloud(
        canvas,
        (
            (-68, 560, 110, 68),
            (25, 532, 91, 65),
            (109, 541, 102, 59),
            (193, 560, 94, 57),
            (266, 583, 69, 44),
            (36, 615, 152, 66),
            (164, 621, 132, 54),
        ),
        opacity=253, shade_strength=1.16, warm_strength=0.82,
        sun_from_left=False,
    )

    # Bottom-right bank.
    place_cloud(
        canvas,
        (
            (611, 586, 70, 42),
            (678, 548, 74, 56),
            (750, 527, 86, 67),
            (824, 551, 92, 59),
            (891, 582, 65, 45),
            (758, 602, 148, 56),
        ),
        opacity=250, shade_strength=1.14, warm_strength=0.9,
        sun_from_left=True,
    )

    # Sparse, tiny twinkles. Most sit in quiet sky; a handful catch the cloud
    # tops so the background shares the sprites' warm-star detail.
    for cx, cy, radius, angle in (
        (285, 90, 2.7, 12),
        (500, 116, 2.2, -10),
        (670, 174, 2.0, 20),
        (744, 233, 1.3, -6),
        (126, 272, 1.8, 24),
        (246, 374, 1.4, 9),
        (330, 450, 2.35, -12),
        (566, 453, 1.7, 8),
        (438, 477, 1.25, 4),
    ):
        add_sparkle(canvas, cx, cy, radius, angle)

    # Blue-lavender side bands keep both paddle columns readable while the
    # bright cloud banks remain at the top and bottom edges.
    add_lane_shade(canvas)

    # Final veil and downsample. Converting through RGB guarantees that every
    # saved alpha value is exactly 255.
    canvas = canvas.convert("RGB")
    canvas = canvas.resize((W, H), Image.Resampling.LANCZOS)
    return canvas.convert("RGBA")


def main() -> None:
    image = build()
    image.save(OUTPUT, "PNG", optimize=True)
    print(f"wrote {OUTPUT} ({image.width}x{image.height}, RGBA)")


if __name__ == "__main__":
    main()
'''

def load_renderer(source: str, label: str) -> dict[str, object]:
    """Execute an embedded renderer without running its file-writing main."""
    namespace: dict[str, object] = {
        "__name__": f"pingpong_art_{label}_renderer",
        "__file__": __file__,
    }
    exec(compile(source, f"<{label} renderer>", "exec"), namespace)
    return namespace


def build() -> Image.Image:
    ball = load_renderer(BALL_RENDERER, "ball")
    pop = load_renderer(POP_RENDERER, "pop")
    cloud = load_renderer(CLOUD_RENDERER, "cloud")
    backdrop = load_renderer(BACKGROUND_RENDERER, "background")

    ball_sheet = ball["finalize"](ball["compose_sheet"]())
    idle = cloud["render_frame"]("idle")
    hit = cloud["render_frame"]("hit")
    background = backdrop["build"]()

    if ball_sheet.size != (259, 89):
        raise RuntimeError(f"unexpected ball sheet size: {ball_sheet.size}")
    if idle.size != (48, 360) or hit.size != (48, 360):
        raise RuntimeError(f"unexpected paddle frame size: {idle.size}, {hit.size}")
    if background.size != (800, 600) or background.mode != "RGBA":
        raise RuntimeError(
            f"unexpected background: {background.mode} {background.size}"
        )
    if background.getchannel("A").getextrema() != (255, 255):
        raise RuntimeError("background must be fully opaque")

    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    # Direct paste keeps every source RGBA value, including hidden RGB in
    # fully transparent texels. Unused sheet areas stay (0, 0, 0, 0).
    sheet.paste(ball_sheet, (0, 0))
    sheet.paste(idle, (81, 90))
    sheet.paste(hit, (130, 90))
    sheet.paste(background, (260, 0))
    for index, (name, x, y, width, height) in enumerate(POP_FRAMES):
        frame = pop["finalize_frame"](pop["render_frame"](index))
        if frame.size != (width, height):
            raise RuntimeError(
                f"unexpected pop frame size: {name} {frame.size}"
            )
        sheet.paste(frame, (x, y))

    # Canonicalise every pixel outside a frame rectangle to (0, 0, 0, 0).
    # The 1 px vertical gutter at x=259, the pop gutters, the y=450 / y=515
    # separator rows and the area below the pop block stay fully transparent.
    coverage = Image.new("L", (SHEET_W, SHEET_H), 0)
    coverage_draw = ImageDraw.Draw(coverage)
    for _name, x, y, width, height in FRAMES:
        coverage_draw.rectangle((x, y, x + width - 1, y + height - 1), fill=255)
    clear = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    sheet = Image.composite(sheet, clear, coverage)

    if sheet.size != (SHEET_W, SHEET_H) or sheet.mode != "RGBA":
        raise RuntimeError(f"unexpected output: {sheet.mode} {sheet.size}")

    # Structural self-checks: the layout contract is part of the build.
    for index, first in enumerate(FRAMES):
        _, ax, ay, aw, ah = first
        for second in FRAMES[index + 1:]:
            _, bx, by, bw, bh = second
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                raise RuntimeError(f"{first[0]} overlaps {second[0]}")
    if sheet.crop((259, 0, 260, SHEET_H)).getchannel("A").getbbox() is not None:
        raise RuntimeError("the x=259 gutter must be fully transparent")
    for y in (450, 515):
        if sheet.crop((0, y, 259, y + 1)).getchannel("A").getbbox() is not None:
            raise RuntimeError(f"the y={y} separator row must be transparent")
    for x in (64, 129, 194):
        if sheet.crop((x, 451, x + 1, 580)).getchannel("A").getbbox() is not None:
            raise RuntimeError(f"the x={x} pop gutter must be transparent")
    if sheet.crop((0, 580, 259, SHEET_H)).getchannel("A").getbbox() is not None:
        raise RuntimeError("the area below the pop frames must be transparent")
    outside_alpha = ImageChops.multiply(
        sheet.getchannel("A"),
        coverage.point(lambda value: 255 - value),
    )
    if outside_alpha.getbbox() is not None:
        raise RuntimeError("all pixels outside listed frames must be transparent")
    backdrop_alpha = sheet.crop((260, 0, SHEET_W, SHEET_H)).getchannel("A")
    if backdrop_alpha.getextrema() != (255, 255):
        raise RuntimeError("the background frame must be fully opaque")
    for name, x, y, width, height in FRAMES:
        if sheet.crop((x, y, x + width, y + height)).getchannel("A").getbbox() is None:
            raise RuntimeError(f"{name} must contain visible pixels")
    for name, x, y, width, height in POP_FRAMES:
        frame_alpha = sheet.crop((x, y, x + width, y + height)).getchannel("A")
        left, top, right, bottom = frame_alpha.getbbox()
        if left < 2 or top < 2 or width - right < 2 or height - bottom < 2:
            raise RuntimeError(
                f"{name} must keep at least a 2 px transparent content margin"
            )
    return sheet


def write_spritepos() -> None:
    """Write the whitespace-delimited frame/animation manifest next to the PNG."""
    frame_names = {entry[0] for entry in FRAMES}

    for name, fps, mode, clip_frames in ANIMATIONS:
        if mode not in ("loop", "once"):
            raise RuntimeError(f"{name}: mode must be loop or once")
        if fps <= 0:
            raise RuntimeError(f"{name}: fps must be positive")
        missing = [frame for frame in clip_frames if frame not in frame_names]
        if missing:
            raise RuntimeError(f"{name}: missing frames: {missing}")

    # Background first for a readable manifest; other frames keep sheet order.
    ordered_frames = [entry for entry in FRAMES if entry[0] == "background"]
    ordered_frames += [entry for entry in FRAMES if entry[0] != "background"]

    lines = [
        "[meta]",
        "version 1",
        "texture pingpong-art.png",
        f"sheet {SHEET_W} {SHEET_H}",
        "",
        "[frames]",
    ]

    for name, x, y, width, height in ordered_frames:
        lines.append(f"{name} {x} {y} {width} {height}")

    lines += ["", "[animations]"]

    for name, fps, mode, clip_frames in ANIMATIONS:
        lines.append(f"{name} {fps} {mode} {' '.join(clip_frames)}")

    SPRITEPOS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    image = build()
    image.save(OUTPUT, format="PNG", compress_level=9, optimize=False)
    write_spritepos()
    print(f"Wrote {OUTPUT} ({image.width}x{image.height}, RGBA)")
    print(f"Wrote {SPRITEPOS}")


if __name__ == "__main__":
    main()
