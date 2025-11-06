from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import datetime, hashlib, sys, io, re, socket
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import json, glob, os

# -----------------------------
# App & Middleware (debe ir primero)
# -----------------------------
app = FastAPI(
    title="IUS‑Digitalis API",
    description="API en español para clasificar texto y archivos de expedientes contractuales.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Modelos
# -----------------------------
class TextIn(BaseModel):
    text: str = Field(..., description="Texto a clasificar", min_length=1, examples=["Contrato de prestación de servicios..."])

class TextOut(BaseModel):
    ok: bool = Field(..., description="Indica si la petición fue procesada correctamente")
    echo: str = Field(..., description="Eco del texto recibido")
    ts: datetime.datetime = Field(..., description="Marca de tiempo ISO8601")

# ----- Campos estructurados -----
class Amount(BaseModel):
    raw: Optional[str] = Field(None, description="Cadena original detectada para el valor")
    value: Optional[float] = Field(None, description="Valor numérico normalizado en la moneda indicada")
    currency: Optional[str] = Field(None, description="Moneda detectada, p. ej., COP")

class Dates(BaseModel):
    start: Optional[str] = Field(None, description="Fecha de inicio ISO8601 si se detecta")
    end: Optional[str] = Field(None, description="Fecha de fin ISO8601 si se detecta")
    months: Optional[int] = Field(None, description="Duración aproximada en meses si hay dos fechas")

class FileOut(BaseModel):
    source_file: str = Field(..., description="Nombre original del archivo subido")
    upload_path: str = Field(..., description="Ruta local donde se guardó el archivo")
    hash: str = Field(..., description="SHA-256 del contenido recibido")
    received_at: datetime.datetime = Field(..., description="Marca de tiempo ISO8601")
    n_pages: Optional[int] = Field(None, description="Número de páginas si es PDF")
    text_excerpt: Optional[str] = Field(None, description="Primeros 1.000 caracteres del texto extraído")
    labels: Optional[List[str]] = Field(None, description="Etiquetas heurísticas detectadas en el texto")
    notes: Optional[str] = Field(None, description="Notas del sistema (p. ej., librería faltante)")
    # Campos estructurados
    objeto: Optional[str] = Field(None, description="Objeto del contrato si se detecta")
    amount: Optional['Amount'] = Field(None, description="Valor detectado")
    dates: Optional['Dates'] = Field(None, description="Fechas relevantes detectadas")
    contractor: Optional[str] = Field(None, description="Contratista si se detecta")
    anchor: Optional[dict] = Field(None, description="Datos de anclaje (simulado) en blockchain si existe")

# -----------------------------
# Página Home (UI)
# -----------------------------
@app.get("/", response_class=HTMLResponse, summary="Home")
def home():
    return """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>IUS‑Digitalis · RCFC Legal</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <!-- Tipografías: títulos serif (estilo firma legal) + texto Montserrat -->
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    /* ======= Tokens de marca (ajustables) ======= */
    :root{
      --bg:#0b0f14;           /* Fondo principal */
      --card:#131a22;         /* Tarjetas */
      --ink:#e8edf5;          /* Texto principal */
      --ink-2:#a7b4c6;        /* Texto secundario */
      --primary:#c6a659;      /* Dorado RCFC (exacto) */
      --primary-2:#a4873b;    /* Dorado oscuro */
      --accent:#2b3a4a;       /* Azul profundo de apoyo */
      --line:#1e2a3b;         /* Bordes */
      --success:#22c55e;
      --radius:14px;
      --shadow:0 16px 36px rgba(0,0,0,.35);
      --pad:16px;
      --pad-lg:22px;
    }
    *{box-sizing:border-box}
    html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);font-family:'Montserrat', -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Ubuntu, Helvetica, Arial, sans-serif}
    a{color:var(--primary);text-decoration:none}
    a:hover{text-decoration:underline}
    /* ======= Barra superior ======= */
    .topbar{
      position:sticky; top:0; z-index:20;
      backdrop-filter: blur(8px);
      background: rgba(11,15,20,.7);
      border-bottom:1px solid var(--line);
    }
    .wrap{max-width:1080px;margin:0 auto;padding:0 var(--pad-lg)}
    .nav{
      display:flex;align-items:center;justify-content:space-between;height:64px;
    }
    .brand{display:flex;gap:12px;align-items:center}
    .logo{
      width:40px;height:40px;border-radius:8px;
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      display:inline-flex;align-items:center;justify-content:center;
      color:#1f1b10;font-weight:800;letter-spacing:.5px;
      border:1px solid rgba(255,255,255,.08);
    }
    .brand h1{
      margin:0;font-size:20px;font-weight:700; letter-spacing:.2px;
      font-family:'Playfair Display', serif;
    }
    .tag{
      display:inline-block;margin-top:4px;font-size:12px;padding:4px 8px;border-radius:999px;
      background: #d4af3722;border:1px solid #d4af3755;color:#ffe6a6
    }
    .btn{
      display:inline-flex;align-items:center;gap:8px;
      background: var(--primary); color:#1a1a1a;
      padding:10px 14px;border-radius:10px;border:none;cursor:pointer;font-weight:700;
    }
    .btn.alt{background:#101826;color:var(--ink);border:1px solid var(--line)}
    /* ======= Hero ======= */
    .hero{padding:18px 0 10px 0}
    .sub{color:var(--ink-2);font-size:13px;margin-top:6px}
    /* ======= Grid ======= */
    .grid{display:grid;grid-template-columns:1fr;gap:18px;margin:12px 0 24px 0}
    @media(min-width:900px){ .grid{grid-template-columns: 1fr 1fr; } }
    .card{
      background: var(--card);
      border:1px solid var(--line);
      border-radius: var(--radius);
      padding: var(--pad-lg);
      box-shadow: var(--shadow);
    }
    h3{margin:0 0 10px 0;font-size:16px;font-weight:700;font-family:'Playfair Display', serif}
    label{display:block;font-weight:600;margin:8px 0}
    textarea{
      width:100%;min-height:160px;border-radius:12px;border:1px solid var(--line);
      background:#0a1220;color:var(--ink);padding:12px;resize:vertical;
    }
    .muted{color:var(--ink-2);font-size:12px}
    .row{display:flex;gap:10px;align-items:center;margin-top:10px}
    .row .btn{background: var(--primary); color:#1f1b10}
    pre{
      background:#0a1220;border:1px solid var(--line);border-radius:12px;
      padding:12px;overflow:auto;max-height:280px;margin-top:10px
    }
    /* ======= Dropzone ======= */
    .drop{
      border:2px dashed var(--accent);padding:26px;border-radius:12px;text-align:center;color:#cbd5e1;
      transition: all .2s ease; background:#0a1220
    }
    .drop.dragover{background:#1a2633}
    /* ======= Progreso ======= */
    .progress{height:8px;background:#0a1220;border:1px solid var(--line);border-radius:999px;margin-top:10px;overflow:hidden}
    .bar{height:100%;width:0;background: linear-gradient(90deg, var(--primary), #ffe392)}
    /* ======= Toaster ======= */
    .toast{
      position:fixed;right:18px;bottom:18px;z-index:40;
      background:#0f1624;border:1px solid var(--line);color:var(--ink);
      padding:12px 14px;border-radius:10px;box-shadow: var(--shadow);display:none
    }
    .footer{margin:8px 0 24px 0;color:var(--ink-2);font-size:12px;display:flex;gap:10px;align-items:center;justify-content:space-between}
    .chips{display:flex;gap:8px;flex-wrap:wrap}
    .chip{display:inline-flex;gap:6px;align-items:center;padding:4px 8px;border-radius:999px;border:1px solid var(--line);background:#0e1526;color:#ffe6a6;font-size:12px}
    .copy{border:1px solid var(--line);background:#0e1526;color:var(--ink);padding:6px 10px;border-radius:8px;cursor:pointer}
    .badge{padding:2px 8px;border-radius:999px;font-size:12px;border:1px solid var(--line);display:inline-block}
    .g{background:#0d1f16;border-color:#1f6f43;color:#8ef0b2}  /* verde */
    .a{background:#1f1a0e;border-color:#a37b00;color:#ffd56a} /* ámbar */
    .r{background:#2a0e0e;border-color:#8a1f1f;color:#ff9a9a} /* rojo  */
    .cardmini{border:1px solid var(--line);background:#0e1526;border-radius:12px;padding:10px}
    .rowmini{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  </style>
</head>
<body>
  <!-- Barra -->
  <div class="topbar">
    <div class="wrap">
      <div class="nav">
        <div class="brand">
          <div class="logo">RC</div>
          <div>
            <h1>IUS‑Digitalis · Panel RCFC Legal</h1>
            <div class="tag">Transforma el caos de expedientes en trazabilidad 100 % confiable</div>
          </div>
        </div>
        <div>
          <a class="btn alt" href="/docs" target="_blank" rel="noopener">Ver API</a>
        </div>
      </div>
    </div>
  </div>

  <div class="wrap hero">
    <div class="sub">Convierte PDFs desordenados en datos confiables. Usa los paneles para probar la IA sin Postman.</div>
    <div class="grid">
      <!-- Texto -->
      <section class="card">
        <h3>1) Clasificar texto</h3>
        <label for="t">Pega un fragmento de contrato</label>
        <textarea id="t" placeholder="Ej.: Cláusula, objeto, valor o fecha…"></textarea>
        <div class="row">
          <button id="bt" class="btn">Clasificar texto</button>
          <span class="muted">Envía JSON a <code>/api/classify-text</code></span>
        </div>
        <div class="row">
          <button id="copyTo" class="copy">Copiar resultado</button>
        </div>
        <pre id="to">{}</pre>
      </section>

      <!-- Archivo -->
<section class="card">
        <h3>2) Subir y clasificar archivo</h3>
        <div id="drop" class="drop">Arrastra y suelta aquí un PDF o haz clic para elegir</div>
        <input id="f" type="file" accept=".pdf,.txt" style="display:none" />
        <div class="row">
          <span class="muted">Usa <code>/api/classify-file</code>. Guardamos el archivo y calculamos su huella (SHA‑256).</span>
        </div>
        <div class="progress"><div id="bar" class="bar"></div></div>
        <div class="row">
          <button id="copyFo" class="copy">Copiar resultado</button>
          <button id="anchorBtn" class="copy">Anclar hash (simulado)</button>
        </div>
        <div id="cards" style="display:none; margin-top:10px; gap:10px; flex-wrap:wrap" class="row">
          <div id="c_obj" class="chip" title="Objeto">Objeto: <span id="obj"></span></div>
          <div id="c_val" class="chip" title="Valor">Valor: <span id="val"></span></div>
          <div id="c_vig" class="chip" title="Vigencia">Vigencia: <span id="vig"></span></div>
          <div id="c_con" class="chip" title="Contratista">Contratista: <span id="con"></span></div>
          <div class="chip" title="Páginas">Páginas: <span id="pg"></span></div>
        </div>
        <pre id="fo">{}</pre>
      </section>
    </div>

    <!-- Auditoría viva -->
    <section class="card" style="grid-column: 1 / -1;">
      <h3>3) Auditoría viva (últimos documentos)</h3>
      <div class="row">
        <button id="refreshRecent" class="copy">Actualizar</button>
        <span class="muted">Listado de los últimos JSON generados en <code>/iusweb/uploads/</code></span>
      </div>
      <div id="recent" style="margin-top:10px;display:grid;grid-template-columns:1fr;gap:10px"></div>
    </section>

    <div class="footer">
      <div class="chips">
        <span class="chip">IA aplicada</span>
        <span class="chip">Índice inteligente</span>
        <span class="chip">Huella en blockchain</span>
      </div>
      <div>© <span id="yy"></span> RCFC Legal · Bogotá</div>
    </div>
  </div>

  <div id="toast" class="toast"></div>

  <script>
    const yy = document.getElementById('yy'); yy.textContent = new Date().getFullYear();
    const toast = (msg)=>{ const t=document.getElementById('toast'); t.textContent=msg; t.style.display='block'; setTimeout(()=>t.style.display='none', 2200); };

    async function postJSON(url, payload) {
      const r = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      const text = await r.text();
      try { return JSON.parse(text); } catch(e){ return { error:'Respuesta no JSON', raw:text }; }
    }

    function renderCards(j){
      const $ = (id)=>document.getElementById(id);
      const has = !!(j && (j.objeto || j.amount || (j.dates && (j.dates.start||j.dates.end)) || j.contractor));
      $('cards').style.display = has ? 'flex' : 'none';
      $('pg').textContent = j.n_pages || '—';
      if(j.objeto){ $('obj').textContent = j.objeto; $('c_obj').style.display='inline-flex'; } else { $('c_obj').style.display='none'; }
      if(j.amount){ 
        const v = (j.amount.value!=null) ? new Intl.NumberFormat('es-CO',{style:'currency',currency:(j.amount.currency||'COP')}).format(j.amount.value) : (j.amount.raw||'—');
        $('val').textContent = v; $('c_val').style.display='inline-flex';
      } else { $('c_val').style.display='none'; }
      if(j.dates && (j.dates.start||j.dates.end)){
        const s = [j.dates.start||'', j.dates.end?(' → '+j.dates.end):''].join('');
        const m = (j.dates.months!=null) ? ` (${j.dates.months} meses)` : '';
        $('vig').textContent = (s||'—') + m; $('c_vig').style.display='inline-flex';
      } else { $('c_vig').style.display='none'; }
      if(j.contractor){ $('con').textContent = j.contractor; $('c_con').style.display='inline-flex'; } else { $('c_con').style.display='none'; }
    }
    function monthsBetween(d1ISO, d2ISO){
      if(!d1ISO || !d2ISO) return null;
      try{
        const d1=new Date(d1ISO), d2=new Date(d2ISO);
        return (d2.getFullYear()-d1.getFullYear())*12 + (d2.getMonth()-d1.getMonth());
      }catch{ return null; }
    }
    function badgeClass(monthsLeft){
      if(monthsLeft==null) return '';
      if(monthsLeft < 3) return 'badge r';
      if(monthsLeft <= 9) return 'badge a';
      return 'badge g';
    }
    async function loadRecent(){
      try{
        const r = await fetch('/api/recent'); const arr = await r.json();
        const wrap = document.getElementById('recent'); wrap.innerHTML='';
        const todayISO = new Date().toISOString().slice(0,10);
        arr.forEach(item=>{
          const end = item?.dates?.end || null;
          const ml = end ? monthsBetween(todayISO, end) : null;
          const cls = badgeClass(ml);
          const div = document.createElement('div'); div.className='cardmini';
          div.innerHTML = `
            <div class="rowmini">
              <strong>${item.source_file||'—'}</strong>
              ${end ? `<span class="${cls}">${ml!=null?ml+' m':''} ${item.dates.start? (item.dates.start+' → '):''}${end}</span>` : ''}
              ${item.amount?.value!=null ? `<span class="badge">${new Intl.NumberFormat('es-CO',{style:'currency',currency:(item.amount.currency||'COP')}).format(item.amount.value)}</span>` : ''}
            </div>
            <div class="rowmini">
              ${item.objeto ? `<span class="chip" title="Objeto">${item.objeto}</span>` : ''}
              ${item.contractor ? `<span class="chip" title="Contratista">${item.contractor}</span>` : ''}
              <span class="chip" title="Páginas">${item.n_pages||'—'} pág.</span>
            </div>
          `;
          wrap.appendChild(div);
        });
      }catch(e){ toast('No se pudo cargar Auditoría viva'); }
    }

    // Texto
    document.getElementById('bt').addEventListener('click', async ()=>{
      const el = document.getElementById('t');
      const out = document.getElementById('to');
      const val = (el.value||'').trim();
      if(!val){ out.textContent = '⚠️ Escribe algún texto.'; toast('Escribe algún texto.'); return; }
      out.textContent = '⏳ Procesando...';
      const res = await postJSON('/api/classify-text', { text: val });
      out.textContent = JSON.stringify(res, null, 2);
      toast('Texto clasificado');
    });
    // Copiar resultados
    document.getElementById('copyTo').addEventListener('click', ()=>{
      const txt = document.getElementById('to').textContent || '';
      navigator.clipboard.writeText(txt); toast('Resultado copiado');
    });
    document.getElementById('copyFo').addEventListener('click', ()=>{
      const txt = document.getElementById('fo').textContent || '';
      navigator.clipboard.writeText(txt); toast('Resultado copiado');
    });

    // Archivo con progreso (XMLHttpRequest para trackear upload)
    const drop = document.getElementById('drop');
    const fileInput = document.getElementById('f');
    const bar = document.getElementById('bar');

    drop.addEventListener('click', ()=> fileInput.click());
    ;['dragenter','dragover'].forEach(ev => drop.addEventListener(ev, e=>{ e.preventDefault(); e.stopPropagation(); drop.classList.add('dragover'); }));
    ;['dragleave','drop'].forEach(ev => drop.addEventListener(ev, e=>{ e.preventDefault(); e.stopPropagation(); drop.classList.remove('dragover'); }));

    drop.addEventListener('drop', e => { if(e.dataTransfer.files.length){ handleFile(e.dataTransfer.files[0]); } });
    fileInput.addEventListener('change', e => { if(e.target.files.length){ handleFile(e.target.files[0]); } });

    function handleFile(file){
      if(!file){ return; }
      const fd = new FormData(); fd.append('file', file);
      bar.style.width='0%';
      const xhr = new XMLHttpRequest();
      xhr.open('POST','/api/classify-file', true);
      xhr.upload.onprogress = (e)=>{ if(e.lengthComputable){ bar.style.width = (e.loaded/e.total*100).toFixed(0)+'%'; } };
      xhr.onload = ()=>{
        (async ()=>{
          try{ const res = JSON.parse(xhr.responseText); document.getElementById('fo').textContent = JSON.stringify(res, null, 2); renderCards(res); }
          catch{ document.getElementById('fo').textContent = xhr.responseText; }
          try{ await loadRecent(); }catch(_){}
          toast('Archivo procesado');
          setTimeout(()=>{ bar.style.width='0%'; }, 800);
        })();
      };
      xhr.onerror = ()=>{ toast('Error al subir el archivo'); };
      xhr.send(fd);
    }

    // Cargar auditoría viva al iniciar
    document.addEventListener('DOMContentLoaded', ()=>{ loadRecent(); });
    document.getElementById('refreshRecent').addEventListener('click', ()=> loadRecent());

    // Anclaje simulado
    document.getElementById('anchorBtn').addEventListener('click', async ()=>{
      try{
        const txt = document.getElementById('fo').textContent||'';
        const j = JSON.parse(txt);
        if(!j.hash){ toast('No hay hash para anclar'); return; }
        const r = await postJSON('/api/anchor', { hash: j.hash });
        toast('Anclado: '+(r.txid||'ok'));
        // refrescar detalle si backend actualizó el JSON
        try{ await loadRecent(); }catch(_){}
      }catch{ toast('Resultado inválido'); }
    });
  </script>
</body>
</html>
"""

# -----------------------------
# Utilidades y configuración
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS = BASE_DIR / "iusweb" / "uploads"
UPLOADS.mkdir(exist_ok=True, parents=True)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# -----------------------------
# Extractores y clasificación simple
# -----------------------------
def _try_import_pypdf2():
    try:
        import PyPDF2  # type: ignore
        return PyPDF2
    except Exception:
        return None

def _try_import_pdf2image():
    try:
        from pdf2image import convert_from_bytes  # type: ignore
        return convert_from_bytes
    except Exception:
        return None

def _try_import_pytesseract():
    try:
        import pytesseract  # type: ignore
        return pytesseract
    except Exception:
        return None

def extract_text_from_pdf_bytes(data: bytes):
    """Devuelve (texto, n_pages, note). Si no hay librería, note explica el motivo."""
    note = ""
    text = ""
    pages = None
    PyPDF2 = _try_import_pypdf2()
    if PyPDF2 is None:
        note = "PyPDF2 no está instalado; se omitió la extracción de texto PDF."
        return text, pages, note
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(data))
        pages = len(reader.pages)
        chunks = []
        for i in range(pages):
            try:
                chunks.append(reader.pages[i].extract_text() or "")
            except Exception:
                chunks.append("")
        text = "\n".join(chunks).strip()
    except Exception as e:
        note = f"Error al leer PDF: {e.__class__.__name__}"
    return text, pages, note

