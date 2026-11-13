"""Spielpläne von handball.net.

handball.net bietet seit dem Relaunch keinen ICS-Export pro Mannschaft mehr.
Die Webseite selbst lädt die Spiele aber über eine öffentliche JSON-Schnittstelle
(`/api/new/matches?team_id=...`), die hier genutzt wird. Sie ist inoffiziell –
ändert handball.net etwas, muss dieses Modul ggf. angepasst werden.

Team-ID finden: Mannschaft auf handball.net öffnen, die Zahl am Ende der URL
(z. B. https://www.handball.net/team/81670) ist die team_id.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from ..config import CalendarConfig
from .cache import fetch_with_cache
from .models import Event
from .rules import apply_title_rules

SITE = "https://www.handball.net"
API = f"{SITE}/api/new/matches"
TIMEOUT_S = 30
MATCH_DURATION = timedelta(minutes=90)
HEADERS = {"User-Agent": "Mozilla/5.0 eink-calendar/1.0", "Accept": "application/json"}


def _client_token(session: requests.Session) -> str | None:
    html = session.get(SITE + "/", timeout=TIMEOUT_S).text
    m = re.search(r'<meta name="client-token" content="([^"]+)"', html)
    return m.group(1) if m else None


def fetch_matches(team_id: int, start: date, end: date) -> list[dict]:
    with requests.Session() as s:
        s.headers.update(HEADERS)
        s.headers["Referer"] = f"{SITE}/team/{team_id}"
        token = _client_token(s)
        if token:
            s.headers["x-client-token"] = token

        matches: list[dict] = []
        page = 1
        while True:
            resp = s.get(API, timeout=TIMEOUT_S, params={
                "team_id": team_id, "date_from": start.isoformat(), "date_to": end.isoformat(),
                "per_page": 100, "page": page,
            })
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("success") is False:
                raise RuntimeError(f"handball.net: {payload.get('error')}")
            matches.extend(payload.get("data") or [])
            last = (payload.get("pagination") or {}).get("last_page") or 1
            if page >= last:
                return matches
            page += 1


def _pretty(name: str) -> str:
    """'SG BORDESHOLM/BRÜGGE II' -> 'SG Bordesholm/Brügge II' (nur falls komplett groß)."""
    if name != name.upper():
        return name
    words = []
    for w in name.split():
        if re.fullmatch(r"[IVX]+|[A-Z]{1,3}", w):
            words.append(w)  # römische Ziffern / Kürzel wie SG, TSV, HSG
        else:
            words.append("/".join(p.capitalize() for p in w.split("/")))
    return " ".join(words)


def parse_matches(cal: CalendarConfig, matches: list[dict], tz: ZoneInfo) -> list[Event]:
    events: list[Event] = []
    for m in matches:
        raw_date = m.get("date")
        if not raw_date:
            continue
        # Die API hängt "+00:00" an, die Uhrzeit ist aber bereits Ortszeit.
        start = datetime.fromisoformat(raw_date[:19]).replace(tzinfo=tz)

        local, visitor = m.get("local") or {}, m.get("visitor") or {}
        is_home = str(local.get("id")) == str(cal.team_id)
        opponent = _pretty((visitor if is_home else local).get("name", "?"))
        title = f"vs. {opponent}" if is_home else f"@ {opponent}"

        icon, title = apply_title_rules(cal, title)
        events.append(Event(title=title, start=start, end=start + MATCH_DURATION,
                            icon=icon, calendar=cal.name))
    return events


def load_events(cal: CalendarConfig, start: date, end: date, tz: ZoneInfo) -> list[Event]:
    raw = fetch_with_cache(
        cal.name,
        f"handballnet:{cal.team_id}:{start}:{end}",
        lambda: json.dumps(fetch_matches(cal.team_id, start, end)).encode(),
        ".json",
    )
    return parse_matches(cal, json.loads(raw), tz)
