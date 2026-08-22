#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " Starting Printway AI Agent & Market Intelligence Platform "
echo "=========================================================="

PORT=${PORT:-8001}
HOST=${HOST:-0.0.0.0}

echo "• Host: $HOST"
echo "• Port: $PORT"
echo "• API Docs: http://localhost:$PORT/docs"
echo "• Health: http://localhost:$PORT/health"
echo "=========================================================="

exec python3 -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
