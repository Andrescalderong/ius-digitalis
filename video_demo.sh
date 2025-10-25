#!/bin/bash
clear
echo "=========================================="
echo "🎥 IUS-DIGITALIS - VIDEO DEMO"
echo "=========================================="
echo ""

# Matar servidores previos
pkill -f "http.server" 2>/dev/null

# Generar datos
echo "📊 Generando datos..."
python3 rpa_secop/src/main_fast.py
python3 ia_classifier/classify_v2.py
python3 blockchain_registry/anchor_v2.py

echo ""
echo "✅ Datos generados"
echo ""

# Mostrar resultados en terminal
echo "⛓️  ANCLAJES BLOCKCHAIN:"
python3 -m json.tool blockchain_registry/outputs/anchors.json | head -25

echo ""
echo "🌐 Iniciando servidor y abriendo dashboard..."
echo ""

# Servidor en background
python3 -m http.server 9999 > /dev/null 2>&1 &
SERVER_PID=$!

# Esperar y abrir navegador
sleep 2
open -a "Google Chrome" http://localhost:9999/visualize.html

echo "✅ Dashboard abierto en Chrome"
echo ""
echo "⏸️  Presiona ENTER cuando termines de grabar..."
read

# Limpiar
kill $SERVER_PID 2>/dev/null
echo "✅ Servidor detenido"
