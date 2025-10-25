#!/usr/bin/env bash
set -euo pipefail

BASE="$(pwd)"
PORT=8888

say() { printf "\033[1;36m%s\033[0m\n" "$*"; }
err() { printf "\033[1;31m%s\033[0m\n" "$*" >&2; }

# 0) Activar venv si existe
if [[ -d .venv ]]; then source .venv/bin/activate; fi

# 1) Matar servidor previo en 8888 (si hubiera)
if lsof -i tcp:$PORT >/dev/null 2>&1; then
  say "🔪 Cerrando proceso previo en :$PORT…"
  lsof -ti tcp:$PORT | xargs -r kill || true
  sleep 1
fi

# 2) Levantar servidor TRL-8 en background
say "🚀 Levantando server en http://localhost:$PORT …"
nohup python3 web_dashboard/server.py > web_dashboard/server.log 2>&1 & echo $! > web_dashboard/.serve.pid
sleep 1

# 3) Esperar hasta que /api/health responda JSON ok:true (máx 20s)
say "⏳ Esperando /api/health …"
ATTEMPTS=40
ok="false"
for i in $(seq 1 $ATTEMPTS); do
  out="$(curl -sS --max-time 2 http://localhost:$PORT/api/health || true)"
  if echo "$out" | python3 -c 'import sys,json; 
import sys
try:
    d=json.load(sys.stdin)
    import sys
    sys.exit(0 if d.get("ok") else 1)
except Exception:
    sys.exit(2)' ; then
      ok="true"; break
  fi
  sleep 0.5
done
[[ "$ok" == "true" ]] || { err "❌ /api/health no respondió OK. Revisa web_dashboard/server.log"; exit 1; }
say "✅ Health OK"

# 4) Ejecutar pipeline real (RPA → IA → Blockchain)
say "⚙️  Ejecutando pipeline (POST /api/run)…"
run_json="$(curl -sS -X POST "http://localhost:$PORT/api/run" -H 'Content-Type: application/json' --data '{}')"
echo "$run_json" | python3 -m json.tool || { err "❌ Respuesta no JSON de /api/run"; exit 1; }

# 5) Verificar que exista anchors.json con transacciones
say "🔎 Consultando /api/anchors…"
anchors_json="$(curl -sS http://localhost:$PORT/api/anchors)"
echo "$anchors_json" | python3 -m json.tool >/dev/null || { err "❌ /api/anchors no devolvió JSON"; exit 1; }

# 6) Validación de integridad (hash local vs anchors.json)
say "🛡️  Verificando integridad SHA-256 vs anchors.json…"
python3 - <<'PY'
import json, subprocess, sys, pathlib
base = pathlib.Path.cwd()
anchors = json.loads((base/"blockchain_registry/outputs/anchors.json").read_text(encoding="utf-8"))
pdfdir = base/"rpa_secop/data/raw"

ok = 0
fail = 0
for a in anchors.get("anchors", []):
    fn = a.get("expediente_id")
    expect = a.get("sha256","")
    p = pdfdir / fn
    if not p.exists():
        print(f"❌ Falta PDF: {p}")
        fail += 1
        continue
    actual = subprocess.check_output(["shasum","-a","256",str(p)], text=True).split()[0]
    print(f"\n📄 {fn}\n   ACTUAL  : {actual}\n   ESPERADO: {expect}")
    if actual == expect and expect:
        print("   ✅ Coinciden"); ok += 1
    else:
        print("   ❌ NO coincide"); fail += 1

print(f"\nResumen: ✅ {ok}  ❌ {fail}")
sys.exit(0 if fail==0 else 1)
PY

# 7) Abrir dashboard y PDFs para la demo/TRL
say "🌐 Abriendo dashboard TRL-8…"
open "http://localhost:$PORT/web_dashboard/dashboard_trl8.html" >/dev/null 2>&1 || true

say "📂 Abriendo PDFs…"
open rpa_secop/data/raw/EXP-2025-001.pdf >/dev/null 2>&1 || true
open rpa_secop/data/raw/EXP-2025-002.pdf >/dev/null 2>&1 || true
open rpa_secop/data/raw/EXP-2025-003.pdf >/dev/null 2>&1 || true

say "🎬 Sugerencia de grabación: ⌘⇧5 → “Grabar toda la pantalla”, desplázate por el dashboard y abre 1 PDF."
say "✅ Listo. (Server sigue en /web_dashboard/.serve.pid; Ctrl+C NO lo detiene)."

