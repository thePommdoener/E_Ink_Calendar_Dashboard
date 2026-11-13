"""Titel-Regeln, die für alle Quellen gelten (Icon per Präfix, Umbenennen, Präfix)."""
from __future__ import annotations

from ..config import CalendarConfig


def apply_title_rules(cal: CalendarConfig, title: str) -> tuple[str, str]:
    """Liefert (Icon, angezeigter Titel)."""
    title = title.strip()
    for old, new in cal.title_replace.items():
        title = title.replace(old, new)
    title = title.strip()

    icon = cal.icon
    for prefix, prefix_icon in cal.prefix_icons.items():
        if title.lower().startswith(prefix.lower()):
            icon = prefix_icon
            title = title[len(prefix):].strip()
            break

    if cal.title_prefix:
        title = f"{cal.title_prefix}{title}"
    return icon, title
