# Pi einrichten – Schritt für Schritt

Hardware: Raspberry Pi Zero 2 WH + Waveshare 7.5" e-Paper HAT (V2, 800×480).

**Dein Pi:** Hostname `KalenderPi`, Benutzer `fynnstapelfeldt`
→ SSH: `ssh fynnstapelfeldt@KalenderPi.local`, Projektordner: `/home/fynnstapelfeldt/E_Ink_Calendar_Dashboard`
Dauer: ca. 1–1,5 Stunden (das meiste ist Warten auf Updates).

Was du brauchst: microSD-Karte (≥ 8 GB), Kartenleser am PC, Netzteil für den Pi
(Micro-USB, 5 V / 2,5 A), WLAN-Name und -Passwort.

---

## 0. Vorab am PC

1. **Code nach GitHub pushen** (falls noch nicht geschehen):
   ```powershell
   git push -u origin main
   ```
2. **Raspberry Pi Imager** installieren: https://www.raspberrypi.com/software/

---

## 1. SD-Karte beschreiben (am PC)

Im Raspberry Pi Imager:

| Auswahl            | Wert                                        |
|--------------------|---------------------------------------------|
| Gerät              | Raspberry Pi Zero 2 W                       |
| Betriebssystem     | Raspberry Pi OS (other) → **Raspberry Pi OS Lite (64-bit)** |
| Speicher           | deine SD-Karte                              |

Bei „Einstellungen bearbeiten“ / „OS-Anpassungen“:

| Einstellung        | Wert                                        |
|--------------------|---------------------------------------------|
| Hostname           | `KalenderPi`                                |
| Benutzername       | `fynnstapelfeldt`                           |
| Passwort           | frei wählen                                 |
| WLAN               | SSID + Passwort, Land **DE**                |
| Zeitzone / Tastatur| `Europe/Berlin` / `de`                      |
| Dienste → SSH      | **aktivieren** (Passwort oder öffentlicher Schlüssel) |

Schreiben, Karte auswerfen.

---

## 2. Hardware zusammenstecken (Pi **ohne Strom**!)

1. Flachbandkabel des Displays in den Stecker am HAT: Verriegelung hochklappen,
   Kabel mit den **Kontakten nach unten** (zur Platine) einschieben, Verriegelung zudrücken.
2. Schalter auf dem HAT (falls vorhanden):
   - **Interface Config** → `0` (4-Draht-SPI)
   - **Display Config** → `B` (Standard für das 7.5" V2 – im Zweifel im
     [Waveshare-Wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual) nachsehen)
3. HAT auf die 40-Pin-Leiste des Pi stecken (bündig, alle Pins drin).
4. SD-Karte rein, Strom an. Der erste Start dauert 2–5 Minuten.

---

## 3. Per SSH verbinden (am PC)

```powershell
ssh fynnstapelfeldt@KalenderPi.local
```

Klappt `KalenderPi.local` nicht: IP-Adresse im Router (z. B. FRITZ!Box → Heimnetz)
nachsehen und `ssh fynnstapelfeldt@192.168.x.x` nutzen.

