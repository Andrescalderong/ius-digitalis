#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/Documents/ius-digitalis"
PY="$BASE/.venv/bin/python3"
PORT=8000

# 1) Pipeline: RPA → IA → Blockchain
"$PY" "$BASE/rpa_secop/src/main.py"
if [[ -f "$BASE/ia_classifier/classify_v2.py" ]]; then
  "$PY" "$BASE/ia_classifier/classify_v2.py"
else
  "$PY" "$BASE/ia_classifier/classify.py"
fi
if [[ -f "$BASE/blockchain_registry/anchor_v2.py" ]]; then
  "$PY" "$BASE/blockchain_registry/anchor_v2.py"
else
  "$PY" "$BASE/blockchain_registry/anchor.py"
fi

# 2) Elige el dashboard existente
HTML=""
for f in demo_interactivo.html dashboard_live.html dashboard_con_pdfs.html dashboard.html visualize.html; do
  if [[ -f "$BASE/$f" ]]; then HTML="$f"; break; fi
done
if [[ -z "$HTML" ]]; then
  echo "No encontré ningún HTML de dashboard en $BASE" >&2
  exit 1
fi
echo "Dashboard: $HTML"

# 3) Servidor local y apertura del navegador
#   (matamos servidor viejo si quedara alguno)
if [[ -f "$BASE/.serve.pid" ]] && ps -p "$(cat "$BASE/.serve.pid")" >/dev/null 2>&1; then
  kill "$(cat "$BASE/.serve.pid")" || true
fi
( cd "$BASE" && "$PY" -m http.server $PORT >/dev/null 2>&1 ) & echo $! > "$BASE/.serve.pid"
sleep 1

URL="http://localhost:$PORT/$HTML"
echo "URL: $URL"
# Abre con el navegador por defecto (sin AppleScript)
open "$URL" || true

echo
echo "Si no se abrió automáticamente, copia y pega esta URL en el navegador:"
echo "$URL"
echo
echo "Para cerrar el servidor cuando termines:"
echo "kill \$(cat \"$BASE/.serve.pid\"); rm \"$BASE/.serve.pid\""
