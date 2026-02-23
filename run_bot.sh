#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "Tworzenie venv i instalacja zależności..."
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi
. .venv/bin/activate
echo "Uruchamiam bota..."
python bot.py