def extract_text_with_ocr_pdf_bytes(data: bytes):
    """
    Devuelve (texto, n_pages, note) usando OCR para PDFs escaneados.
    Requiere: pdf2image + poppler y pytesseract + tesseract.
    Es tolerante: si faltan dependencias, devuelve note explicando.
    """
    convert_from_bytes = _try_import_pdf2image()
    pytesseract = _try_import_pytesseract()
    if convert_from_bytes is None or pytesseract is None:
        miss = []
        if convert_from_bytes is None: miss.append("pdf2image/poppler")
        if pytesseract is None: miss.append("pytesseract/tesseract")
        return "", None, "OCR no disponible: falta " + " y ".join(miss)
    try:
        images = convert_from_bytes(data, fmt="png")  # requiere poppler instalado en el sistema
        texts = []
        for im in images:
            try:
                txt = pytesseract.image_to_string(im, lang="spa+eng")
            except Exception:
                txt = ""
            texts.append(txt or "")
        text = "\n".join(texts).strip()
        return text, len(images), ("OCR aplicado" if text else "OCR intentado sin texto")
    except Exception as e:
        return "", None, f"OCR error: {e.__class__.__name__}"

def extract_text_from_txt_bytes(data: bytes):
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return data.decode(enc)
        except Exception:
            continue
    return ""

