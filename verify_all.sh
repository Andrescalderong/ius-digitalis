#!/bin/bash

echo "🚀 Verificando IUS-DIGITALIS..."
echo ""

# 1. Ejecutar pipeline
echo "1️⃣ Ejecutando pipeline..."
python3 run_pipeline.py
echo ""

# 2. Ver estructura
echo "2️⃣ Estructura de archivos:"
find . -type f \( -name "*.py" -o -name "*.json" -o -name "*.csv" \) ! -path "*/.venv/*" ! -path "*/__pycache__/*" | sort
echo ""

# 3. Ejecutar tests
echo "3️⃣ Ejecutando tests..."
python3 tests/test_pipeline.py
echo ""

# 4. Mostrar resumen
echo "4️⃣ Resumen de outputs:"
ls -lh rpa_secop/data/metadata.json 2>/dev/null && echo "✅ RPA metadata" || echo "❌ RPA metadata"
ls -lh ia_classifier/outputs/classifications.csv 2>/dev/null && echo "✅ IA classifications" || echo "❌ IA classifications"
ls -lh blockchain_registry/outputs/anchors.json 2>/dev/null && echo "✅ Blockchain anchors" || echo "❌ Blockchain anchors"
echo ""

# 5. Abrir visualización
echo "5️⃣ Abriendo dashboard..."
open visualize.html

echo "✅ Verificación completa"
