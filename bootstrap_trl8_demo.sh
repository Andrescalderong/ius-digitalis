#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p web_dashboard
# ─────────────────────────────────────────────────────────────
# server.py (API: /api/health, /api/run, /api/anchors + estáticos)
# ─────────────────────────────────────────────────────────────
cat > web_dashboard/server.py <<'PY'
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json, os, subprocess, sys, time, traceback
from pathlib import Path

HERE   = Path(__file__).resolve().parent
BASE   = HERE.parent
PDFDIR = BASE / "rpa_secop" / "data" / "raw"
ANCH   = BASE / "blockchain_registry" / "outputs" / "anchors.json"

def run_phase(title, *cmd):
    try:
        p = subprocess.run(list(cmd), cwd=str(BASE), text=True,
                           capture_output=True, check=False, timeout=120)
        return {"title":title, "cmd":" ".join(cmd), "returncode":p.returncode,
                "stdout":p.stdout, "stderr":p.stderr}
    except subprocess.TimeoutExpired:
        return {"title":title, "returncode":-1, "stdout":"", "stderr":"Timeout"}
    except Exception as e:
        return {"title":title, "returncode":-1, "stdout":"", "stderr":f"{e.__class__.__name__}: {e}"}

def load_anchors():
    if not ANCH.exists():
        return {"anchors":[], "total":0, "timestamp":int(time.time())}
    with open(ANCH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("anchors", [])
    data.setdefault("total", len(data["anchors"]))
    data.setdefault("timestamp", int(time.time()))
    return data

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Resolver estáticos contra la raíz del repo
        old = SimpleHTTPRequestHandler.translate_path(self, path)
        rel = os.path.relpath(old, os.getcwd())
        return str(BASE / rel)

    def _json(self, obj, status=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        try:
            if self.path in ("/", "/index.html"):
                self.send_response(302)
                self.send_header("Location","/web_dashboard/dashboard_trl8.html")
                self.end_headers()
                return
            if self.path.startswith("/api/health"):
                return self._json({"ok":True,"ts":int(time.time()),
                                   "pdf_dir":str(PDFDIR),"anchors":str(ANCH),
                                   "has_anchors":ANCH.exists()})
            if self.path.startswith("/api/anchors"):
                return self._json({"ok":True, **load_anchors()})
            if self.path.startswith("/api/run"):
                return self._run_pipeline()
            if self.path.startswith("/pdf/"):
                return super().do_GET()  # servimos desde BASE
            return super().do_GET()
        except Exception as e:
            traceback.print_exc()
            self._json({"ok":False,"error":str(e)}, 500)

    def do_POST(self):
        if self.path.startswith("/api/run"):
            return self._run_pipeline()
        self.send_error(404, "Not Found")

    def _run_pipeline(self):
        try:
            ANCH.parent.mkdir(parents=True, exist_ok=True)
            if ANCH.exists(): ANCH.unlink()
        except Exception:
            pass
        logs = []
        logs.append(run_phase("RPA",        sys.executable, "-u", "rpa_secop/src/main.py"))
        logs.append(run_phase("IA",         sys.executable, "-u", "ia_classifier/classify_v2.py"))
        logs.append(run_phase("Blockchain", sys.executable, "-u", "blockchain_registry/anchor_v2.py"))
        anchors = load_anchors()
        ok = all(x.get("returncode")==0 for x in logs) and anchors.get("total",0) > 0
        return self._json({"ok":ok, "timestamp":int(time.time()),
                           "logs":logs, "anchors":anchors.get("anchors",[]),
                           "total":anchors.get("total",0)})

def main():
    port = int(os.environ.get("PORT","8888"))
    srv = ThreadingHTTPServer(("localhost", port), Handler)
    print(f"🚀  Servidor TRL-8 en http://localhost:{port}", flush=True)
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()

if __name__ == "__main__":
    main()
PY

# ─────────────────────────────────────────────────────────────
# dashboard_trl8.html (UI limpia, botón Ejecutar)
# ─────────────────────────────────────────────────────────────
cat > web_dashboard/dashboard_trl8.html <<'HTML'
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>IUS-DIGITALIS · Demo TRL-8</title>
<style>
:root{--bg:#0b1020;--panel:#131a2b;--text:#e6f0ff;--muted:#9ab;--accent:#00ff9c;--warn:#ff5577;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,Segoe UI,Roboto}
.wrap{max-width:1100px;margin:32px auto;padding:0 16px}
h1{font-weight:800} .badge{background:#143;padding:2px 8px;border-radius:8px;color:#9ff;font-size:12px}
.bar{display:flex;gap:12px;align-items:center;margin:12px 0 24px}
button{background:var(--accent);color:#041410;border:0;padding:12px 18px;border-radius:12px;font-weight:700;cursor:pointer}
button:disabled{opacity:.6;cursor:not-allowed}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{background:var(--panel);border:1px solid #1f2a44;border-radius:16px;padding:16px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px}
.tx{border:1px dashed #28405f;border-radius:12px;padding:12px;margin-top:12px}
.row{display:grid;grid-template-columns:140px 1fr;gap:8px;margin:4px 0}
.label{color:var(--muted)} .ok{color:var(--accent);font-weight:700} .err{color:var(--warn);font-weight:700}
.links a{display:inline-block;margin-right:10px;margin-top:6px;text-decoration:none;color:#9df}
</style>
</head>
<body>
<div class="wrap">
  <h1>🧪 IUS-DIGITALIS — Demo TRL-8 <span class="badge">RPA → IA → Blockchain</span></h1>
  <div class="bar">
    <button id="run">▶ Ejecutar pipeline</button>
    <div id="status" class="mono">Listo.</div>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Registros</h3>
      <pre id="log-rpa" class="mono"></pre>
      <pre id="log-ia"  class="mono"></pre>
      <pre id="log-bc"  class="mono"></pre>
      <div class="links mono">
        Evidencias PDF:
        <a href="/pdf/EXP-2025-001.pdf" target="_blank">EXP-2025-001.pdf</a>
        <a href="/pdf/EXP-2025-002.pdf" target="_blank">EXP-2025-002.pdf</a>
        <a href="/pdf/EXP-2025-003.pdf" target="_blank">EXP-2025-003.pdf</a>
      </div>
    </div>
    <div class="card">
      <h3>Transacciones</h3>
      <div id="txs"></div>
    </div>
  </div>
</div>

<script>
const $=(s)=>document.querySelector(s);

function renderLogs(data){
  const logs=data.logs||[];
  const pick=(t)=>logs.find(x=>x.title===t)||{stdout:"",stderr:"",returncode:0};
  const fmt=(x)=>(x.stderr?x.stderr+"\n":"")+(x.stdout||"");
  $("#log-rpa").textContent="RPA\n"+fmt(pick("RPA"));
  $("#log-ia").textContent ="IA\n"+fmt(pick("IA"));
  $("#log-bc").textContent ="Blockchain\n"+fmt(pick("Blockchain"));
}

function renderAnchors(data){
  const box=$("#txs"); box.innerHTML="";
  (data.anchors||[]).forEach((a,i)=>{
    const ts=new Date(((a.timestamp)||data.timestamp||Date.now()/1000)*1000).toLocaleString('es-ES');
    box.insertAdjacentHTML('beforeend',`
      <div class="tx mono">
        <div class="row"><div class="label">#</div><div>${i+1}</div></div>
        <div class="row"><div class="label">Expediente</div><div>${a.expediente_id||'-'}</div></div>
        <div class="row"><div class="label">Categoría</div><div>${a.categoria||'-'}</div></div>
        <div class="row"><div class="label">SHA-256</div><div><code>${a.sha256||'-'}</code></div></div>
        <div class="row"><div class="label">TX ID</div><div><code>${a.txid||'-'}</code></div></div>
        <div class="row"><div class="label">Network</div><div>${a.network||'-'}</div></div>
        <div class="row"><div class="label">Timestamp</div><div>${ts}</div></div>
      </div>
    `);
  });
}

async function run(){
  const btn=$("#run"), st=$("#status");
  btn.disabled=true; st.textContent="Ejecutando…";
  try{
    const r=await fetch("/api/run",{method:"POST",cache:"no-store"});
    if(!r.ok) throw new Error("HTTP "+r.status);
    const data=await r.json();
    renderLogs(data); renderAnchors(data);
    st.innerHTML=data.ok?'<span class="ok">Completado</span>':'<span class="err">Con errores</span>';
  }catch(e){
    console.error(e);
    st.innerHTML='<span class="err">Error</span>';
  }finally{
    btn.disabled=false;
  }
}
$("#run").addEventListener("click", run);
</script>
</body>
</html>
HTML

# ─────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────
cat > run_trl8_web.sh <<'RUN'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -d .venv ]]; then source .venv/bin/activate; fi
python3 web_dashboard/server.py
RUN
chmod +x run_trl8_web.sh

echo "✅ Archivos creados: web_dashboard/server.py y web_dashboard/dashboard_trl8.html"
echo "➡️  Ejecuta ahora: ./run_trl8_web.sh"
