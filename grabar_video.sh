#!/bin/bash
clear
echo "🎥 Preparando demo para video..."
echo ""

# 1. Generar datos nuevos
echo "📊 Generando nuevos datos..."
python3 rpa_secop/src/main_fast.py > /dev/null
python3 ia_classifier/classify_v2.py > /dev/null
python3 blockchain_registry/anchor_v2.py > /dev/null

# 2. Actualizar dashboard
echo "🌐 Actualizando dashboard..."
python3 update_dashboard.py

# 3. Abrir dashboard
echo "✅ Abriendo dashboard en Chrome..."
open -a "Google Chrome" dashboard_live.html

echo ""
echo "🎬 Dashboard listo para grabar!"
echo ""
echo "Pasos para el video:"
echo "1. Graba la pantalla de Chrome"
echo "2. Muestra el dashboard (scroll lento)"
echo "3. Resalta las transacciones"
echo ""
echo "Para regenerar datos nuevos: ./grabar_video.sh"
