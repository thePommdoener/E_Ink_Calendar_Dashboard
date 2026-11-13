"""Datenmodell für Termine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass(frozen=True)
class Event:
    """Ein Termin, wie er aus einem Kalender kommt.

    Bei ganztägigen Terminen sind start/end `date`-Objekte und `end` ist exklusiv
    (wie im iCalendar-Standard: ein eintägiger Termin am 13. hat end = 14.).
    `icon` ist der Name eines Piktogramms aus rendering/icons.py.
    """

    title: str
    start: date | datetime
    end: date | datetime
    icon: str = "beide"
    all_day: bool = False
    calendar: str = ""


@dataclass(frozen=True)
class DayEntry:
    """Ein Termin, aufbereitet für genau einen Tag der Anzeige."""

    icon: str
    time_label: str  # "09:00" oder "ganztägig"
    title: str  # inkl. Zähler bei mehrtägigen Terminen, z. B. "Messe 2/3"
    sort_key: tuple
    ends_at: datetime | None = None  # Ende (lokal, ohne tz) – für "bereits vorbei"


# Termine, die bis zu dieser Uhrzeit am Folgetag enden, zählen nicht für den Folgetag
_OVERNIGHT_CUTOFF = time(6, 0)


def _as_date(value: date | datetime) -> date:
    return value.date() if isinstance(value, datetime) else value


def entries_for_day(events: list[Event], day: date) -> list[DayEntry]:
    """Alle Termine eines Tages, ganztägige zuerst, dann nach Uhrzeit."""
    result: list[DayEntry] = []
    for ev in events:
        first = _as_date(ev.start)
        if ev.all_day:
            last = _as_date(ev.end) - timedelta(days=1)
        else:
            last = _as_date(ev.end)
            if isinstance(ev.end, datetime) and ev.end.time() <= _OVERNIGHT_CUTOFF and last > first:
                last -= timedelta(days=1)
        last = max(last, first)
        if not (first <= day <= last):
            continue

        total = (last - first).days + 1
        title = ev.title if total == 1 else f"{ev.title} {(day - first).days + 1}/{total}"

        if ev.all_day or day != first:
            result.append(DayEntry(ev.icon, "ganztägig", title, (0, "", title)))
        else:
            hhmm = ev.start.strftime("%H:%M")
            ends_at = ev.end.replace(tzinfo=None) if isinstance(ev.end, datetime) else None
            result.append(DayEntry(ev.icon, hhmm, title, (1, hhmm, title), ends_at))
    return sorted(result, key=lambda e: e.sort_key)
