#!/usr/bin/env bash
# Einmaliges Setup auf dem Raspberry Pi (Raspberry Pi OS Lite 64-bit, Bookworm).
# Aufruf aus dem Repo-Verzeichnis:  bash scripts/setup_pi.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo ">> Systempakete installieren"
sudo apt update
sudo apt install -y git python3-pip python3-venv python3-pil python3-numpy \
    python3-spidev python3-gpiozero python3-lgpio fonts-dejavu-core

echo ">> SPI aktivieren"
sudo raspi-config nonint do_spi 0

echo ">> Waveshare-Treiber holen (nur der Python-Teil, per sparse checkout)"
if [ ! -d lib/waveshare_epd ]; then
    tmp=$(mktemp -d)
    git clone --depth 1 --filter=blob:none --sparse https://github.com/waveshareteam/e-Paper.git "$tmp"
    git -C "$tmp" sparse-checkout set RaspberryPi_JetsonNano/python/lib/waveshare_epd
    cp -r "$tmp/RaspberryPi_JetsonNano/python/lib/waveshare_epd" lib/
    rm -rf "$tmp"
fi

echo ">> Virtuelle Umgebung (nutzt apt-Pakete mit)"
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt

echo ">> Konfiguration"
[ -f config/config.toml ] || cp config/config.example.toml config/config.toml

echo "Fertig. Bitte config/config.toml anpassen und ggf. neu starten (SPI)."