_LABEL_PATTERNS = [
    (r"\b(póliza|poliza)\b", "Póliza"),
    (r"\b(interventor|supervisor(a)?)\b", "Interventoría/Supervisión"),
    (r"\b(objeto del contrato|objeto)\b", "Objeto"),
    (r"\b(plazo|vigencia)\b", "Plazo/Vigencia"),
    (r"\b(valor|cuantía|cuantia|\$ ?\d)", "Valor"),
    (r"\b(garantía|garantia)\b", "Garantía"),
    (r"\b(obra pública|obra publica|obra)\b", "Obra pública"),
    (r"\b(adición|adicion|prórroga|prorroga)\b", "Modificaciones"),
]

def label_text_heuristic(text: str) -> List[str]:
    text_low = text.lower()
    labels = []
    for pat, tag in _LABEL_PATTERNS:
        if re.search(pat, text_low):
            labels.append(tag)
    # de-dup y orden estable
    seen = set()
    ordered = []
    for t in labels:
        if t not in seen:
            ordered.append(t); seen.add(t)
    return ordered[:8]

# -----------------------------
# Extractores de campos estructurados (heurísticos)
# -----------------------------
_MONTHS = {
    "enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
    "julio":7,"agosto":8,"septiembre":9,"setiembre":9,"octubre":10,"noviembre":11,"diciembre":12
}

