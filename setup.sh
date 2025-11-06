#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# venv único
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip

# instalación reproducible: preferir lock
if [ -f "requirements.lock" ]; then
  python -m pip install -r requirements.lock
else
  # fallback seguro (sin paquetes pesados ni hashlib-extra)
  for f in requirements.txt requirements-core.txt requirements-rest.txt; do
    [ -f "$f" ] && sed -i '' '/^hashlib[-_]*extra[>=<]/Id' "$f"
  done
  [ -f requirements-core.txt ] && python -m pip install --no-cache-dir -r requirements-core.txt || true
  [ -f requirements-rest.txt ] && python -m pip install --no-cache-dir -r requirements-rest.txt || true
fi

echo "✅ Entorno listo en .venv"
