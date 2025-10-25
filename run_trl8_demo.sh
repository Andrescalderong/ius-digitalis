#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# === CONFIG ===
BASE="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8765}"
export PYTHONUNBUFFERED=1

cd "$BASE"
source .venv/bin/activate

echo "🧹 Limpiando anclajes previos…"
rm -f blockchain_registry/outputs/anchors.json || true

echo
echo "📄 [1/3] RPA — Generando PDFs y metadatos (stdout en tiempo real)…"
time python3 -u rpa_secop/src/main.py

echo
echo "🧠 [2/3] IA — Clasificando documentos…"
time python3 -u ia_classifier/classify_v2.py

echo
echo "⛓️  [3/3] Blockchain — Registrando anclajes…"
time python3 -u blockchain_registry/anchor_v2.py

echo
echo "🌐 Servidor local y dashboard… (puerto $PORT)"
python3 -m http.server "$PORT" >/dev/null 2>&1 &
SRV_PID=$!
sleep 1

DASH="demo_interactivo.html"
URL="http://localhost:${PORT}/${DASH}?t=$(date +%s)"
echo "🔎 Abriendo dashboard: $URL"
open "$URL"

echo "📂 Abriendo PDFs (para mostrar en el video)…"
open rpa_secop/data/raw/EXP-2025-001.pdf
open rpa_secop/data/raw/EXP-2025-002.pdf
open rpa_secop/data/raw/EXP-2025-003.pdf

cat <<TXT

🎬 Grabación sugerida (manual, estable):
   1) Presiona ⌘⇧5  → "Grabar toda la pantalla"
   2) En el dashboard: scroll suave (TX, SHA-256, timestamp, categoría)
   3) Abre un PDF y muéstralo unos segundos
   4) Detén la grabación (⌘⌃Esc).
TXT

read -r -p "✅ Pulsa Enter cuando termines para cerrar el servidor y verificar…"

echo "🛑 Cerrando server ($SRV_PID)…"
kill "$SRV_PID" 2>/dev/null || true

echo
echo "🔎 Verificando integridad (PDF vs anchors.json)…"
./verificar_todo.sh

echo
echo "✅ Demo TRL-8 finalizada."
