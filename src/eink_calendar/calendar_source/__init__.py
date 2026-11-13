"""Datenquellen für Kalendertermine."""
from __future__ import annotations

import logging
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from ..config import CalendarConfig, Config
from . import handballnet_source, ics_source
from .models import Event

log = logging.getLogger(__name__)

SOURCES = {
    "ics": ics_source.load_events,
    "handballnet": handballnet_source.load_events,
}


def load_calendar(cal: CalendarConfig, start: date, end: date, tz: ZoneInfo) -> list[Event]:
    return SOURCES[cal.type](cal, start, end, tz)


def load_all_events(cfg: Config, today: date) -> tuple[list[Event], list[str]]:
    """Lädt alle aktiven Kalender. Liefert (Termine, Fehlermeldungen).

    Ein defekter Kalender bricht nicht alles ab – die übrigen werden trotzdem angezeigt.
    """
    tz = ZoneInfo(cfg.timezone)
    start, end = today, today + timedelta(days=cfg.days_ahead)
    events: list[Event] = []
    errors: list[str] = []
    for cal in cfg.calendars:
        if not cal.enabled:
            continue
        try:
            events.extend(load_calendar(cal, start, end, tz))
        except Exception as exc:  # noqa: BLE001 – ein Kalender darf nicht alles stoppen
            log.error("Kalender '%s' fehlgeschlagen: %s", cal.name, exc)
            errors.append(f"{cal.name}: {exc}")
    return events, errors
