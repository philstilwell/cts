#!/usr/bin/env python3
"""Render narrow SurveyOL section header images for CTS weekly surveys."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

W = 1600
H = 136
SCALE = 4

FONT = "/System/Library/Fonts/Avenir Next.ttc"


def font(size: int, index: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size * SCALE, index=index)


TITLE = font(47, 8)
SUBTITLE = font(24, 5)
EYEBROW = font(15, 2)
MARK_BIG = font(45, 8)
MARK_SMALL = font(13, 2)
PILL = font(19, 2)


def sc(value: int | float) -> int:
    return round(value * SCALE)


def color(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
        alpha,
    )


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    left = color("#553E15")
    right = color("#6A4D1C")
    for x in range(W * SCALE):
        t = x / max(1, W * SCALE - 1)
        r = round(left[0] * (1 - t) + right[0] * t)
        g = round(left[1] * (1 - t) + right[1] * t)
        b = round(left[2] * (1 - t) + right[2] * t)
        draw.line([(x, 0), (x, H * SCALE)], fill=(r, g, b, 255))


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    fill: tuple[int, int, int, int],
    fnt: ImageFont.FreeTypeFont,
    anchor: str = "la",
) -> None:
    draw.text((sc(xy[0]), sc(xy[1])), value, fill=fill, font=fnt, anchor=anchor)


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int, int] | None,
    outline: tuple[int, int, int, int] | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(
        tuple(sc(v) for v in box),
        radius=sc(radius),
        fill=fill,
        outline=outline,
        width=sc(width),
    )


def shadowed_panel(draw: ImageDraw.ImageDraw) -> None:
    draw.polygon(
        [(sc(0), sc(0)), (sc(480), sc(0)), (sc(410), sc(H)), (sc(0), sc(H))],
        fill=color("#8D6F4D", 172),
    )
    draw.polygon(
        [(sc(1210), sc(0)), (sc(W), sc(0)), (sc(W), sc(H)), (sc(1135), sc(H))],
        fill=color("#8D6F4D", 110),
    )
    draw.polygon(
        [(sc(1390), sc(0)), (sc(W), sc(0)), (sc(W), sc(H)), (sc(1495), sc(H))],
        fill=color("#D8912F", 116),
    )
    rule = color("#D89232")
    draw.rectangle((0, 0, sc(W), sc(6)), fill=rule)
    draw.rectangle((0, sc(H - 6), sc(W), sc(H)), fill=rule)


def draw_microbars(draw: ImageDraw.ImageDraw, x0: int, y0: int, values: list[int]) -> None:
    for i, value in enumerate(values):
        x = x0 + i * 15
        draw.rounded_rectangle(
            (sc(x), sc(y0 + 42 - value), sc(x + 8), sc(y0 + 42)),
            radius=sc(3),
            fill=color("#EAA23B", 226),
        )
    draw.line(
        (sc(x0 - 6), sc(y0 + 45), sc(x0 + len(values) * 15 - 1), sc(y0 + 45)),
        fill=color("#F3C072", 132),
        width=sc(2),
    )


def render(
    filename: str,
    marker: str,
    marker_label: str,
    title: str,
    subtitle: str,
    pill: str,
    bars: list[int],
) -> None:
    image = Image.new("RGBA", (W * SCALE, H * SCALE), color("#553E15"))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_gradient(draw)
    shadowed_panel(draw)

    rounded(draw, (48, 24, 145, 112), 18, color("#EAA23B"), color("#F6CA77", 165), 1)
    text(draw, (96, 60), marker, color("#241708"), MARK_BIG, "mm")
    text(draw, (96, 93), marker_label, color("#33220B"), MARK_SMALL, "mm")

    text(draw, (178, 37), "CTS WEEKLY SURVEY", color("#140D04"), EYEBROW)
    text(draw, (177, 80), title, color("#FFF8EA"), TITLE, "lm")

    line_x = max(622, round(177 + TITLE.getlength(title) / SCALE + 48))
    draw.line((sc(line_x), sc(38), sc(line_x), sc(99)), fill=color("#EAA23B", 190), width=sc(3))
    text(draw, (line_x + 26, 66), subtitle, color("#F8E3BE"), SUBTITLE, "lm")

    rounded(draw, (1058, 44, 1432, 91), 23, color("#392612", 186), color("#EAA23B", 172), 1)
    text(draw, (1245, 68), pill, color("#F7CE7C"), PILL, "mm")

    draw_microbars(draw, 1466, 48, bars)

    image = image.resize((W, H), Image.Resampling.LANCZOS)
    image.save(ASSETS / filename, optimize=True)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    render(
        "featured-topic-header.png",
        "12",
        "ITEMS",
        "Featured Topic",
        "12 related survey items",
        "0-100 credence sliders",
        [30, 14, 24, 36, 18, 28, 40, 16, 34, 22, 37, 26],
    )
    render(
        "independent-items-header.png",
        "3",
        "ITEMS",
        "Independent Items",
        "Additional live survey items",
        "chosen for this week",
        [18, 39, 27],
    )


if __name__ == "__main__":
    main()
