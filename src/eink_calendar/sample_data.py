"""Beispieltermine für die Vorschau ohne echten Kalender (relativ zu heute)."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from .calendar_source.models import Event


def sample_events(today: date) -> list[Event]:
    def timed(icon, offset, hh, mm, title, dur_h=1):
        start = datetime.combine(today + timedelta(days=offset), time(hh, mm))
        return Event(title, start, start + timedelta(hours=dur_h), icon)

    def allday(icon, offset, title, days=1):
        d = today + timedelta(days=offset)
        return Event(title, d, d + timedelta(days=days), icon, all_day=True)

    return [
        allday("fyn", -2, "Messe Hamburg", days=3),
        allday("beide", 0, "Müllabfuhr Gelbe Tonne"),
        timed("lena", 0, 9, 0, "Zahnarzt Dr. Meier"),
        timed("beide", 0, 18, 0, "Abendessen bei Oma"),
        timed("handball", 1, 14, 0, "HSG Musterstadt - TV Beispiel"),
        timed("beide", 1, 15, 0, "Geburtstag Lisa"),
        allday("beide", 2, "Ausflug Ostsee"),
        timed("lena", 3, 7, 30, "Frühdienst"),
        timed("termin", 3, 19, 0, "Kino: Ein sehr langer Filmtitel, der gekürzt werden muss"),
        timed("handball", 5, 18, 0, "Training"),
        timed("lena", 6, 17, 0, "Yoga"),
    ]
