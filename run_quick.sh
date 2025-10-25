#!/bin/bash
set -e

echo "🚀 IUS-DIGITALIS - Iniciando..."
echo ""

# RPA
echo "📄 [1/3] RPA - Generación de PDFs..."
python3 rpa_secop/src/main.py
echo ""

# IA
echo "🤖 [2/3] IA - Clasificación..."
python3 ia_classifier/classify_v2.py
echo ""

# Blockchain
echo "⛓️  [3/3] Blockchain - Anclaje..."
python3 blockchain_registry/anchor_v2.py
echo ""

echo "✅ COMPLETADO"
