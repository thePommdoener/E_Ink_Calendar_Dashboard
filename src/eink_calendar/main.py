"""Einstiegspunkt: Konfig laden -> Termine holen -> Bild rendern -> auf Display ausgeben."""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from .calendar_source import load_all_events
from .config import ConfigError, load_config
from .display.mock_display import MockDisplay
from .rendering.layout import render_agenda

log = logging.getLogger("eink_calendar")


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        cfg = load_config()
    except ConfigError as exc:
        log.error("%s", exc)
        return 2

    now = datetime.now(ZoneInfo(cfg.timezone)).replace(second=0, microsecond=0, tzinfo=None)
    events, errors = load_all_events(cfg, now.date())
    log.info("%d Termine aus %d Kalendern geladen.", len(events), sum(c.enabled for c in cfg.calendars))

    image = render_agenda(events, now, grayscale=cfg.grayscale)

    if cfg.mock:
        path = MockDisplay().show(image)
        log.info("Mock-Display: %s", path)
    else:
        # TODO: Waveshare-Ausgabe, sobald der Pi da ist (display/waveshare_display.py)
        log.error("Echtes Display noch nicht implementiert – setze [display] mock = true.")
        return 1
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(run())
