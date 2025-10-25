#!/usr/bin/env python3
from pathlib import Path

print("🔍 Verificando dependencias...")
for lib in ['pandas', 'numpy', 'tqdm', 'reportlab']:
    try:
        __import__(lib)
        print(f"✅ {lib}")
    except:
        print(f"❌ {lib}")

print("\n🔍 Estructura:")
base = Path(__file__).parent
for nombre, ruta in {
    "PDFs": base / "rpa_secop/data/raw",
    "Outputs": base / "ia_classifier/outputs",
    "Logger": base / "utils/logger.py",
    "Clasificador": base / "ia_classifier/classify_v2.py"
}.items():
    print(f"{'✅' if ruta.exists() else '❌'} {nombre}: {ruta}")

print("\n🎯 Listo!")
