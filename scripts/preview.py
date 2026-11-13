"""Erzeugt eine Vorschau nach output/preview.png.

    python scripts/preview.py          # mit Beispieldaten
    python scripts/preview.py --live   # mit den echten Kalendern aus config/config.toml
    python scripts/preview.py --mono   # reines Schwarz/Weiß statt 4 Graustufen
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eink_calendar.display.mock_display import MockDisplay  # noqa: E402
from eink_calendar.rendering.layout import render_agenda  # noqa: E402


def main() -> None:
    now = datetime.now().replace(second=0, microsecond=0)
    if "--live" in sys.argv:
        from eink_calendar.calendar_source import load_all_events
        from eink_calendar.config import load_config

        events, errors = load_all_events(load_config(), now.date())
        for err in errors:
            print(f"WARNUNG: {err}")
    else:
        from eink_calendar.sample_data import sample_events

        events = sample_events(now.date())

    path = MockDisplay().show(render_agenda(events, now, grayscale="--mono" not in sys.argv))
    print(f"Vorschau gespeichert: {path}")


if __name__ == "__main__":
    main()
