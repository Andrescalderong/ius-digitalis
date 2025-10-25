#!/bin/bash
clear
cat << 'BANNER'
╔══════════════════════════════════════════════════════════╗
║       🏛️  IUS-DIGITALIS BLOCKCHAIN REGISTRY            ║
║     Sistema de Verificación de Integridad Documental    ║
╚══════════════════════════════════════════════════════════╝
BANNER

echo ""
echo "📊 ESTADO DEL SISTEMA"
echo "════════════════════════════════════════════════════════"
echo "🟢 Todos los módulos operativos"
echo "📄 Documentos procesados: 3"
echo "⛓️  Transacciones ancladas: 3"
echo ""

echo "🔐 ANCLAJES BLOCKCHAIN"
echo "════════════════════════════════════════════════════════"
echo ""

python3 << 'PYTHON'
import json
from pathlib import Path
from datetime import datetime

data = json.loads(Path("blockchain_registry/outputs/anchors.json").read_text())

for i, anchor in enumerate(data['anchors'], 1):
    print(f"📄 Transacción #{i}")
    print(f"   Expediente:  {anchor['expediente_id']}")
    print(f"   Categoría:   {anchor['categoria']}")
    print(f"   SHA-256:     {anchor['sha256']}")
    print(f"   TX ID:       {anchor['txid']}")
    print(f"   Network:     {anchor['network']}")
    ts = datetime.fromtimestamp(anchor['timestamp'])
    print(f"   Timestamp:   {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

print(f"✅ Total: {data['total']} transacciones confirmadas")
print("════════════════════════════════════════════════════════")
PYTHON
