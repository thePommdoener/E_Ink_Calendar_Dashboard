from pathlib import Path

from PIL import Image

from eink_calendar import main as main_mod
from eink_calendar.config import load_config


def test_run_in_mock_mode_writes_preview(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.toml"
    fixture = Path(__file__).parent / "fixtures" / "beispiel.ics"
    cfg_file.write_text(
        f'[display]\nmock = true\n[[calendars]]\nname = "T"\nfile = "{fixture.as_posix()}"\nicon = "beide"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(main_mod, "load_config", lambda: load_config(cfg_file))
    saved = {}

    class FakeMock:
        def show(self, image):
            saved["img"] = image
            return tmp_path / "preview.png"

    monkeypatch.setattr(main_mod, "MockDisplay", FakeMock)
    assert main_mod.run([]) == 0
    assert isinstance(saved["img"], Image.Image) and saved["img"].size == (800, 480)


def test_loop_full_then_clock_partial(tmp_path, monkeypatch):
    from datetime import datetime

    cfg_file = tmp_path / "config.toml"
    fixture = Path(__file__).parent / "fixtures" / "beispiel.ics"
    cfg_file.write_text(
        f'[display]\nmock = true\nclock = true\n[[calendars]]\nname = "T"\nfile = "{fixture.as_posix()}"\nicon = "beide"\n',
        encoding="utf-8",
    )
    cfg = load_config(cfg_file)
    calls = []

    class FakeDisplay:
        def show(self, image):
            calls.append(("full", image.size))

        def show_partial(self, region, x, y):
            calls.append(("partial", region.size, (x, y)))

    times = iter([datetime(2026, 11, 14, 15, 14), datetime(2026, 11, 14, 15, 14),
                  datetime(2026, 11, 14, 15, 14), datetime(2026, 11, 14, 15, 15),
                  datetime(2026, 11, 14, 15, 15)])
    monkeypatch.setattr(main_mod, "_make_display", lambda c: FakeDisplay())
    monkeypatch.setattr(main_mod, "_now", lambda tz: next(times))
    monkeypatch.setattr(main_mod, "_sleep_until_next_minute", lambda: None)

    # 15:14 erster Lauf -> komplett, 15:14 nochmal -> Uhr, 15:15 -> komplett (15er-Takt)
    main_mod.run_loop(cfg, max_iterations=3)
    assert calls[0] == ("full", (800, 480))
    assert calls[1] == ("partial", (248, 80), (0, 0))
    assert calls[2] == ("full", (800, 480))
