"""Speichert das Bild als PNG in output/ – zum Entwickeln am PC ohne Display."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "output"


class MockDisplay:
    def __init__(self, output_dir: Path = OUTPUT_DIR) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current: Image.Image | None = None

    def show(self, image: Image.Image) -> Path:
        self.current = image.copy()
        return self._save()

    def show_partial(self, region: Image.Image, x: int, y: int) -> Path:
        """Simuliert den Teil-Refresh: Ausschnitt in das letzte Bild einsetzen."""
        if self.current is None:
            raise RuntimeError("Teil-Refresh vor dem ersten vollständigen Bild")
        self.current.paste(region.convert(self.current.mode), (x, y))
        return self._save()

    def _save(self) -> Path:
        path = self.output_dir / "preview.png"
        self.current.save(path)
        # Zusätzlich 2x vergrößert, damit man am Monitor die Pixel gut erkennt
        self.current.resize((self.current.width * 2, self.current.height * 2), Image.NEAREST).save(
            self.output_dir / "preview_2x.png"
        )
        return path
