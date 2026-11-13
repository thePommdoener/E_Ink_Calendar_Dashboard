"""Lädt und prüft config/config.toml."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

from .rendering.icons import ICONS

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "config.toml"


class ConfigError(Exception):
    pass


@dataclass
class CalendarConfig:
    name: str
    icon: str
    type: str = "ics"            # "ics" oder "handballnet"
    url: str | None = None
    file: Path | None = None
    team_id: int | None = None   # nur für type = "handballnet"
    prefix_icons: dict[str, str] = field(default_factory=dict)
    title_replace: dict[str, str] = field(default_factory=dict)
    title_prefix: str = ""
    enabled: bool = True

    @property
    def source(self) -> str:
        if self.type == "handballnet":
            return f"https://www.handball.net/team/{self.team_id}"
        return self.url or str(self.file)


@dataclass
class Config:
    timezone: str
    days_ahead: int
    display_model: str
    mock: bool
    grayscale: bool
    calendars: list[CalendarConfig]


def _check_icon(name: str, where: str) -> None:
    if name not in ICONS:
        raise ConfigError(f"{where}: unbekanntes Icon '{name}'. Verfügbar: {', '.join(ICONS)}")


def _parse_calendar(raw: dict, index: int) -> CalendarConfig:
    where = f"[[calendars]] Nr. {index + 1}"
    name = raw.get("name") or f"Kalender {index + 1}"
    where = f"{where} ('{name}')"

    cal_type = raw.get("type", "ics")
    if cal_type not in ("ics", "handballnet"):
        raise ConfigError(f"{where}: type muss 'ics' oder 'handballnet' sein.")
    team_id = raw.get("team_id")
    url, file = raw.get("url"), raw.get("file")
    if cal_type == "handballnet":
        if not str(team_id or "").isdigit():
            raise ConfigError(f"{where}: type = 'handballnet' braucht team_id (Zahl).")
        team_id = int(team_id)
    elif bool(url) == bool(file):
        raise ConfigError(f"{where}: genau eines von 'url' oder 'file' angeben.")
    if url:
        url = url.strip()
        if url.startswith("webcal://"):
            url = "https://" + url[len("webcal://"):]
    path = None
    if file:
        path = Path(file)
        if not path.is_absolute():
            path = ROOT / path

    icon = raw.get("icon", "termin")
    _check_icon(icon, where)
    prefix_icons = dict(raw.get("prefix_icons", {}))
    for prefix, pi in prefix_icons.items():
        _check_icon(pi, f"{where} prefix_icons['{prefix}']")

    return CalendarConfig(
        name=name,
        icon=icon,
        type=cal_type,
        url=url,
        file=path,
        team_id=team_id,
        prefix_icons=prefix_icons,
        title_replace=dict(raw.get("title_replace", {})),
        title_prefix=raw.get("title_prefix", ""),
        enabled=raw.get("enabled", True),
    )


def load_config(path: Path = CONFIG_PATH) -> Config:
    if not path.exists():
        raise ConfigError(
            f"{path} fehlt. Kopiere config/config.example.toml nach config/config.toml und passe sie an."
        )
    with path.open("rb") as f:
        raw = tomllib.load(f)

    general = raw.get("general", {})
    display = raw.get("display", {})
    calendars = [_parse_calendar(c, i) for i, c in enumerate(raw.get("calendars", []))]
    if not any(c.enabled for c in calendars):
        raise ConfigError("Kein aktiver Kalender in [[calendars]] eingetragen.")

    return Config(
        timezone=general.get("timezone", "Europe/Berlin"),
        days_ahead=int(general.get("days_ahead", 14)),
        display_model=display.get("model", "epd7in5_V2"),
        mock=bool(display.get("mock", False)),
        grayscale=bool(display.get("grayscale", True)),
        calendars=calendars,
    )
