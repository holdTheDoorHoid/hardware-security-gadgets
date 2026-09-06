#!/usr/bin/env bash
# Local preview. The site also works by opening index.html directly,
# but a server keeps URLs clean and matches how it will behave when hosted.
cd "$(dirname "$0")"
PORT="${1:-8080}"
echo "Sec Gadget Index -> http://localhost:$PORT"
exec python3 -m http.server "$PORT"
