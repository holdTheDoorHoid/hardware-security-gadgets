#!/usr/bin/env bash
# Local preview. The site also works by opening index.html directly,
# but the server sends no-cache headers so edits always show on reload.
cd "$(dirname "$0")"
exec python3 devserver.py "${1:-8080}"
