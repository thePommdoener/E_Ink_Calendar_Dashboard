"""Gemeinsame Schnittstelle für alle Displays."""
from __future__ import annotations

from typing import Protocol

from PIL import Image


class Display(Protocol):
    def show(self, image: Image.Image) -> object: ...