def _to_iso(d: int, m: int, y: int) -> str:
    try:
        return datetime.date(y, m, d).isoformat()
    except Exception:
        return f"{y:04d}-{m:02d}-{d:02d}"

_RE_DATE_1 = re.compile(r"(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})", re.I)
_RE_DATE_2 = re.compile(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})")
_RE_DATE_3 = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_RE_AMOUNT = re.compile(r"(?:COP|COL|COL\$|\$)\s*[\d\.\,]+(?:\s*(?:millones|millón|millon|billones|billón))?", re.I)
_RE_CONTRACTOR = re.compile(r"(?:contratista|proveedor|adjudicatario)\s*[:\-]\s*(.+)", re.I)

# Nueva regex para meses de tenor y suma de meses a fecha
_RE_MONTHS_TENOR = re.compile(r"(?:plazo|vigencia)\s*(?:de)?\s*(\d{1,3})\s*mes(?:es)?", re.I)

def _add_months(y: int, m: int, d: int, k: int) -> str:
    # suma k meses a una fecha (y,m,d) y devuelve ISO8601
    ny = y + (m - 1 + k) // 12
    nm = (m - 1 + k) % 12 + 1
    # ajustar día fin de mes
    import calendar
    last = calendar.monthrange(ny, nm)[1]
    nd = min(d, last)
    try:
        return datetime.date(ny, nm, nd).isoformat()
    except Exception:
        return f"{ny:04d}-{nm:02d}-{nd:02d}"

