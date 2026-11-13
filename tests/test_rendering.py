from datetime import datetime

from eink_calendar.rendering.layout import render_agenda
from eink_calendar.sample_data import sample_events

NOW = datetime(2026, 11, 13, 16, 0)


def test_grayscale_uses_only_the_four_driver_levels():
    img = render_agenda(sample_events(NOW.date()), NOW, grayscale=True)
    assert img.mode == "L" and img.size == (800, 480)
    used = {v for v, count in enumerate(img.histogram()) if count}
    assert used <= {0x00, 0x80, 0xC0, 0xFF}


def test_mono_is_pure_black_white():
    img = render_agenda(sample_events(NOW.date()), NOW, grayscale=False)
    assert img.mode == "1"
