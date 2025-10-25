#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "⚙️  Activando entorno…"
source .venv/bin/activate

echo "📄 [1/3] RPA…"
python3 rpa_secop/src/main.py

echo "🧠 [2/3] IA…"
python3 ia_classifier/classify_v2.py

echo "⛓️  [3/3] Blockchain…"
python3 blockchain_registry/anchor_v2.py

echo "🌐 Lanzando dashboard…"
# Servidor local (mejor para demos y evita bloqueos del navegador con file://)
PORT=8765
python3 -m http.server "$PORT" >/dev/null 2>&1 &
SRV_PID=$!
sleep 1

# Abre el dashboard interactivo (ajusta archivo si deseas otro)
open "http://localhost:$PORT/demo_interactivo.html"

# Abre los PDFs
open rpa_secop/data/raw/EXP-2025-001.pdf
open rpa_secop/data/raw/EXP-2025-002.pdf
open rpa_secop/data/raw/EXP-2025-003.pdf

echo
echo "🎬 Listo para grabar:"
echo "   1) Presiona ⌘⇧5  → 'Grabar toda la pantalla'"
echo "   2) Muestra el dashboard (scroll suave) y los PDFs"
echo "   3) Al terminar, detén la grabación (⌘⌃Esc)"
echo
read -p "Pulsa Enter cuando termines para cerrar el servidor…"
kill $SRV_PID || true
echo "✅ Demo finalizado."
