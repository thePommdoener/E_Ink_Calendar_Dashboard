"""Liest Termine aus ICS-Abos (URL) oder lokalen .ics-Dateien.

Funktioniert für alle Kalender, die einen ICS-/webcal-Link anbieten:
öffentliche iCloud-Kalender, AWR-Abfuhrkalender, Google, Feiertage, ...
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events
import requests

from ..config import CalendarConfig
from .cache import fetch_with_cache
from .models import Event
from .rules import apply_title_rules

TIMEOUT_S = 20


def fetch_ics(cal: CalendarConfig) -> bytes:
    """Rohdaten holen: Datei lesen bzw. URL laden (mit Cache als Fallback)."""
    if cal.file:
        return cal.file.read_bytes()

    def _download() -> bytes:
        resp = requests.get(cal.url, timeout=TIMEOUT_S, headers={"User-Agent": "eink-calendar/1.0"})
        resp.raise_for_status()
        return resp.content

    return fetch_with_cache(cal.name, cal.url, _download, ".ics")


def _to_local(value: date | datetime, tz: ZoneInfo) -> date | datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=tz)
        return value.astimezone(tz)
    return value


def parse_events(cal: CalendarConfig, raw: bytes, start: date, end: date, tz: ZoneInfo) -> list[Event]:
    calendar = icalendar.Calendar.from_ical(raw)
    events: list[Event] = []
    for comp in recurring_ical_events.of(calendar).between(start, end):
        if str(comp.get("STATUS", "")).upper() == "CANCELLED":
            continue
        dt_start = comp.decoded("DTSTART")
        if "DTEND" in comp:
            dt_end = comp.decoded("DTEND")
        elif "DURATION" in comp:
            dt_end = dt_start + comp.decoded("DURATION")
        else:
            dt_end = dt_start + (timedelta(days=1) if not isinstance(dt_start, datetime) else timedelta(0))

        all_day = not isinstance(dt_start, datetime)
        icon, title = apply_title_rules(cal, str(comp.get("SUMMARY", "(ohne Titel)")))
        events.append(Event(
            title=title,
            start=_to_local(dt_start, tz),
            end=_to_local(dt_end, tz),
            icon=icon,
            all_day=all_day,
            calendar=cal.name,
        ))
    return events


def load_events(cal: CalendarConfig, start: date, end: date, tz: ZoneInfo) -> list[Event]:
    return parse_events(cal, fetch_ics(cal), start, end, tz)
