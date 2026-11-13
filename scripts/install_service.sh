#!/usr/bin/env bash
# Installiert systemd-Service + Timer für die automatische Aktualisierung.
set -euo pipefail
cd "$(dirname "$0")/.."
sudo cp systemd/eink-calendar.service systemd/eink-calendar.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now eink-calendar.timer
systemctl list-timers eink-calendar.timer
