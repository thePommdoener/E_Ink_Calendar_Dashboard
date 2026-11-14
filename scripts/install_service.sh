#!/usr/bin/env bash
# Installiert systemd-Service + Timer für die automatische Aktualisierung.
# Benutzer und Projektpfad werden automatisch eingesetzt.
set -euo pipefail
cd "$(dirname "$0")/.."
DIR="$(pwd)"
RUN_USER="$(id -un)"

sed -e "s|@USER@|${RUN_USER}|g" -e "s|@DIR@|${DIR}|g" systemd/eink-calendar.service \
    | sudo tee /etc/systemd/system/eink-calendar.service >/dev/null
sudo cp systemd/eink-calendar.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now eink-calendar.timer
echo "Service installiert für Benutzer ${RUN_USER} in ${DIR}"
systemctl list-timers eink-calendar.timer
