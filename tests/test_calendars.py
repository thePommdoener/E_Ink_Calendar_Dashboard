from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from eink_calendar.calendar_source.ics_source import load_events
from eink_calendar.calendar_source.models import entries_for_day
from eink_calendar.config import CalendarConfig, ConfigError, load_config

FIXTURE = Path(__file__).parent / "fixtures" / "beispiel.ics"
TZ = ZoneInfo("Europe/Berlin")


def _cal(**kw):
    return CalendarConfig(name="Test", icon="beide", file=FIXTURE,
                          prefix_icons={"L:": "lena", "F:": "fyn"}, **kw)


def test_parse_prefix_recurring_timezone_cancelled():
    events = load_events(_cal(), date(2026, 11, 13), date(2026, 11, 24), TZ)
    titles = sorted((e.title, e.icon) for e in events)
    assert ("Yoga", "lena") in titles                     # Präfix entfernt, Icon gesetzt
    assert sum(t == "Yoga" for t, _ in titles) == 2       # Serie: 16.11. und 23.11.
    assert ("Messe", "fyn") in titles                     # mehrtägig, ragt in den Zeitraum
    assert all(t != "Abgesagt" for t, _ in titles)        # abgesagte Termine fehlen
    dinner = next(e for e in events if e.title == "Abendessen")
    assert dinner.start == datetime(2026, 11, 13, 18, 0, tzinfo=TZ)  # UTC -> Berlin


def test_multi_day_counter():
    events = load_events(_cal(), date(2026, 11, 13), date(2026, 11, 14), TZ)
    titles = [e.title for e in entries_for_day(events, date(2026, 11, 13))]
    assert titles[0] == "Messe 3/3"


def test_title_prefix():
    events = load_events(_cal(title_prefix="HB: "), date(2026, 11, 13), date(2026, 11, 14), TZ)
    assert any(e.title == "HB: Abendessen" for e in events)


def test_config_validation(tmp_path):
    p = tmp_path / "c.toml"
    p.write_text('[[calendars]]\nname="X"\nurl="webcal://example.org/a.ics"\nicon="handball"\n', encoding="utf-8")
    cfg = load_config(p)
    assert cfg.calendars[0].url == "https://example.org/a.ics"

    p.write_text('[[calendars]]\nname="X"\nurl="https://x"\nicon="einhorn"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="unbekanntes Icon"):
        load_config(p)


def test_title_replace():
    from eink_calendar.calendar_source.rules import apply_title_rules
    cal = CalendarConfig(name="AWR", icon="tonne", url="x",
                         title_replace={"(14-täglich)": "", "Restabfall": "Restmüll"})
    assert apply_title_rules(cal, "Restabfall(14-täglich)") == ("tonne", "Restmüll")


def test_handballnet_parse_home_away_and_local_time():
    from eink_calendar.calendar_source.handballnet_source import parse_matches
    cal = CalendarConfig(name="HB", icon="fyn_handball", type="handballnet", team_id=81670)
    matches = [
        {"date": "2026-11-14T17:00:00+00:00",
         "local": {"id": 81670, "name": "SG BORDESHOLM/BRÜGGE III"},
         "visitor": {"id": 1, "name": "HSG 91 NORTORF II"}},
        {"date": "2026-11-21T14:00:00+00:00",
         "local": {"id": 2, "name": "IF Stjernen Flensborg"},
         "visitor": {"id": 81670, "name": "SG BORDESHOLM/BRÜGGE III"}},
    ]
    home, away = parse_matches(cal, matches, TZ)
    assert home.title == "vs. HSG 91 Nortorf II"
    assert away.title == "@ IF Stjernen Flensborg"
    assert home.start == datetime(2026, 11, 14, 17, 0, tzinfo=TZ)  # Uhrzeit = Ortszeit


def test_handballnet_requires_team_id(tmp_path):
    p = tmp_path / "c.toml"
    p.write_text('[[calendars]]\nname="X"\ntype="handballnet"\nicon="handball"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="team_id"):
        load_config(p)


def test_config_syntax_error_is_friendly(tmp_path):
    p = tmp_path / "c.toml"
    p.write_text("mock false\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="Tippfehler"):
        load_config(p)
