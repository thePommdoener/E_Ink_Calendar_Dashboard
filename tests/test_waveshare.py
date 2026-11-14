from PIL import Image

from eink_calendar.display.waveshare_display import WaveshareDisplay


class FakeEPD:
    width, height = 800, 480

    def __init__(self):
        self.log = []

    def init_part(self):
        self.log.append(("init_part",))

    def send_command(self, c):
        self.log.append(("cmd", c))

    def send_data(self, d):
        self.log.append(("data", d))

    def send_data2(self, d):
        self.log.append(("data2", bytes(d)))

    def ReadBusy(self):
        pass

    def sleep(self):
        self.log.append(("sleep",))


def test_partial_writes_old_as_inverse_of_new():
    disp = WaveshareDisplay.__new__(WaveshareDisplay)
    disp.epd, disp.model = FakeEPD(), "fake"
    region = Image.new("1", (248, 80), 1)
    disp.show_partial(region, 0, 0)

    log = disp.epd.log
    old = log[log.index(("cmd", 0x10)) + 1][1]
    new = log[log.index(("cmd", 0x13)) + 1][1]
    assert len(new) == 248 // 8 * 80
    assert all(o == n ^ 0xFF for o, n in zip(old, new))
    assert log.index(("cmd", 0x10)) < log.index(("cmd", 0x13)) < log.index(("cmd", 0x12))
    assert log[-1] == ("sleep",)
