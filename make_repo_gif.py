#!/usr/bin/env python3
"""Generate a lightweight animated GIF for a GitHub repository.

This script renders a simple repository summary card with a moving accent and
animated bars. Update the LANGUAGES list if you want to reflect the actual
language breakdown for this repo.
"""

from __future__ import annotations

import os
from math import sin, pi
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image, ImageDraw, ImageFont

REPO_NAME = "habeebikram2014-droid/ayam"
OUTPUT_PATH = Path("repo_gif.gif")

# Replace this list with real language percentages if you have them.
LANGUAGES: List[Tuple[str, float, str]] = [
    ("TypeScript", 46, "#3178C6"),
    ("JavaScript", 29, "#F7DF1E"),
    ("CSS", 15, "#563D7C"),
    ("HTML", 10, "#E34C26"),
]


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def gradient_background(size: Tuple[int, int], phase: float) -> Image.Image:
    width, height = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(height):
        for x in range(width):
            r = int(14 + (x / width) * 38 + sin((y / height) * 3.0 + phase) * 18)
            g = int(22 + (y / height) * 46 + cos((x / width) * 2.5 + phase) * 16)
            b = int(40 + (x / width) * 66)
            px[x, y] = (min(r, 255), min(g, 255), min(b, 255))
    return img


def draw_repo_card(frame_index: int, total_frames: int) -> Image.Image:
    width, height = 900, 500
    bg = gradient_background((width, height), frame_index / total_frames * 2 * pi)
    draw = ImageDraw.Draw(bg)

    # Soft overlay panel
    panel = (40, 34, width - 40, height - 34)
    draw.rounded_rectangle(panel, radius=28, fill=(15, 21, 33, 180), outline=(255, 255, 255, 56), width=2)

    # Accent orb with motion
    orb_x = 130 + int(sin(frame_index / total_frames * 2 * pi) * 28)
    orb_y = 116 + int(cos(frame_index / total_frames * 2 * pi) * 18)
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((orb_x - 80, orb_y - 80, orb_x + 80, orb_y + 80), fill=(120, 200, 255, 90))
    bg = Image.alpha_composite(bg.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(bg)

    # Text
    title_font = load_font(30)
    repo_font = load_font(22)
    label_font = load_font(18)
    bar_font = load_font(16)

    draw.text((80, 70), "GitHub Repository", fill=(170, 210, 255), font=title_font)
    draw.text((80, 112), REPO_NAME, fill=(255, 255, 255), font=repo_font)

    # Ring style decorative element on the right
    ring_center = (720, 180)
    ring_radius = 92
    for i in range(24):
        angle = i / 24 * 2 * pi + frame_index / total_frames * 2 * pi
        x1 = ring_center[0] + int(cos(angle) * (ring_radius - 6))
        y1 = ring_center[1] + int(sin(angle) * (ring_radius - 6))
        x2 = ring_center[0] + int(cos(angle) * (ring_radius + 18))
        y2 = ring_center[1] + int(sin(angle) * (ring_radius + 18))
        draw.line((x1, y1, x2, y2), fill=(120, 200, 255, 180), width=3)
    draw.ellipse((ring_center[0] - 42, ring_center[1] - 42, ring_center[0] + 42, ring_center[1] + 42), outline=(160, 177, 255), width=2)

    # Language bars
    bar_x = 88
    bar_y = 190
    bar_w = 500
    bar_h = 20
    total = sum(v for _, v, _ in LANGUAGES)

    for idx, (name, percentage, color) in enumerate(LANGUAGES):
        # animate compression slightly
        pulse = 1.0 + 0.06 * sin(frame_index / total_frames * 2 * pi + idx)
        bar_len = int((percentage / total) * bar_w * pulse)
        y = bar_y + idx * 56
        draw.rounded_rectangle((bar_x, y, bar_x + bar_w, y + bar_h), radius=10, fill=(255, 255, 255, 30), outline=(255, 255, 255, 24))
        draw.rounded_rectangle((bar_x, y, bar_x + bar_len, y + bar_h), radius=10, fill=color)
        draw.text((bar_x + 6, y - 2), name, fill=(230, 233, 245), font=bar_font)
        draw.text((bar_x + bar_w - 46, y - 2), f"{percentage}%", fill=(230, 233, 245), font=bar_font)

    # Footer info
    draw.text((80, 430), "repo summary / animated preview", fill=(160, 180, 220), font=label_font)
    draw.text((680, 420), "GIF", fill=(122, 179, 255), font=load_font(26))

    return bg


def build_gif(output_path: Path) -> None:
    total_frames = 24
    frames: List[Image.Image] = []
    for i in range(total_frames):
        frames.append(draw_repo_card(i, total_frames))

    first = frames[0]
    first.save(
        output_path,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=120,
        loop=0,
        optimize=False,
        disposal=2,
    )


if __name__ == "__main__":
    build_gif(OUTPUT_PATH)
    print(f"Created {OUTPUT_PATH.resolve()}")
