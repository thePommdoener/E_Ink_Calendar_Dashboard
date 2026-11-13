"""Monochrome Piktogramme, pixelgenau für E-Paper.

Farb-Emojis funktionieren auf einem Schwarz/Weiß-Display nicht, deshalb werden
die Symbole hier als einfache Vektorformen gezeichnet. Alle Icons sind 22 px hoch.

Neues Icon hinzufügen: Zeichenfunktion schreiben und in ICONS eintragen.
Der Name ist dann in config.toml unter `icon = "..."` nutzbar.
"""
from __future__ import annotations

import math
from typing import Callable

from PIL import ImageDraw

ICON_H = 22
ICON_GAP = 3

DrawFn = Callable[[ImageDraw.ImageDraw, int, int, int], None]


def _white(draw) -> int:
    """Hintergrundfarbe für Aussparungen (1 im S/W-Bild, 255 im Graustufenbild)."""
    return 1 if draw.mode == "1" else 255


def _head(draw, x, y, fill) -> None:
    draw.ellipse((x + 3, y, x + 10, y + 7), fill=fill)


def _woman(draw, x, y, fill) -> None:
    _head(draw, x, y, fill)
    draw.polygon([(x + 4, y + 9), (x + 9, y + 9), (x + 13, y + 17), (x + 0, y + 17)], fill=fill)
    draw.rectangle((x + 4, y + 18, x + 5, y + 21), fill=fill)
    draw.rectangle((x + 8, y + 18, x + 9, y + 21), fill=fill)


def _man(draw, x, y, fill) -> None:
    _head(draw, x, y, fill)
    draw.rectangle((x + 2, y + 9, x + 11, y + 15), fill=fill)
    draw.rectangle((x + 3, y + 16, x + 6, y + 21), fill=fill)
    draw.rectangle((x + 7, y + 16, x + 10, y + 21), fill=fill)


def _both(draw, x, y, fill) -> None:
    _woman(draw, x, y, fill)
    _man(draw, x + 14 + ICON_GAP, y, fill)


def _handball(draw, x, y, fill) -> None:
    """Ball: Ring, Fünfeck in der Mitte, Nähte zum Rand."""
    cx, cy, r = x + 10, y + 11, 10
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=2)
    inner = [(cx + 4.5 * math.cos(math.radians(-90 + 72 * i)),
              cy + 4.5 * math.sin(math.radians(-90 + 72 * i))) for i in range(5)]
    draw.polygon(inner, fill=fill)
    for px, py in inner:
        dx, dy = px - cx, py - cy
        k = (r - 1) / math.hypot(dx, dy)
        draw.line((px, py, cx + dx * k, cy + dy * k), fill=fill, width=1)


def _termin(draw, x, y, fill) -> None:
    """Kleines Kalenderblatt – neutrales Symbol für sonstige Kalender."""
    bg = _white(draw)
    draw.rectangle((x, y + 3, x + 17, y + 21), fill=fill)
    draw.rectangle((x + 2, y + 8, x + 15, y + 19), fill=bg)
    draw.rectangle((x + 4, y + 1, x + 5, y + 5), fill=fill)
    draw.rectangle((x + 12, y + 1, x + 13, y + 5), fill=fill)
    for cx, cy in ((4, 10), (8, 10), (12, 10), (4, 14), (8, 14)):
        draw.rectangle((x + cx, y + cy, x + cx + 1, y + cy + 1), fill=fill)


def _stern(draw, x, y, fill) -> None:
    pts = [(9, 1), (11.5, 8), (19, 8), (13, 12.5), (15.5, 20), (9, 15.5),
           (2.5, 20), (5, 12.5), (-1, 8), (6.5, 8)]
    draw.polygon([(x + 1 + px, y + py) for px, py in pts], fill=fill)


def _small_ball(draw, x, y, fill) -> None:
    """Kleiner Ball (12 px) unten rechts neben einer Person: Ring + Mittelfleck + Nähte."""
    cx, cy = x + 6, y + 15
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline=fill, width=1)
    draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=fill)
    for dx, dy in ((0, -1), (1, 0.3), (0.6, 1), (-0.6, 1), (-1, 0.3)):
        draw.line((cx + dx * 2, cy + dy * 2, cx + dx * 5, cy + dy * 5), fill=fill, width=1)


def _lena_handball(draw, x, y, fill) -> None:
    _woman(draw, x, y, fill)
    _small_ball(draw, x + 16, y, fill)


def _fyn_handball(draw, x, y, fill) -> None:
    _man(draw, x, y, fill)
    _small_ball(draw, x + 15, y, fill)


def _tonne(draw, x, y, fill) -> None:
    """Mülltonne mit Deckel und Rädern."""
    bg = _white(draw)
    draw.rectangle((x, y + 2, x + 16, y + 5), fill=fill)                    # Deckel
    draw.rectangle((x + 6, y, x + 10, y + 2), fill=fill)                    # Griff
    draw.polygon([(x + 1, y + 7), (x + 15, y + 7), (x + 14, y + 19), (x + 2, y + 19)], fill=fill)
    for lx in (5, 8, 11):                                                   # Rillen
        draw.line((x + lx, y + 9, x + lx, y + 17), fill=bg, width=1)
    draw.ellipse((x + 1, y + 18, x + 5, y + 22), fill=fill)                 # Räder
    draw.ellipse((x + 11, y + 18, x + 15, y + 22), fill=fill)


# Name -> (Breite in px, Zeichenfunktion)
ICONS: dict[str, tuple[int, DrawFn]] = {
    "lena": (14, _woman),
    "fyn": (14, _man),
    "beide": (14 * 2 + ICON_GAP, _both),
    "handball": (21, _handball),
    "termin": (18, _termin),
    "stern": (20, _stern),
    "lena_handball": (29, _lena_handball),
    "fyn_handball": (28, _fyn_handball),
    "tonne": (17, _tonne),
}
DEFAULT_ICON = "termin"


def icon_width(name: str) -> int:
    return ICONS.get(name, ICONS[DEFAULT_ICON])[0]


def draw_icon(draw: ImageDraw.ImageDraw, x: int, y: int, name: str, fill: int = 0) -> None:
    """Zeichnet das Icon `name` mit linker oberer Ecke (x, y)."""
    ICONS.get(name, ICONS[DEFAULT_ICON])[1](draw, x, y, fill)
