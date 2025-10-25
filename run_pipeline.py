#!/usr/bin/env python3
"""Pipeline completo IUS-DIGITALIS"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent

def run_phase(name, script, critical=True):
    """Ejecutar fase del pipeline"""
    print(f"\n{'='*60}")
    print(f"▶️  FASE: {name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            ["python3", str(script)],
            cwd=BASE,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ {name} completado\n")
            return True
        else:
            print(f"⚠️  {name} falló con código {result.returncode}\n")
            return not critical
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {name} excedió timeout\n")
        return not critical
    except Exception as e:
        print(f"❌ {name} error: {e}\n")
        return not critical

def main():
    start = datetime.now()
    
    print("\n" + "="*60)
    print("🚀 IUS-DIGITALIS PIPELINE COMPLETO")
    print(f"⏰ Inicio: {start.strftime('%H:%M:%S')}")
    print("="*60)
    
    phases = [
        ("📄 RPA - Generación PDFs", BASE / "rpa_secop/src/main.py", False),
        ("🤖 IA - Clasificación", BASE / "ia_classifier/classify_v2.py", True),
        ("⛓️  Blockchain - Anclaje", BASE / "blockchain_registry/anchor_v2.py", True)
    ]
    
    for name, script, critical in phases:
        if not script.exists():
            print(f"⚠️  {name}: Script no existe: {script}")
            if critical:
                print(f"❌ Pipeline abortado\n")
                sys.exit(1)
            continue
        
        if not run_phase(name, script, critical):
            if critical:
                print(f"❌ Pipeline abortado en: {name}\n")
                sys.exit(1)
    
    duration = (datetime.now() - start).total_seconds()
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETADO")
    print(f"⏱️  Duración: {duration:.2f}s")
    print("="*60 + "\n")
    
    # Resumen de outputs
    print("📊 OUTPUTS GENERADOS:")
    outputs = [
        ("RPA Metadata", BASE / "rpa_secop/data/metadata.json"),
        ("IA Classifications", BASE / "ia_classifier/outputs/classifications.csv"),
        ("Blockchain Anchors", BASE / "blockchain_registry/outputs/anchors.json")
    ]
    
    for label, path in outputs:
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {label}: {path.name} ({size} bytes)")
        else:
            print(f"   ❌ {label}: no encontrado")
    
    print()

if __name__ == "__main__":
    main()
