from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse, HTMLResponse
from pathlib import Path
import tempfile, subprocess, sys, json, datetime, hashlib

# --- Carpetas base ---
BASE_DIR = Path(__file__).resolve().parents[1]
CLI = BASE_DIR / "classify_v2.py"
UPLOADS = BASE_DIR / "web" / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)

# --- Funciones auxiliares ---
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _run_cli_on_text(text: str, model: str = "transformers") -> dict:
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    out_path = Path(tmp_path).with_suffix(".json")
    cmd = [sys.executable, str(CLI), "-f", tmp_path, "-m", model, "-o", str(out_path)]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    data = json.loads(out_path.read_text(encoding="utf-8"))
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    return data

def _run_cli_on_file(file_path: Path, model: str = "transformers") -> dict:
    out_path = file_path.with_suffix(".out.json")
    cmd = [sys.executable, str(CLI), "-f", str(file_path), "-m", model, "-o", str(out_path)]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    data = json.loads(out_path.read_text(encoding="utf-8"))
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    return data

# --- App principal ---
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style='font-family:Arial'>
    <h2>Clasificación</h2>
    <textarea id='textIn' rows='3' style='width:600px;' placeholder='Pega un texto legal...'></textarea><br>
    <select id='modelSel'>
        <option value='transformers' selected>transformers</option>
        <option value='rule-based'>rule-based</option>
        <option value='sklearn'>sklearn</option>
    </select>
    <button id='btnTxt'>Clasificar texto</button>
    <pre id='textOut'></pre>
    <hr>
    <form id='fileForm'>
        <input type='file' id='file' name='file'/>
        <button type='submit'>Subir y clasificar</button>
    </form>
    <pre id='fileOut'></pre>
    <script>
    async function postJSON(url, payload){
      const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      const txt = await r.text();
      let json; try { json = JSON.parse(txt); } catch(e){ json = {error: "Respuesta no JSON", raw: txt}; }
      return json;
    }
    async function postFile(url, fd){
      const r = await fetch(url, {method:'POST', body: fd});
      const txt = await r.text();
      let json; try { json = JSON.parse(txt); } catch(e){ json = {error: "Respuesta no JSON", raw: txt}; }
      return json;
    }
    document.getElementById('btnTxt').addEventListener('click', async ()=>{
      const text = document.getElementById('textIn').value;
      const model = document.getElementById('modelSel').value;
      const out = await postJSON('/api/classify-text', {text, model});
      document.getElementById('textOut').textContent = JSON.stringify(out, null, 2);
    });
    document.getElementById('fileForm').addEventListener('submit', async (e)=>{
      e.preventDefault();
      const fd = new FormData(e.target);
      const out = await postFile('/api/classify-file', fd);
      document.getElementById('fileOut').textContent = JSON.stringify(out, null, 2);
    });
    </script>
    </body>
    </html>
    """

@app.post("/api/classify-text")
async def api_classify_text(payload: dict = Body(...)):
    text = (payload or {}).get("text", "").strip()
    model = (payload or {}).get("model", "transformers")
    if not text:
        return JSONResponse({"error": "Falta 'text'"}, status_code=400)
    data = _run_cli_on_text(text, model=model)
    data["source"] = "text"
    data["received_at"] = datetime.datetime.utcnow().isoformat()
    return data

@app.post("/api/classify-file")
async def api_classify_file(file: UploadFile = File(...), model: str = Form("transformers")):
    contents = await file.read()
    if not contents:
        return JSONResponse({"error": "Archivo vacío"}, status_code=400)
    fname = f"{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{file.filename}"
    path = UPLOADS / fname
    path.write_bytes(contents)
    data = _run_cli_on_file(path, model=model)
    data["source"] = "file"
    data["source_file"] = file.filename
    data["upload_sha256"] = sha256_bytes(contents)
    data["received_at"] = datetime.datetime.utcnow().isoformat()
    return data