from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path
import json, time, hashlib

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

EXPEDIENTES = [
    {"id": "EXP-2025-001", "titulo": "Contrato de Suministro de Equipos", "monto": 50000000},
    {"id": "EXP-2025-002", "titulo": "Póliza de Garantía", "monto": 0},
    {"id": "EXP-2025-003", "titulo": "Acta de Inicio de Obra", "monto": 0},
]

def crea_pdf(path, titulo, cuerpo):
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, h-72, titulo)
    c.setFont("Helvetica", 11)
    y = h-110
    for linea in cuerpo.split("\n"):
        c.drawString(72, y, linea)
        y -= 16
    c.showPage()
    c.save()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    registros = []
    for e in EXPEDIENTES:
        pdf_path = RAW_DIR / f"{e['id']}.pdf"
        crea_pdf(
            pdf_path,
            f"Expediente {e['id']}",
            f"Titulo: {e['titulo']}\nMonto: {e['monto']}\nFuente: SECOP (simulado)\nTimestamp: {int(time.time())}"
        )
        h = sha256_file(pdf_path)
        registros.append({
            "expediente_id": e["id"],
            "pdf": str(pdf_path),
            "sha256": h,
            "timestamp": int(time.time())
        })
        print(f"[OK] Generado {pdf_path.name}  sha256={h[:12]}...")

    meta_path = RAW_DIR.parent / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"expedientes": registros}, f, ensure_ascii=False, indent=2)

    print(f"\nListo. PDFs en: {RAW_DIR}")
    print(f"Metadatos en:   {meta_path}")

if __name__ == "__main__":
    main()
