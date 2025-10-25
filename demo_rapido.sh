#!/bin/bash
clear
echo "=========================================="
echo "🚀 IUS-DIGITALIS DEMO"
echo "=========================================="
echo ""
sleep 1

python3 rpa_secop/src/main.py
python3 ia_classifier/classify_v2.py  
python3 blockchain_registry/anchor_v2.py

echo ""
echo "📊 ANCLAJES BLOCKCHAIN:"
python3 -m json.tool blockchain_registry/outputs/anchors.json

echo ""
echo "🌐 Abriendo dashboard..."
open visualize.html
