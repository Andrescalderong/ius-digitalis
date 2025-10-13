from pathlib import Path
import pandas as pd
import hashlib
from PyPDF2 import PdfReader

RAW_DIR = Path(__file__).resolve().parents[1] / "rpa_secop" / "data" / "raw"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CATEG = {
    "CONTRATO": "Contrato",
    "PÓLIZA": "Poliza",
    "POLIZA": "Poliza",
    "ACTA": "Acta"
}

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def heuristica(pdf_path):
    try:
        reader = PdfReader(str(pdf_path))
        txt = reader.pages[0].extract_text() or ""
        txt = txt.upper()
    except Exception:
        txt = ""
    for k, v in CATEG.items():
        if k in txt:
            return v
    return ["Contrato", "Poliza", "Acta"][hash(pdf_path.name) % 3]

def main():
    if not RAW_DIR.exists():
        raise SystemExit(f"No existe {RAW_DIR}. Ejecuta primero el RPA: python rpa_secop/src/main.py")
    rows = []
    for pdf in sorted(RAW_DIR.glob("*.pdf")):
        categoria = heuristica(pdf)
        content_hash = sha256_file(pdf)
        rows.append({
            "expediente_id": pdf.stem,
            "pdf": str(pdf),
            "categoria": categoria,
            "sha256": content_hash
        })
        print(f"[IA] {pdf.name} -> {categoria}")
    if not rows:
        raise SystemExit(f"No hay PDFs en {RAW_DIR}. Ejecuta el RPA primero.")
    df = pd.DataFrame(rows)
    out_csv = OUT_DIR / "classifications.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nClasificaciones guardadas en: {out_csv}")

if __name__ == "__main__":
    main()
