#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "⚙️  Activando entorno…"
source .venv/bin/activate

echo "📄 [1/3] RPA — Generando PDFs y metadatos…"
python3 rpa_secop/src/main.py

echo "🧠 [2/3] IA — Clasificando…"
python3 ia_classifier/classify_v2.py

echo "⛓️  [3/3] Blockchain — Anclando (v3, hashes reales)…"
python3 blockchain_registry/anchor_v3.py

echo "🌐 Levantando servidor local…"
PORT=8765
python3 -m http.server "$PORT" >/dev/null 2>&1 &
SRV_PID=$!
sleep 1

DASH="demo_interactivo.html"
URL="http://localhost:$PORT/$DASH"
echo "🔎 Abriendo dashboard: $URL"
open "$URL"

echo "📂 Abriendo PDFs…"
open rpa_secop/data/raw/EXP-2025-001.pdf
open rpa_secop/data/raw/EXP-2025-002.pdf
open rpa_secop/data/raw/EXP-2025-003.pdf

echo
echo "🎬 Grabación sugerida (manual, estable):"
echo "   1) Presiona ⌘⇧5  → 'Grabar toda la pantalla'"
echo "   2) En el dashboard: scroll suave por tarjetas (TX, SHA, timestamp, categoría)"
echo "   3) Muestra uno de los PDFs abiertos"
echo "   4) Detén la grabación (⌘⌃Esc)."
echo
echo "✅ Cuando termines, vuelve a esta ventana y pulsa Enter para cerrar el servidor…"
read -r _
kill $SRV_PID || true
echo "✅ Demo TRL-8 finalizado."
