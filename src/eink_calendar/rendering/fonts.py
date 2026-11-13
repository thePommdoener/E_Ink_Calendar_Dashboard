"""Lädt Schriften aus assets/fonts/."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

FONT_DIR = Path(__file__).resolve().parents[3] / "assets" / "fonts"

REGULAR = "DejaVuSans.ttf"
BOLD = "DejaVuSans-Bold.ttf"
CONDENSED = "DejaVuSansCondensed.ttf"
CONDENSED_BOLD = "DejaVuSansCondensed-Bold.ttf"


@lru_cache(maxsize=None)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)