def extract_objeto(text: str) -> Optional[str]:
    if not text: return None
    t = text[:4000]  # limitar búsqueda
    # Busca encabezados de "objeto" y toma el renglón siguiente o mismo párrafo
    m = re.search(r"\bobjeto\b[:\-]?\s*(.+)", t, re.I)
    if m:
        obj = m.group(1).strip()
        # Cortar si es demasiado largo o se va a otra sección
        obj = re.split(r"\n{2,}|^\s*\d+\)\s+", obj)[0].strip()
        return obj[:280]
    # Fallback: primeras dos líneas
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    return (" ".join(lines[:2]))[:180] if lines else None

def _parse_amount_raw(raw: str) -> (Optional[float], Optional[str]):
    if not raw: return None, None
    cur = "COP" if "cop" in raw.lower() or "$" in raw else None
    s = raw
    mult = 1.0
    if re.search(r"billon", raw, re.I) or re.search(r"billones|billón", raw, re.I):
        mult = 1_000_000_000.0
    elif re.search(r"millon|millón|millones", raw, re.I):
        mult = 1_000_000.0
    # quitar moneda y espacios
    s = re.sub(r"[^\d,\.]", "", s)
    # heurística CO: punto como mil, coma decimal
    s = s.replace(".", "").replace(",", ".")
    try:
        val = float(s) * mult
        return val, cur or "COP"
    except Exception:
        return None, cur or "COP"

