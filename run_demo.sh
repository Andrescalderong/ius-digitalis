#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/Documents/ius-digitalis"
PY="$BASE/.venv/bin/python3"
PIP="$BASE/.venv/bin/pip"
DASH_HTML=""

log() { printf "\n\033[1;32m%s\033[0m\n" "$*"; }
err() { printf "\n\033[1;31m%s\033[0m\n" "$*" >&2; }

cd "$BASE"

# 0) Entorno
if [[ ! -x "$PY" ]]; then
  log "⚙️  Creando venv…"
  python3 -m venv .venv
fi

log "⚙️  Activando venv y verificando dependencias…"
source .venv/bin/activate
$PIP install --quiet --upgrade pip wheel setuptools
$PIP install --quiet --only-binary=:all: numpy==2.2.1 pandas==2.2.3 reportlab==4.0.7 tqdm==4.66.1 python-dotenv==1.0.0

# 1) Generar PDFs (RPA)
log "📄 [1/3] RPA — Generando PDFs y metadatos…"
"$PY" rpa_secop/src/main.py

# 2) Clasificar (IA)
log "🧠 [2/3] IA — Clasificando documentos…"
if [[ -f ia_classifier/classify_v2.py ]]; then
  "$PY" ia_classifier/classify_v2.py
else
  "$PY" ia_classifier/classify.py
fi

# 3) Anclar en Blockchain (simulado)
log "⛓️  [3/3] Blockchain — Registrando anclajes…"
if [[ -f blockchain_registry/anchor_v2.py ]]; then
  "$PY" blockchain_registry/anchor_v2.py
else
  "$PY" blockchain_registry/anchor.py
fi

# 4) Elegir dashboard para mostrar
if [[ -f "$BASE/dashboard_live.html" ]]; then
  DASH_HTML="$BASE/dashboard_live.html"
elif [[ -f "$BASE/demo_interactivo.html" ]]; then
  DASH_HTML="$BASE/demo_interactivo.html"
elif [[ -f "$BASE/dashboard_con_pdfs.html" ]]; then
  DASH_HTML="$BASE/dashboard_con_pdfs.html"
elif [[ -f "$BASE/dashboard_ius_digitalis.html" ]]; then
  DASH_HTML="$BASE/dashboard_ius_digitalis.html"
else
  # fallback mínimo generado al vuelo si no hubiera ninguno
  DASH_HTML="$BASE/_dashboard_auto.html"
  "$PY" - <<'PYGEN'
import json, pathlib, datetime
base = pathlib.Path().resolve()
anchors = json.loads((base/"blockchain_registry/outputs/anchors.json").read_text(encoding="utf-8"))
html = f"""<!doctype html><meta charset="utf-8">
<title>IUS-DIGITALIS — Dashboard Auto</title>
<style>body{{font-family:system-ui;background:#0a0e27;color:#00ff41;padding:24px}}
.card{{background:#111a3a;border:1px solid #00ff41;border-radius:10px;padding:16px;margin:12px 0}}
.hash{{font-family:monospace;color:#ff6b35;word-break:break-all}}</style>
<h1>⛓️ IUS-DIGITALIS — Demo</h1>
<p>Generado: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<h2>Transacciones</h2>
"""
for i,a in enumerate(anchors.get("anchors",[]),1):
    html += f"""<div class="card">
    <h3>📄 Transacción #{i} — {a['expediente_id']}</h3>
    <p><b>Categoría:</b> {a.get('categoria','—')}</p>
    <p><b>SHA-256:</b> <span class="hash">{a['sha256']}</span></p>
    <p><b>TXID:</b> <span class="hash">{a['txid']}</span></p>
    <p><b>Red:</b> {a['network']}</p>
    <p><b>Timestamp:</b> {datetime.datetime.fromtimestamp(a['timestamp']).isoformat()}</p>
</div>"""
(pathlib.Path("_dashboard_auto.html")).write_text(html, encoding="utf-8")
PYGEN
fi

# 5) Abrir Chrome con el dashboard
log "🌐 Abriendo dashboard en Chrome…"
open -a "Google Chrome" "file://$DASH_HTML" >/dev/null 2>&1 || open "file://$DASH_HTML"

# 6) Tips rápidos para la grabación
log "🎬 Listo para grabar:"
echo "   • Abre QuickTime Player → Archivo → Nueva grabación de pantalla"
echo "   • En el dashboard: scroll suave por tarjetas y hashes"
echo "   • (Opcional) Abre también: rpa_secop/data/raw/*.pdf"
echo
log "✅ Demo ejecutado con éxito."
