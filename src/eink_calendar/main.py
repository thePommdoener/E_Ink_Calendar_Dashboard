"""Einstiegspunkt: Konfig laden -> Termine holen -> Bild rendern -> auf Display ausgeben.

    python -m eink_calendar           # normaler Lauf (wie der systemd-Timer)
    python -m eink_calendar --clear   # Display leeren (z. B. vor längerer Lagerung)
"""
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


def run(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        cfg = load_config()
    except ConfigError as exc:
        log.error("%s", exc)
        return 2

    if "--clear" in argv:
        from .display.waveshare_display import WaveshareDisplay

        WaveshareDisplay(cfg.display_model).clear()
        log.info("Display geleert.")
        return 0

    now = datetime.now(ZoneInfo(cfg.timezone)).replace(second=0, microsecond=0, tzinfo=None)
    events, errors = load_all_events(cfg, now.date())
    log.info("%d Termine aus %d Kalendern geladen.", len(events), sum(c.enabled for c in cfg.calendars))

    image = render_agenda(events, now, grayscale=cfg.grayscale)

    # Vorschau immer speichern – praktisch zum Nachsehen per scp
    path = MockDisplay().show(image)
    log.info("Vorschau: %s", path)

    if not cfg.mock:
        from .display.waveshare_display import WaveshareDisplay

        WaveshareDisplay(cfg.display_model).show(image)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(run())
