"""Prüft alle Kalender aus config/config.toml und listet die nächsten Termine.

Aufruf:  python scripts/check_calendars.py
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eink_calendar.calendar_source import load_calendar  # noqa: E402
from eink_calendar.config import ConfigError, load_config  # noqa: E402

SHOW = 5


def main() -> int:
    try:
        cfg = load_config()
    except ConfigError as exc:
        print(f"FEHLER in der Konfiguration: {exc}")
        return 2

    tz = ZoneInfo(cfg.timezone)
    start = date.today()
    end = start + timedelta(days=cfg.days_ahead)
    failed = 0

    for cal in cfg.calendars:
        print(f"\n=== {cal.name}  [Icon: {cal.icon}]")
        print(f"    Quelle: {cal.source}")
        if not cal.enabled:
            print("    (deaktiviert)")
            continue
        try:
            events = sorted(load_calendar(cal, start, end, tz), key=lambda e: str(e.start))
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"    FEHLER: {exc}")
            continue
        print(f"    OK – {len(events)} Termine in den nächsten {cfg.days_ahead} Tagen")
        for ev in events[:SHOW]:
            when = ev.start.strftime("%a %d.%m.") + ("  ganztägig" if ev.all_day else ev.start.strftime("  %H:%M"))
            print(f"      {when:<20} [{ev.icon}] {ev.title}")
        if len(events) > SHOW:
            print(f"      ... und {len(events) - SHOW} weitere")

    print("\nAlle Kalender OK." if not failed else f"\n{failed} Kalender mit Fehlern.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
