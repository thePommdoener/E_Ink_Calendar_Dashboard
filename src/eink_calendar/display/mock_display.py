"""Speichert das Bild als PNG in output/ – zum Entwickeln am PC ohne Display."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "output"


class MockDisplay:
    def __init__(self, output_dir: Path = OUTPUT_DIR) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def show(self, image: Image.Image) -> Path:
        path = self.output_dir / "preview.png"
        image.save(path)
        # Zusätzlich 2x vergrößert, damit man am Monitor die Pixel gut erkennt
        image.resize((image.width * 2, image.height * 2), Image.NEAREST).save(
            self.output_dir / "preview_2x.png"
        )
        return path
