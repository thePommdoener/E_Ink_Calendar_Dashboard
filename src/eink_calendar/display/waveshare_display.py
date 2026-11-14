"""Ausgabe auf dem Waveshare-E-Paper (nur auf dem Pi lauffähig).

Der Treiber liegt in lib/waveshare_epd/ (wird von scripts/setup_pi.sh geholt).
Graustufenbilder (Modus "L") werden im 4-Gray-Modus gezeichnet, S/W-Bilder
(Modus "1") im normalen Modus. Danach geht das Display immer in den Schlafmodus –
das schont das Panel und den Stromverbrauch.
"""
from __future__ import annotations

import importlib
import logging
import sys
import time
from pathlib import Path

from PIL import Image

LIB_DIR = Path(__file__).resolve().parents[3] / "lib"
log = logging.getLogger(__name__)


class WaveshareDisplay:
    def __init__(self, model: str = "epd7in5_V2") -> None:
        if str(LIB_DIR) not in sys.path:
            sys.path.insert(0, str(LIB_DIR))
        try:
            module = importlib.import_module(f"waveshare_epd.{model}")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                f"Waveshare-Treiber '{model}' nicht gefunden in {LIB_DIR}. "
                "Bitte scripts/setup_pi.sh ausführen."
            ) from exc
        self.epd = module.EPD()
        self.model = model

    def show(self, image: Image.Image) -> None:
        epd = self.epd
        if image.size != (epd.width, epd.height):
            raise ValueError(f"Bildgröße {image.size} passt nicht zum Display {(epd.width, epd.height)}")

        try:
            if image.mode == "L":
                log.info("Zeichne in 4 Graustufen (%s) ...", self.model)
                epd.init_4Gray()
                epd.display_4Gray(epd.getbuffer_4Gray(image))
            else:
                log.info("Zeichne in Schwarz/Weiß (%s) ...", self.model)
                epd.init()
                epd.display(epd.getbuffer(image.convert("1")))
        finally:
            epd.sleep()
        log.info("Display aktualisiert.")

    def show_partial(self, region: Image.Image, x: int, y: int) -> None:
        """Teil-Refresh eines Rechtecks (nur Schwarz/Weiß, kein Flackern).

        Nachbau von epd7in5_V2.display_Partial, aber nur für den Ausschnitt.
        x und die Breite müssen Vielfache von 8 sein.
        """
        epd = self.epd
        img = region.convert("1")
        w, h = img.size
        if x % 8 or w % 8:
            raise ValueError("Teil-Refresh: x und Breite müssen Vielfache von 8 sein")
        x_end, y_end = x + w - 1, y + h - 1

        try:
            epd.init_part()
            epd.send_command(0x50)          # VCOM/Daten-Intervall für Teil-Refresh
            epd.send_data(0xA9)
            epd.send_data(0x07)
            epd.send_command(0x91)          # Teil-Modus an
            epd.send_command(0x90)          # Fenster setzen
            for value in (x >> 8, x & 0xFF, x_end >> 8, x_end & 0xFF,
                          y >> 8, y & 0xFF, y_end >> 8, y_end & 0xFF, 0x01):
                epd.send_data(value)
            new = bytearray(img.tobytes())  # im Teil-Modus: 1 = weiß
            # "Alt"-Speicher = Gegenteil von "neu" -> jedes Pixel im Fenster wird
            # garantiert umgeschaltet. Nötig, weil der Tiefschlaf den Speicher löscht;
            # sonst sieht das Display keinen Unterschied und zeichnet nichts.
            epd.send_command(0x10)
            epd.send_data2(bytearray(b ^ 0xFF for b in new))
            epd.send_command(0x13)
            epd.send_data2(new)
            epd.send_command(0x12)          # Refresh
            time.sleep(0.1)
            epd.ReadBusy()
        finally:
            epd.sleep()

    def clear(self) -> None:
        try:
            self.epd.init()
            self.epd.Clear()
        finally:
            self.epd.sleep()