def extract_amount(text: str) -> Optional[Amount]:
    if not text: return None
    m = _RE_AMOUNT.search(text)
    if not m: return None
    raw = m.group(0)
    val, cur = _parse_amount_raw(raw)
    return Amount(raw=raw, value=val, currency=cur)

def extract_dates(text: str) -> Optional[Dates]:
    if not text: return None
    start = end = None
    # 1) Fecha de inicio (varios formatos)
    m = _RE_DATE_1.search(text)
    if m:
        d = int(m.group(1)); mth = _MONTHS[m.group(2).lower()]; y = int(m.group(3))
        start = _to_iso(d, mth, y)
    else:
        m = _RE_DATE_2.search(text)
        if m:
            d = int(m.group(1)); mth = int(m.group(2)); y = int(m.group(3))
            if y < 100: y += 2000
            start = _to_iso(d, mth, y)
        else:
            m = _RE_DATE_3.search(text)
            if m:
                y = int(m.group(1)); mth = int(m.group(2)); d = int(m.group(3))
                start = _to_iso(d, mth, y)

    # 2) Buscar una segunda fecha explícita (fin)
    m2 = None
    rx_used = None
    for rx in (_RE_DATE_3, _RE_DATE_2, _RE_DATE_1):
        m2 = rx.search(text, (m.end() if m else 0))
        if m2:
            rx_used = rx
            break
    if m2 and rx_used is _RE_DATE_1:
        d = int(m2.group(1)); mth = _MONTHS[m2.group(2).lower()]; y = int(m2.group(3))
        end = _to_iso(d, mth, y)
    elif m2 and rx_used is _RE_DATE_2:
        d = int(m2.group(1)); mth = int(m2.group(2)); y = int(m2.group(3)); y = y+2000 if y<100 else y
        end = _to_iso(d, mth, y)
    elif m2 and rx_used is _RE_DATE_3:
        y = int(m2.group(1)); mth = int(m2.group(2)); d = int(m2.group(3))
        end = _to_iso(d, mth, y)

    # 3) Si no hay fin pero existe un tenor de meses (p.ej. "plazo 12 meses"), calcúlalo
    months = None
    mtenor = _RE_MONTHS_TENOR.search(text)
    if mtenor:
        try:
            months = int(mtenor.group(1))
        except Exception:
            months = None

    if start and (end is None) and months:
        try:
            y1, m1, d1 = [int(x) for x in start.split("-")]
            end = _add_months(y1, m1, d1, months)
        except Exception:
            pass

    # 4) Si hay dos fechas, computar meses aproximados
    if start and end and months is None:
        try:
            y1, m1, d1 = [int(x) for x in start.split("-")]
            y2, m2i, d2 = [int(x) for x in end.split("-")]
            months = (y2 - y1) * 12 + (m2i - m1)
        except Exception:
            months = None

    return Dates(start=start, end=end, months=months)

