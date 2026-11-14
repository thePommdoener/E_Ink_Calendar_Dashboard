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
