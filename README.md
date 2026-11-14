# E-Ink Calendar Dashboard

Zeigt einen geteilten iCloud-Kalender auf einem Waveshare 7.5" E-Paper HAT an
(Raspberry Pi Zero 2 WH, Raspberry Pi OS Lite 64-bit).

## Struktur

```
config/            config.example.toml  -> Kopie als config.toml (nicht im Git)
src/eink_calendar/
  main.py          Ablauf: Termine holen -> rendern -> anzeigen
  config.py        Konfiguration laden
  calendar_source/ iCloud-Anbindung (ICS-Link oder CalDAV) + Datenmodell
  rendering/       Bild mit Pillow erzeugen (Layout, Fonts)
  display/         Waveshare-Hardware oder Mock (PNG in output/)
lib/waveshare_epd/ Waveshare-Treiber (wird von scripts/setup_pi.sh geholt)
assets/fonts/      Schriftarten (.ttf)
scripts/           Setup, Service-Installation, Update
systemd/           Dienst: Uhr jede Minute, Kalender alle 15 min
tests/             Tests
output/            Generierte Vorschaubilder (nicht im Git)
```

## Kalender einrichten

Alle Kalender stehen in `config/config.toml` (Vorlage: `config/config.example.toml`)
als `[[calendars]]`-Blöcke – beliebig viele:

```toml
[[calendars]]
name = "Handball"
url = "webcal://..."        # oder: file = "config/calendars/xyz.ics"
icon = "handball"           # lena | fyn | beide | handball | termin | stern
```

Optional: `prefix_icons = { "L:" = "lena", "F:" = "fyn" }` (Titel-Präfix bestimmt das Icon),
`title_prefix = "HB: "`, `enabled = false`.

```bash
python scripts/check_calendars.py   # prüft alle Links, zeigt die nächsten Termine
python scripts/preview.py --live    # Vorschau mit echten Kalendern -> output/preview.png
python scripts/preview.py           # Vorschau mit Beispieldaten
python -m pytest                    # Tests
```

Neue Icons: in `src/eink_calendar/rendering/icons.py` zeichnen und in `ICONS` eintragen.

## Installation auf dem Pi

Ausführliche Schritt-für-Schritt-Anleitung: [docs/PI_SETUP.md](docs/PI_SETUP.md)

```bash
git clone https://github.com/thePommdoener/E_Ink_Calendar_Dashboard.git
cd E_Ink_Calendar_Dashboard
bash scripts/setup_pi.sh
nano config/config.toml
sudo reboot
```

Pi: Hostname `KalenderPi`, Benutzer `fynnstapelfeldt` (`ssh fynnstapelfeldt@KalenderPi.local`).
`scripts/install_service.sh` setzt Benutzer und Projektpfad automatisch in den systemd-Service ein.
