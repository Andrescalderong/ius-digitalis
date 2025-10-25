#!/bin/bash
clear
echo "=========================================="
echo "🚀 IUS-DIGITALIS - DEMO RÁPIDO"
echo "=========================================="
echo ""

# RPA Fast
python3 rpa_secop/src/main_fast.py

# IA
python3 ia_classifier/classify_v2.py

# Blockchain
python3 blockchain_registry/anchor_v2.py

echo ""
echo "✅ COMPLETADO - Outputs generados"
echo ""

# Mostrar resultados
echo "📊 RESULTADOS:"
cat blockchain_registry/outputs/anchors.json | python3 -m json.tool | head -40

echo ""
echo "🌐 Abriendo dashboard..."
open visualize.html
