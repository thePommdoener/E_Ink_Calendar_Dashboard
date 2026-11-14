"""Agenda-Ansicht: links Datum + Monatskalender, rechts Terminliste ab heute.

Entspricht design/ansicht_agenda.txt.

Zwei Farbmodi:
- grayscale=True : 4 Graustufen (Weiß, Hellgrau, Dunkelgrau, Schwarz) – nutzt den
                   4-Gray-Modus des Waveshare 7.5" V2.
- grayscale=False: reines Schwarz/Weiß (schneller, Teil-Refresh möglich).

Text wird immer ohne Kantenglättung gezeichnet, damit er auf dem E-Paper scharf bleibt.
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from PIL import Image, ImageDraw

from ..calendar_source.models import DayEntry, Event, entries_for_day
from .fonts import BOLD, CONDENSED, CONDENSED_BOLD, REGULAR, font
from .icons import ICON_H, draw_icon, icon_width

WIDTH, HEIGHT = 800, 480

# Exakte Graustufen des Waveshare-Treibers (epd7in5_V2.GRAY1..GRAY4)
WHITE, LIGHT, DARK, BLACK = 0xFF, 0xC0, 0x80, 0x00

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
WD_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

# --- Geometrie --------------------------------------------------------------
LEFT_W = 248                 # Breite linke Spalte (Vielfaches von 8 -> Teil-Refresh)
CLOCK_BOX = (0, 0, LEFT_W, 80)   # Uhrbereich (x0, y0, x1, y1), nur Schwarz/Weiß
DIVIDER_X = LEFT_W
RIGHT_X = LEFT_W + 16        # Start rechte Spalte
RIGHT_END = WIDTH - 12
TOP = 10
BOTTOM = HEIGHT - 8

DAY_HEADER_H = 30            # Tagesüberschrift inkl. Linie/Balken
ROW_H = 26                   # Höhe einer Terminzeile
DAY_GAP = 8                  # Abstand zwischen Tagen
EMPTY_DAY_H = 26             # Einzeiler für Tage ohne Termine
BADGE_W = 34
TIME_X = RIGHT_X + BADGE_W + 12
TITLE_X = TIME_X + 104
MAX_DAYS = 14


@dataclass(frozen=True)
class Palette:
    """Farben je Modus. Im S/W-Modus fallen Grautöne auf Schwarz bzw. Weiß zurück."""
    gray: bool
    ink: int = BLACK        # Haupttext
    muted: int = DARK       # Nebensächliches (KW, "ganztägig", vergangene Termine)
    band: int = LIGHT       # Hintergrund-Balken

    @staticmethod
    def for_mode(grayscale: bool) -> "Palette":
        if grayscale:
            return Palette(gray=True)
        return Palette(gray=False, muted=BLACK, band=WHITE)


# --- Hilfsfunktionen --------------------------------------------------------
def _text_w(draw: ImageDraw.ImageDraw, text: str, fnt) -> int:
    return int(draw.textlength(text, font=fnt))


def _centered(draw, cx: int, y: int, text: str, fnt, fill=BLACK) -> None:
    draw.text((cx - _text_w(draw, text, fnt) // 2, y), text, font=fnt, fill=fill)


def _ellipsize(draw, text: str, fnt, max_w: int) -> str:
    if _text_w(draw, text, fnt) <= max_w:
        return text
    while text and _text_w(draw, text + "…", fnt) > max_w:
        text = text[:-1]
    return text.rstrip() + "…"


# --- Linke Spalte -----------------------------------------------------------
def _draw_clock(draw: ImageDraw.ImageDraw, now: datetime, ox: int = 0, oy: int = 0) -> None:
    """Große Uhr oben links. Nur Schwarz auf Weiß – wird minütlich per Teil-Refresh erneuert."""
    x0, y0, x1, y1 = CLOCK_BOX
    draw.rectangle((x0 - ox, y0 - oy, x1 - 1 - ox, y1 - 1 - oy), fill=WHITE)
    _centered(draw, (x0 + x1) // 2 - ox, y0 + 6 - oy, f"{now:%H:%M}", font(BOLD, 62), BLACK)


def _draw_left(draw: ImageDraw.ImageDraw, p: Palette, today: date, now: datetime,
               updated: datetime, clock: bool) -> None:
    cx = LEFT_W // 2

    if clock:
        _draw_clock(draw, now)
        draw.line((20, CLOCK_BOX[3] + 2, LEFT_W - 20, CLOCK_BOX[3] + 2), fill=p.muted, width=1)
        top = CLOCK_BOX[3] + 8
        day_font, day_h = font(BOLD, 84), 88
    else:
        top = TOP + 14
        day_font, day_h = font(BOLD, 112), 132

    _centered(draw, cx, top, WEEKDAYS[today.weekday()].upper(), font(BOLD, 24), p.ink)
    _centered(draw, cx, top + 26, str(today.day), day_font, p.ink)
    y = top + 26 + day_h
    _centered(draw, cx, y, f"{MONTHS[today.month - 1].upper()} {today.year}", font(BOLD, 19), p.ink)
    _centered(draw, cx, y + 24, f"KW {today.isocalendar().week}", font(REGULAR, 16), p.muted)

    sep_y = y + 48
    draw.line((20, sep_y, LEFT_W - 20, sep_y), fill=p.muted, width=1)

    # Monatskalender
    cell_w, cell_h = 30, 23
    x0 = cx - (7 * cell_w) // 2
    y0 = sep_y + 8
    f_head, f_num = font(CONDENSED_BOLD, 15), font(CONDENSED, 16)
    for i, wd in enumerate(WD_SHORT):
        _centered(draw, x0 + i * cell_w + cell_w // 2, y0, wd, f_head, p.ink)
    for r, week in enumerate(calendar.Calendar().monthdayscalendar(today.year, today.month)):
        y = y0 + (r + 1) * cell_h
        if p.gray and today.day in week:
            # aktuelle Woche hellgrau hinterlegen
            draw.rounded_rectangle((x0 - 2, y - 3, x0 + 7 * cell_w + 1, y + cell_h - 4), radius=4, fill=p.band)
        for c, d in enumerate(week):
            if not d:
                continue
            mx = x0 + c * cell_w + cell_w // 2
            if d == today.day:
                draw.rectangle((mx - 13, y - 2, mx + 13, y + cell_h - 5), fill=p.ink)
                _centered(draw, mx, y, str(d), font(CONDENSED_BOLD, 16), fill=WHITE)
            else:
                past = d < today.day
                _centered(draw, mx, y, str(d), f_num, p.muted if past else p.ink)

    _centered(draw, cx, BOTTOM - 16, f"Kalender-Stand: {updated:%d.%m. %H:%M}", font(REGULAR, 12), p.muted)


# --- Rechte Spalte ----------------------------------------------------------
def _day_title(day: date, today: date) -> str:
    base = f"{WD_SHORT[day.weekday()]} {day:%d.%m.}"
    if day == today:
        return f"HEUTE  ·  {base}"
    if day == today + timedelta(days=1):
        return f"MORGEN  ·  {base}"
    return base


def _day_height(n_entries: int) -> int:
    return DAY_HEADER_H + max(n_entries, 0) * ROW_H


def _draw_day_header(draw, p: Palette, y: int, title: str, is_today: bool, empty: bool) -> None:
    f_title = font(BOLD, 18)
    if p.gray:
        # Graustufen: Balken statt Linie – heute schwarz, sonst hellgrau
        bg, fg = (p.ink, WHITE) if is_today else (p.band, p.ink)
        draw.rectangle((RIGHT_X - 6, y - 1, RIGHT_END, y + 24), fill=bg)
        draw.text((RIGHT_X, y + 1), title, font=f_title, fill=fg)
        empty_fill = WHITE if is_today else p.muted
    else:
        draw.text((RIGHT_X, y), title, font=f_title, fill=p.ink)
        draw.line((RIGHT_X, y + 24, RIGHT_END, y + 24), fill=p.ink, width=3 if is_today else 1)
        empty_fill = p.ink
    if empty:
        f = font(REGULAR, 15)
        txt = "keine Termine"
        draw.text((RIGHT_END - 6 - _text_w(draw, txt, f), y + 4), txt, font=f, fill=empty_fill)


def _draw_entry(draw, p: Palette, y: int, e: DayEntry, now: datetime) -> None:
    past = e.ends_at is not None and e.ends_at <= now
    color = p.muted if past else p.ink

    ix = RIGHT_X + (BADGE_W - icon_width(e.icon)) // 2
    iy = y + (ROW_H - ICON_H) // 2
    draw_icon(draw, ix, iy, e.icon, fill=color)

    all_day = e.time_label == "ganztägig"
    f_time = font(CONDENSED, 17) if all_day else font(REGULAR, 18)
    draw.text((TIME_X, y + 2), e.time_label, font=f_time, fill=p.muted if all_day else color)
    f_title = font(REGULAR, 18)
    draw.text((TITLE_X, y + 2), _ellipsize(draw, e.title, f_title, RIGHT_END - TITLE_X), font=f_title, fill=color)


def _draw_empty_day(draw, p: Palette, y: int, title: str) -> None:
    """Einzeiler: Datum links, "keine Termine" auf Höhe der Titel."""
    draw.text((RIGHT_X, y + 2), title, font=font(BOLD, 16), fill=p.muted)
    draw.text((TITLE_X, y + 3), "keine Termine", font=font(REGULAR, 15), fill=p.muted)


def _draw_right(draw: ImageDraw.ImageDraw, p: Palette, events: list[Event], now: datetime) -> None:
    today = now.date()
    y = TOP + 6
    limit = BOTTOM
    prev_empty = False

    for offset in range(MAX_DAYS):
        day = today + timedelta(days=offset)
        entries = entries_for_day(events, day)

        if not entries and day != today:
            if y + EMPTY_DAY_H > limit:
                break
            _draw_empty_day(draw, p, y, _day_title(day, today))
            y += EMPTY_DAY_H
            prev_empty = True
            continue

        if offset > 0 and prev_empty:
            y += DAY_GAP // 2  # etwas Luft nach einem Block leerer Tage
        prev_empty = False
        needed = _day_height(len(entries))

        if y + needed > limit:
            if offset == 0:
                # Heute passt nicht komplett: kürzen mit "+ X weitere"
                fit = max((limit - y - DAY_HEADER_H) // ROW_H - 1, 0)
                hidden = len(entries) - fit
                _draw_day_header(draw, p, y, _day_title(day, today), True, False)
                y += DAY_HEADER_H
                for e in entries[:fit]:
                    _draw_entry(draw, p, y, e, now)
                    y += ROW_H
                draw.text((TIME_X, y + 2), f"+ {hidden} weitere", font=font(BOLD, 16), fill=p.ink)
            break  # Regel: lieber ganzen Tag weglassen als abschneiden

        _draw_day_header(draw, p, y, _day_title(day, today), day == today, not entries)
        y += DAY_HEADER_H
        for e in entries:
            _draw_entry(draw, p, y, e, now)
            y += ROW_H
        y += DAY_GAP


# --- Öffentliche Funktionen ------------------------------------------------
def render_agenda(events: list[Event], now: datetime, grayscale: bool = True,
                  clock: bool = False, updated: datetime | None = None) -> Image.Image:
    """Erzeugt das komplette 800x480-Bild.

    clock   – große Uhr oben links (für den Minutentakt per Teil-Refresh)
    updated – Zeitpunkt der letzten Kalenderabfrage (Standard: now)
    Rückgabe: Modus "L" mit genau 4 Grauwerten (grayscale) bzw. Modus "1" (S/W).
    """
    p = Palette.for_mode(grayscale)
    img = Image.new("L", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"  # keine Kantenglättung -> nur die 4 erlaubten Grauwerte

    _draw_left(draw, p, now.date(), now, updated or now, clock)
    draw.line((DIVIDER_X, TOP, DIVIDER_X, BOTTOM), fill=p.muted if p.gray else p.ink, width=2)
    _draw_right(draw, p, events, now)

    if not grayscale:
        return img.point(lambda v: 255 if v >= 128 else 0).convert("1", dither=Image.Dither.NONE)
    return img


def render_clock(now: datetime) -> tuple[Image.Image, tuple[int, int]]:
    """Nur der Uhrbereich als S/W-Bild + linke obere Ecke – für den Teil-Refresh."""
    x0, y0, x1, y1 = CLOCK_BOX
    img = Image.new("L", (x1 - x0, y1 - y0), WHITE)
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    _draw_clock(draw, now, ox=x0, oy=y0)
    return img.convert("1", dither=Image.Dither.NONE), (x0, y0)
