#!/usr/bin/env bash
set -euo pipefail

# =============== CONFIG =================
BASE="$HOME/Documents/ius-digitalis"
PY="$BASE/.venv/bin/python3"
CANDIDATES=("demo_interactivo.html" "dashboard_live.html" "dashboard_con_pdfs.html" "dashboard.html" "visualize.html")
PORT=8000
SCROLL_SECONDS=45        # tiempo de autoscroll para el video
CHROME_BUNDLE="com.google.Chrome"
# =======================================

log(){ printf "\n\033[1;36m%s\033[0m\n" "$*"; }
ok(){  printf "\033[1;32m%s\033[0m\n" "$*"; }
err(){ printf "\033[1;31m%s\033[0m\n" "$*" 1>&2; }

# 0) Comprobaciones rápidas
[[ -x "$PY" ]] || { err "No encuentro el venv: $PY"; exit 1; }

log "⚙️  Activando venv y verificando dependencias…"
"$PY" - <<'PY'
import importlib, sys
for m in ("pandas","numpy","reportlab","tqdm"):
    try: importlib.import_module(m)
    except Exception as e: 
        print("❌ Falta módulo:", m, e); sys.exit(1)
print("✅ Dependencias OK")
PY

# 1) RPA
log "📄 [1/3] RPA — Generando PDFs y metadatos…"
"$PY" "$BASE/rpa_secop/src/main.py"

# 2) IA
log "🧠 [2/3] IA — Clasificando documentos…"
if [[ -f "$BASE/ia_classifier/classify_v2.py" ]]; then
  "$PY" "$BASE/ia_classifier/classify_v2.py"
else
  "$PY" "$BASE/ia_classifier/classify.py"
fi

# 3) Blockchain
log "⛓️  [3/3] Blockchain — Registrando anclajes…"
if [[ -f "$BASE/blockchain_registry/anchor_v2.py" ]]; then
  "$PY" "$BASE/blockchain_registry/anchor_v2.py"
else
  "$PY" "$BASE/blockchain_registry/anchor.py"
fi

# 4) Elegir dashboard
HTML=""
for f in "${CANDIDATES[@]}"; do
  [[ -f "$BASE/$f" ]] && HTML="$f" && break
done
[[ -n "$HTML" ]] || { err "No encontré ningún dashboard HTML en $BASE"; exit 1; }
ok "Dashboard seleccionado: $HTML"

# 5) Levantar servidor HTTP local (para evitar bloqueos de file://)
log "🌐 Iniciando servidor en http://localhost:${PORT}/ …"
# mata server previo si sigue vivo
if [[ -f "$BASE/.serve.pid" ]] && ps -p "$(cat "$BASE/.serve.pid")" >/dev/null 2>&1; then
  kill "$(cat "$BASE/.serve.pid")" || true
fi
( cd "$BASE" && "$PY" -m http.server "$PORT" >/dev/null 2>&1 ) & echo $! > "$BASE/.serve.pid"
sleep 1

URL="http://localhost:${PORT}/${HTML}"
log "🔎 URL: $URL"

# 6) Abrir Chrome (con fallback)
log "🖥️  Abriendo Chrome…"
if ! open -b "$CHROME_BUNDLE" "$URL" 2>/dev/null; then
  if ! open -a "Google Chrome" "$URL" 2>/dev/null; then
    log "⚠️  Chrome no disponible; abriendo navegador por defecto…"
    open "$URL"
  fi
fi

# 7) Autoscroll suave con AppleScript (Chrome)
log "🎥 Activando autoscroll para la grabación (${SCROLL_SECONDS}s)…"
osascript <<APPLESCRIPT >/dev/null 2>&1
on run
  tell application id "$CHROME_BUNDLE"
    activate
    delay 1
    try
      set theTab to active tab of front window
    on error
      make new window
      set theTab to active tab of front window
    end try
  end tell
  -- zoom al 110% y scroll suave
  tell application "System Events"
    keystroke "+" using {command down}
  end tell
  delay 0.5
  repeat ${SCROLL_SECONDS}
    tell application id "$CHROME_BUNDLE"
      tell active tab of front window to execute javascript "window.scrollBy({top: window.innerHeight/2, behavior:'smooth'});"
    end tell
    delay 1
  end repeat
end run
APPLESCRIPT

ok "🎬 ¡Listo! Graba con QuickTime: Archivo → Nueva grabación de pantalla."
ok "⏹  Para detener el servidor:  kill \$(cat \"$BASE/.serve.pid\"); rm \"$BASE/.serve.pid\""
