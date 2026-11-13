#!/usr/bin/env bash
# Neuesten Stand vom GitHub-Repo holen.
set -euo pipefail
cd "$(dirname "$0")/.."
git pull --ff-only
.venv/bin/pip install -r requirements.txt
