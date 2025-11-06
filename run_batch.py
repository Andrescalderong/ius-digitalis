import os, json, hashlib, pathlib, subprocess, sys

INPUT_DIR = pathlib.Path("data/input")
OUTPUT_DIR = pathlib.Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {".txt", ".pdf"}  # PDF opcional (requiere PyMuPDF si está disponible)

def pdf_to_text(pdf_path: pathlib.Path) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception:
        return ""  # si no está instalado, se ignora el PDF
    text = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text.append(page.get_text("text"))
    return "\n".join(text).strip()

def write_temp_txt(src: pathlib.Path) -> pathlib.Path:
    """Convierte PDF a TXT temporal si es PDF; si es TXT, lo retorna igual."""
    if src.suffix.lower() == ".txt":
        return src
    if src.suffix.lower() == ".pdf":
        txt = pdf_to_text(src)
        if not txt:
            print(f"[WARN] PyMuPDF no disponible o PDF vacío: {src.name}. Se omite.")
            return None
        tmp = OUTPUT_DIR / f"{src.stem}.tmp.txt"
        tmp.write_text(txt, encoding="utf-8")
        return tmp
    return None

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main():
    files = [p for p in INPUT_DIR.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED]
    if not files:
        print(f"[INFO] No hay archivos en {INPUT_DIR}. Coloca .txt o .pdf")
        sys.exit(0)

    for i, src in enumerate(sorted(files), 1):
        proxy = write_temp_txt(src)
        if proxy is None:
            continue

        out = OUTPUT_DIR / f"{src.stem}_result.json"
        cmd = [
            sys.executable, "classify_v2.py",
            "-f", str(proxy),
            "-m", "transformers",               # o 'sklearn' si quieres velocidad
            "-o", str(out)
        ]
        print(f"[{i}/{len(files)}] →", " ".join(cmd))
        subprocess.run(cmd, check=True)

        # Adjunta un hash del TXT (trazabilidad mínima)
        try:
            data = json.loads(out.read_text(encoding="utf-8"))
            txt = proxy.read_text(encoding="utf-8")
            data["batch_text_hash"] = sha256_text(txt)
            out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[WARN] No se pudo anexar hash a {out.name}: {e}")

        # limpia temporales
        if proxy is not None and proxy.name.endswith(".tmp.txt"):
            proxy.unlink(missing_ok=True)

    print("\n✅ Clasificación por lotes completada. Revisa la carpeta 'outputs/'.")
if __name__ == "__main__":
    main()
