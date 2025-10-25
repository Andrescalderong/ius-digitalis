#!/bin/bash

clear
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "    🎬 IUS-DIGITALIS - VIDEO DEMO"
echo "═══════════════════════════════════════════════════════════"
echo ""
sleep 2

echo "📋 PASO 1: Ejecutando Pipeline Completo..."
echo ""
sleep 2

python3 run_pipeline.py

echo ""
echo "═══════════════════════════════════════════════════════════"
sleep 2

echo ""
echo "📊 PASO 2: Visualizando Anclajes Blockchain..."
echo ""
sleep 2

python3 << 'PYTHON'
import json
from pathlib import Path
from datetime import datetime

data = json.loads(Path("blockchain_registry/outputs/anchors.json").read_text())

print("\n" + "="*70)
print("⛓️  BLOCKCHAIN ANCHORS - REGISTRO INMUTABLE")
print("="*70 + "\n")

for i, anchor in enumerate(data['anchors'], 1):
    print(f"📄 Transacción #{i}")
    print(f"   Expediente: {anchor['expediente_id']}")
    print(f"   Categoría:  {anchor['categoria']}")
    print(f"   SHA-256:    {anchor['sha256'][:32]}...")
    print(f"   TX ID:      {anchor['txid'][:32]}...")
    print(f"   Network:    {anchor['network']}")
    ts = datetime.fromtimestamp(anchor['timestamp'])
    print(f"   Timestamp:  {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

print(f"✅ Total: {data['total']} transacciones ancladas")
print("="*70 + "\n")
PYTHON

sleep 3

echo ""
echo "🌐 PASO 3: Abriendo Dashboard Web..."
echo ""
sleep 1

open visualize.html

sleep 2

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "    ✅ DEMO COMPLETADO"
echo "═══════════════════════════════════════════════════════════"
echo ""
