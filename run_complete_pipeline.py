#!/usr/bin/env python3
"""Pipeline completo con manejo de errores"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
PYTHON = BASE / ".venv/bin/python3"

def run_phase(name, script, critical=True):
    """Ejecutar fase del pipeline"""
    print(f"\n{'='*60}")
    print(f"▶️  FASE: {name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [str(PYTHON), "-u", str(script)],
            capture_output=False,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ {name} completado\n")
            return True
        else:
            print(f"⚠️  {name} falló con código {result.returncode}\n")
            if critical:
                return False
            return True
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {name} excedió timeout de 60s\n")
        return not critical
    except Exception as e:
        print(f"❌ {name} error: {e}\n")
        return not critical

def main():
    start = datetime.now()
    
    print("\n" + "="*60)
    print("🚀 IUS-DIGITALIS PIPELINE COMPLETO")
    print(f"Inicio: {start.strftime('%H:%M:%S')}")
    print("="*60)
    
    phases = [
        ("RPA - Generación PDFs", BASE / "rpa_secop/src/main.py", True),
        ("IA - Clasificación", BASE / "ia_classifier/classify_v2.py", True),
        ("Blockchain - Anclaje", BASE / "blockchain_registry/anchor_v2.py", False)
    ]
    
    for name, script, critical in phases:
        if not script.exists():
            print(f"⚠️  {name}: Script no existe: {script}")
            if critical:
                sys.exit(1)
            continue
        
        if not run_phase(name, script, critical):
            if critical:
                print(f"\n❌ Pipeline abortado en: {name}")
                sys.exit(1)
    
    duration = (datetime.now() - start).total_seconds()
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETADO")
    print(f"⏱️  Duración total: {duration:.2f}s")
    print("="*60 + "\n")
    
    # Mostrar resumen
    print("📊 RESUMEN DE OUTPUTS:")
    outputs = [
        BASE / "rpa_secop/data/metadata.json",
        BASE / "ia_classifier/outputs/classifications.csv",
        BASE / "blockchain_registry/outputs/anchors.json"
    ]
    
    for path in outputs:
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {path.name} ({size} bytes)")
        else:
            print(f"   ❌ {path.name} (no existe)")
    
    print()

if __name__ == "__main__":
    main()
