#!/usr/bin/env bash
# ex-video 웹앱 실행 (이 서버에서 구동). 기본 포트 8077.
set -e
cd "$(dirname "$0")/.."
PORT="${PORT:-8077}"
HOST="${HOST:-0.0.0.0}"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install --upgrade pip
  ./.venv/bin/pip install -r requirements.txt -r requirements-web.txt
fi
echo "ex-video web on http://$HOST:$PORT"
./.venv/bin/python -m uvicorn web.server:app --host "$HOST" --port "$PORT"
