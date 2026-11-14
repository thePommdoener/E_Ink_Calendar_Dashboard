#!/usr/bin/env bash
# Installiert den systemd-Dienst für den Dauerbetrieb (Uhr minütlich, Kalender alle 15 min).
# Benutzer und Projektpfad werden automatisch eingesetzt.
set -euo pipefail
cd "$(dirname "$0")/.."
DIR="$(pwd)"
RUN_USER="$(id -un)"

# Alten 15-Minuten-Timer (frühere Version) entfernen, falls vorhanden
if systemctl list-unit-files eink-calendar.timer >/dev/null 2>&1 && \
   systemctl list-unit-files eink-calendar.timer | grep -q eink-calendar.timer; then
    sudo systemctl disable --now eink-calendar.timer || true
    sudo rm -f /etc/systemd/system/eink-calendar.timer
fi

sed -e "s|@USER@|${RUN_USER}|g" -e "s|@DIR@|${DIR}|g" systemd/eink-calendar.service \
    | sudo tee /etc/systemd/system/eink-calendar.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable eink-calendar.service
sudo systemctl restart eink-calendar.service
echo "Dienst läuft für Benutzer ${RUN_USER} in ${DIR}"
systemctl --no-pager status eink-calendar.service | head -n 5