def extract_contractor(text: str) -> Optional[str]:
    if not text: return None
    m = _RE_CONTRACTOR.search(text)
    if not m: return None
    return m.group(1).strip()[:120]

# -----------------------------
# Endpoints de API (JSON)
# -----------------------------
@app.post(
    "/api/classify-text",
    summary="Clasificar texto",
    tags=["Clasificación"],
    response_model=TextOut,
    responses={
        200: {
            "description": "Respuesta exitosa",
            "content": {"application/json": {"example": {"ok": True, "echo": "Texto de prueba", "ts": "2025-01-01T12:00:00"}}},
        },
        400: {"description": "Solicitud inválida: falta 'text'", "content": {"application/json": {"example": {"error": "Falta 'text'"}}}},
    },
)
async def api_classify_text(payload: TextIn = Body(...)):
    text = payload.text.strip()
    if not text:
        return JSONResponse({"error": "Falta 'text'"}, status_code=400)
    return TextOut(ok=True, echo=text, ts=datetime.datetime.now())

@app.post(
    "/api/classify-file",
    summary="Subir y clasificar archivo",
    tags=["Clasificación"],
    response_model=FileOut,
    responses={
        200: {
            "description": "Archivo recibido",
            "content": {"application/json": {"example": {
                "source_file": "ejemplo.pdf",
                "upload_path": "/.../uploads/20250101T120000_ejemplo.pdf",
                "hash": "9f2f5a...abcd",
                "received_at": "2025-01-01T12:00:00",
            }}},
        },
        400: {"description": "Archivo vacío o no provisto", "content": {"application/json": {"example": {"error": "Archivo vacío"}}}},
    },
)
async def api_classify_file(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        return JSONResponse({"error": "Archivo vacío"}, status_code=400)

    # Guardar archivo con timestamp
    fname = f"{datetime.datetime.now():%Y%m%dT%H%M%S}_{file.filename}"
    path = UPLOADS / fname
    path.write_bytes(contents)

    # Extraer según extensión
    ext = (file.filename or "").lower()
    text = ""
    pages = None
    note = ""
    if ext.endswith(".pdf"):
        text, pages, note = extract_text_from_pdf_bytes(contents)
        if (not text or len(text.strip()) < 20):
            # Fallback: intentar OCR para PDFs escaneados
            ocr_text, ocr_pages, ocr_note = extract_text_with_ocr_pdf_bytes(contents)
            # Si OCR trajo texto, úsalo; combinar notas
            if ocr_text:
                text = ocr_text
                pages = pages or ocr_pages
            note = " | ".join([s for s in (note, ocr_note) if s])
    elif ext.endswith(".txt"):
        text = extract_text_from_txt_bytes(contents)
    else:
        note = "Tipo de archivo no reconocido para extracción automática (se admiten .pdf y .txt)."

    excerpt = (text[:1000] + ("…" if len(text) > 1000 else "")) if text else None
    labels = label_text_heuristic(text) if text else None

    # ---- Campos estructurados ----
    objeto = extract_objeto(text) if text else None
    amount = extract_amount(text) if text else None
    dates = extract_dates(text) if text else None
    contractor = extract_contractor(text) if text else None

    result = FileOut(
        source_file=file.filename,
        upload_path=str(path),
        hash=sha256_bytes(contents),
        received_at=datetime.datetime.now(),
        n_pages=pages,
        text_excerpt=excerpt,
        labels=labels,
        notes=(note or None),
        objeto=objeto,
        amount=amount,
        dates=dates,
        contractor=contractor,
    )
    # Guardar JSON junto al PDF
    try:
        json_path = path.with_suffix(path.suffix + ".json")
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(json.loads(result.model_dump_json()), fh, ensure_ascii=False, indent=2)
    except Exception as e:
        # No interrumpir flujo si falla el guardado
        pass
    return result

# -----------------------------
# Auditoría viva: endpoints y helpers
# -----------------------------

# Modelo para anclaje
class AnchorIn(BaseModel):
    hash: str = Field(..., description="Hash SHA-256 del documento a anclar")

def _update_json_by_hash(doc_hash: str, updater):
    """Busca JSON en uploads por hash y permite actualizar su contenido en sitio."""
    for fp in glob.glob(str(UPLOADS / "*.pdf.json")):
        try:
            with open(fp, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("hash") == doc_hash:
                newdata = updater(data) or data
                with open(fp, "w", encoding="utf-8") as fh:
                    json.dump(newdata, fh, ensure_ascii=False, indent=2)
                return True
        except Exception:
            continue
    return False

# Endpoint para listar últimos JSON
@app.get("/api/recent", summary="Últimos resultados JSON", tags=["Auditoría"])
def api_recent():
    files = sorted(glob.glob(str(UPLOADS / "*.pdf.json")), key=os.path.getmtime, reverse=True)[:10]
    out = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as fh:
                out.append(json.load(fh))
        except Exception:
            continue
    return out

# Endpoint para anclar hash (simulado)
@app.post("/api/anchor", summary="Anclar hash en blockchain (simulado)", tags=["Auditoría"])
def api_anchor(payload: AnchorIn):
    h = (payload.hash or "").strip()
    if not h:
        return JSONResponse({"error": "Falta hash"}, status_code=400)
    # Simular un txid determinístico
    now = datetime.datetime.now().isoformat()
    txid = f"sim-{h[:16]}-{int(datetime.datetime.now().timestamp())}"
    anchor_obj = {
        "txid": txid,
        "network": "simulated:polygon-mumbai",
        "anchored_at": now,
    }
    # Intentar actualizar el JSON correspondiente
    _update_json_by_hash(h, lambda d: {**d, "anchor": anchor_obj})
    return {"ok": True, "txid": txid, "anchor": anchor_obj}

# -----------------------------
# DEBUG
# -----------------------------
# -----------------------------
# DEBUG
# -----------------------------
print("MOD:", __file__)
print("TIENE app?:", isinstance(app, FastAPI))
print("RUTAS:", [getattr(r, 'path', '?') for r in app.routes], file=sys.stderr)

# -----------------------------
# Helper para encontrar un puerto libre preferido
# -----------------------------
def _find_free_port(preferred: int = 8000) -> int:
    """Devuelve un puerto libre; intenta el preferido y si no, uno aleatorio."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', preferred))
            return preferred
    except Exception:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

# -----------------------------
# Modo ejecutable local (python iusweb/app.py)
# -----------------------------
if __name__ == "__main__":
    import threading, time, webbrowser
    try:
        import uvicorn  # type: ignore
    except Exception as _e:
        print("Falta uvicorn. Instala con: pip install uvicorn[standard]")
        raise

    PORT = _find_free_port(8000)

    # Inicia el servidor en un hilo para no bloquear la UI
    def _run_server():
        uvicorn.run(app, host="127.0.0.1", port=PORT, reload=False)

    threading.Thread(target=_run_server, daemon=True).start()
    time.sleep(1.0)

    # Intenta abrir ventana nativa (lo más fácil para quien no es técnico)
    try:
        import webview  # type: ignore
        # Crea una ventana tipo app de escritorio
        webview.create_window("IUS‑Digitalis · RCFC Legal", f"http://127.0.0.1:{PORT}/", width=1100, height=800)
        webview.start()
    except Exception:
        # Si no hay pywebview, abre el navegador por defecto
        try:
            webbrowser.open(f"http://127.0.0.1:{PORT}/")
            print(f"Abrimos tu navegador. Si no se abre, visita: http://127.0.0.1:{PORT}/")
        except Exception:
            print(f"Inicia un navegador y visita: http://127.0.0.1:{PORT}/")
        # Mantener proceso vivo
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass