#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install --upgrade pip
  ./.venv/bin/pip install -r requirements.txt
fi
read -r -p "영상 경로 또는 구글드라이브/URL 링크 입력: " SRC
./.venv/bin/python -m exvideo "$SRC" -o output
echo "완료. output/bundle.md 를 확인하세요."
