# Simulación de RPA de ingesta SECOP
# Este script no scrapea SECOP real; genera archivos PDF dummy en ./out
import os, time, pathlib

def run():
    out = pathlib.Path(__file__).parent.parent / "out"
    out.mkdir(exist_ok=True)
    for i in range(1, 4):
        pdf_path = out / f"expediente_{i:03d}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n% Dummy expediente PDF\n")
        print(f"[RPA] Guardado {pdf_path}")
        time.sleep(0.5)

if __name__ == "__main__":
    print("[RPA] Inicio de ingesta simulada")
    run()
    print("[RPA] Fin")