Optional – Login ohne Passwort:
```powershell
ssh-keygen -t ed25519            # nur falls noch kein Schlüssel existiert
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh fynnstapelfeldt@KalenderPi.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

> Ab hier laufen alle Befehle **auf dem Pi** (in der SSH-Sitzung), außer es steht „am PC“ dabei.

---

## 4. System aktualisieren (auf dem Pi)

```bash
sudo apt update && sudo apt full-upgrade -y     # dauert auf dem Zero 2 eine Weile
sudo apt install -y git tmux
sudo timedatectl set-timezone Europe/Berlin
```

**WLAN-Energiesparen ausschalten** – sonst friert die SSH-Verbindung beim Zero 2 gern ein:
```bash
nmcli -t -f NAME connection show --active          # Name der WLAN-Verbindung anzeigen
sudo nmcli connection modify "NAME" 802-11-wireless.powersave 2
sudo nmcli connection up "NAME"                    # SSH kann kurz hängen -> neu verbinden
```

Hinweise zu Meldungen beim Upgrade (alle harmlos):
- `WARNING: apt does not have a stable CLI interface` → ignorieren.
- `debconf: unable to initialize frontend: Dialog` → Terminal zu klein; Fragen kommen als Text, mit **Enter** die Standardantwort nehmen.
- `Could not get lock /var/lib/dpkg/lock-frontend` → ein anderes apt läuft noch; warten, **nie** die Lock-Datei löschen.

Tipp: Lange Befehle in `tmux` starten (`tmux`, danach normal arbeiten). Bricht die
Verbindung ab: neu verbinden und `tmux attach`.

---

## 5. Projekt holen und einrichten (auf dem Pi)

```bash
cd ~
git clone https://github.com/thePommdoener/E_Ink_Calendar_Dashboard.git
cd E_Ink_Calendar_Dashboard
bash scripts/setup_pi.sh
sudo reboot
```

Ist das GitHub-Repo **privat**, fragt `git clone` nach Zugangsdaten. Dann entweder
einen Deploy-Key einrichten oder den Ordner direkt vom PC kopieren (am PC):
```powershell
scp -r D:\Documents\Repos\E_Ink_Calendar_Dashboard fynnstapelfeldt@KalenderPi.local:~/
```
Danach auf dem Pi die Windows-Python-Umgebung entfernen (sonst scheitert das Setup):
```bash
cd ~/E_Ink_Calendar_Dashboard
rm -rf .venv
find . -name "__pycache__" -type d -prune -exec rm -rf {} +
```
(Bei dieser Variante ist `config/config.toml` schon dabei – Schritt 6 entfällt.)

`setup_pi.sh` erledigt automatisch:
- Systempakete: Python, Pillow, numpy, spidev, gpiozero, lgpio, Schriften
- **SPI aktivieren** (Schnittstelle zum Display)
- Waveshare-Treiber nach `lib/waveshare_epd/` holen
- Python-Umgebung `.venv` + Pakete aus `requirements.txt`
- `config/config.toml` aus der Vorlage anlegen

---

## 6. Persönliche Konfiguration übertragen (am PC)

Deine `config.toml` (Handball-Teams, AWR-Adresse) ist nicht im Git. Vom PC kopieren:

```powershell
scp D:\Documents\Repos\E_Ink_Calendar_Dashboard\config\config.toml fynnstapelfeldt@KalenderPi.local:~/E_Ink_Calendar_Dashboard/config/
```

`mock = true` erst mal so lassen.

---

## 7. Software testen (auf dem Pi, noch ohne Display)

```bash
ssh fynnstapelfeldt@KalenderPi.local
cd ~/E_Ink_Calendar_Dashboard
.venv/bin/python -m pytest -q                  # erwartet: alle Tests "passed"
.venv/bin/python scripts/check_calendars.py    # erwartet: "Alle Kalender OK."
.venv/bin/python scripts/preview.py --live     # erzeugt output/preview.png
```

Bild zum Anschauen auf den PC holen (am PC):
```powershell
scp fynnstapelfeldt@KalenderPi.local:~/E_Ink_Calendar_Dashboard/output/preview.png $env:USERPROFILE\Desktop\
```

---

## 8. Display-Hardware testen (auf dem Pi)

SPI prüfen – es müssen zwei Einträge erscheinen:
```bash
ls /dev/spidev0.*
```

**Test A – Display löschen** (wird kurz schwarz/weiß flackern):
```bash
cd ~/E_Ink_Calendar_Dashboard
.venv/bin/python - <<'EOF'
import sys; sys.path.insert(0, "lib")
from waveshare_epd import epd7in5_V2
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()
epd.sleep()
print("OK")
EOF
```

**Test B – Vorschau in 4 Graustufen anzeigen:**
```bash
.venv/bin/python - <<'EOF'
import sys; sys.path.insert(0, "lib")
from PIL import Image
from waveshare_epd import epd7in5_V2
epd = epd7in5_V2.EPD()
epd.init_4Gray()
img = Image.open("output/preview.png").convert("L")
epd.display_4Gray(epd.getbuffer_4Gray(img))
epd.sleep()
print("OK")
EOF
```

Wenn Test B den Kalender zeigt, funktioniert die Hardware – weiter mit Schritt 9.

Fotografier das Display gern ab, dann können wir Graustufen und Schriftgrößen
am echten Bild nachjustieren.

---

## 9. Automatischer Betrieb

```bash
cd ~/E_Ink_Calendar_Dashboard
bash scripts/update.sh                          # neuesten Code holen
nano config/config.toml                         # [display] mock = false
PYTHONPATH=src .venv/bin/python -m eink_calendar   # einmal manuell -> Display zeichnet
bash scripts/install_service.sh                 # ab jetzt alle 15 Minuten automatisch
```

Display leeren (z. B. vor längerer Lagerung):
```bash
PYTHONPATH=src .venv/bin/python -m eink_calendar --clear
```

Nützliche Befehle:
```bash
systemctl list-timers eink-calendar.timer      # wann läuft es das nächste Mal?
journalctl -u eink-calendar.service -n 50      # Log der letzten Läufe
bash scripts/update.sh                         # neuen Code von GitHub holen
```

---

## Fehlerhilfe

| Problem | Lösung |
|---|---|
| `ssh: Could not resolve hostname KalenderPi.local` | IP im Router nachsehen, `ssh fynnstapelfeldt@<IP>` |
| Pi taucht gar nicht im WLAN auf | WLAN-Daten/Land im Imager prüfen, Karte neu schreiben (Zero 2 kann nur **2,4 GHz**) |
| Test hängt bei `e-Paper busy` | Strom aus, Flachbandkabel und Schalter (Schritt 2) prüfen, HAT richtig aufgesteckt? |
| `No such file /dev/spidev0.0` | `sudo raspi-config nonint do_spi 0`, dann `sudo reboot` |
| Bild verzerrt / falsche Größe | Displayversion auf der Rückseite prüfen (V1 = 640×384 bräuchte anderen Treiber) |
| `ModuleNotFoundError: waveshare_epd` | Befehle im Projektordner ausführen; `ls lib/waveshare_epd` prüfen, ggf. `setup_pi.sh` erneut |
| Kalender-Fehler bei `check_calendars.py` | Internet am Pi? `ping -c 3 google.de` |

## Pflegehinweise fürs E-Paper (laut Waveshare)

- Nicht öfter als alle **3 Minuten** neu zeichnen (15 Minuten sind ideal).
- Nach dem Zeichnen immer `sleep()` – macht das Programm automatisch.
- Wird das Display länger nicht benutzt (Lagerung): vorher mit Test A **leeren**.
