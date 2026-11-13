"""Einfacher Datei-Cache: Ist eine Quelle offline, wird die letzte Kopie genutzt."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Callable

from ..config import ROOT

log = logging.getLogger(__name__)
CACHE_DIR = ROOT / "cache"


def _path(key: str, suffix: str) -> Path:
    return CACHE_DIR / f"{hashlib.sha1(key.encode()).hexdigest()[:12]}{suffix}"


def fetch_with_cache(name: str, key: str, fetch: Callable[[], bytes], suffix: str = ".bin") -> bytes:
    """Ruft `fetch()` auf und speichert das Ergebnis. Bei Fehler: letzte Kopie zurückgeben."""
    path = _path(key, suffix)
    try:
        data = fetch()
    except Exception as exc:  # noqa: BLE001
        if path.exists():
            log.warning("%s: Laden fehlgeschlagen (%s), nutze Cache.", name, exc)
            return path.read_bytes()
        raise
    CACHE_DIR.mkdir(exist_ok=True)
    path.write_bytes(data)
    return data
