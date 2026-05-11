#!/usr/bin/env bash
cd "$(dirname "$0")"

PORT=8765
URL="http://localhost:$PORT"

echo ""
echo "================================================================"
echo "  Guida agli Agenti AI / Guide to AI Agents — local server"
echo "================================================================"
echo ""
echo "  IT: $URL"
echo "  EN: $URL/en/"
echo ""
echo "  Stop: Ctrl+C or close this window"
echo ""

( sleep 1 && open "$URL" ) &

python3 -m http.server $PORT --bind 127.0.0.1
