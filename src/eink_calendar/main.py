"""Einstiegspunkt: Konfig laden -> Termine holen -> Bild rendern -> auf Display ausgeben.

    python -m eink_calendar           # einmal komplett zeichnen und beenden
    python -m eink_calendar --loop    # Dauerbetrieb (systemd): Uhr jede Minute,
                                      # komplettes Bild alle full_refresh_minutes
    python -m eink_calendar --clear   # Display leeren (z. B. vor längerer Lagerung)
"""
from __future__ import annotations

import logging
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from .calendar_source import load_all_events
from .config import Config, ConfigError, load_config
from .display.mock_display import MockDisplay
from .rendering.layout import render_agenda, render_clock

log = logging.getLogger("eink_calendar")


def _now(tz: ZoneInfo) -> datetime:
    return datetime.now(tz).replace(second=0, microsecond=0, tzinfo=None)


def _make_display(cfg: Config):
    if cfg.mock:
        return MockDisplay()
    from .display.waveshare_display import WaveshareDisplay

    return WaveshareDisplay(cfg.display_model)


def _full_due(cfg: Config, now: datetime, last_full: datetime | None) -> bool:
    if last_full is None or now.date() != last_full.date():
        return True
    if (now - last_full).total_seconds() >= cfg.full_refresh_minutes * 60:
        return True  # falls eine Minute verpasst wurde
    return (now.hour * 60 + now.minute) % cfg.full_refresh_minutes == 0


def _sleep_until_next_minute() -> None:
    t = time.time()
    time.sleep(60 - (t % 60) + 0.05)


def run_once(cfg: Config) -> int:
    tz = ZoneInfo(cfg.timezone)
    now = _now(tz)
    events, errors = load_all_events(cfg, now.date())
    log.info("%d Termine geladen.", len(events))
    image = render_agenda(events, _now(tz), grayscale=cfg.grayscale, clock=cfg.clock, updated=now)
    path = MockDisplay().show(image)
    log.info("Vorschau: %s", path)
    if not cfg.mock:
        _make_display(cfg).show(image)
    return 1 if errors else 0


def run_loop(cfg: Config, max_iterations: int | None = None) -> None:
    """Dauerbetrieb. Ein Fehler in einer Runde beendet die Schleife nicht."""
    tz = ZoneInfo(cfg.timezone)
    display = _make_display(cfg)
    events: list = []
    fetched: datetime | None = None
    last_full: datetime | None = None
    iteration = 0

    while max_iterations is None or iteration < max_iterations:
        iteration += 1
        now = _now(tz)
        try:
            if _full_due(cfg, now, last_full):
                events, errors = load_all_events(cfg, now.date())
                fetched = now
                log.info("Komplett-Refresh: %d Termine, %d Fehler.", len(events), len(errors))
                now = _now(tz)  # Abfrage kann einige Sekunden dauern
                display.show(render_agenda(events, now, grayscale=cfg.grayscale,
                                           clock=cfg.clock, updated=fetched))
                last_full = now
            elif cfg.clock:
                region, (x, y) = render_clock(now)
                display.show_partial(region, x, y)
                log.info("Uhr: %s", f"{now:%H:%M}")
        except Exception:  # noqa: BLE001
            log.exception("Fehler in der Aktualisierung – nächster Versuch in einer Minute.")

        if max_iterations is None or iteration < max_iterations:
            _sleep_until_next_minute()


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

    if "--loop" in argv:
        run_loop(cfg)
        return 0

    return run_once(cfg)


if __name__ == "__main__":
    sys.exit(run())
