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

    def clear(self) -> None:
        try:
            self.epd.init()
            self.epd.Clear()
        finally:
            self.epd.sleep()
