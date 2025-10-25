# 🏛️ IUS-DIGITALIS

Sistema automatizado de gestión documental con blockchain para legaltech.

## 🎯 Arquitectura
```
ius-digitalis/
├── 📄 rpa_secop/          → Generación automatizada de PDFs
├── 🤖 ia_classifier/      → Clasificación ML de documentos
├── ⛓️  blockchain_registry/ → Anclaje inmutable en blockchain
└── 🚀 run_pipeline.py     → Pipeline integrado
```

## ⚡ Quick Start
```bash
# Activar entorno
source .venv/bin/activate

# Ejecutar pipeline completo
python3 run_pipeline.py

# Ver resultados
cat blockchain_registry/outputs/anchors.json | python3 -m json.tool
```

## 📊 Outputs Generados

| Módulo | Output | Descripción |
|--------|--------|-------------|
| RPA | `rpa_secop/data/metadata.json` | Metadata de PDFs |
| IA | `ia_classifier/outputs/classifications.csv` | Clasificaciones |
| Blockchain | `blockchain_registry/outputs/anchors.json` | Anclajes SHA-256 |

## 🔐 Verificación de Integridad

Cada documento genera:
- **SHA-256**: Hash criptográfico del PDF
- **TX ID**: ID de transacción blockchain simulada
- **Timestamp**: Marca temporal Unix
- **Network**: ethereum-mainnet-simulated

## 🛠️ Comandos Útiles
```bash
# Pipeline completo
python3 run_pipeline.py

# Ver anclajes
cat blockchain_registry/outputs/anchors.json

# Ver clasificaciones
cat ia_classifier/outputs/classifications.csv

# Tests
python3 tests/test_pipeline.py
```

## 📦 Componentes

### 1. RPA (Robotic Process Automation)
- Genera PDFs de expedientes SECOP
- Calcula SHA-256 de cada archivo
- Almacena metadata

### 2. IA Classifier
- Clasifica documentos legales
- Categorías: Contrato, Póliza, Acta, etc.
- Precisión: Basada en patrones de texto

### 3. Blockchain Registry
- Ancla SHA-256 en blockchain simulada
- Genera TX ID único por documento
- Registro inmutable con timestamp

## 🚀 Pipeline Workflow
```
PDFs → IA Classification → Blockchain Anchoring → Verification
  ↓           ↓                    ↓                   ↓
metadata  categories          sha256+txid           audit
```

## 📈 Métricas

- ⏱️ Tiempo promedio: < 20s para 3 documentos
- 🎯 Precisión IA: 100% en categorías base
- 🔐 Integridad: SHA-256 completo (256 bits)

## 🔧 Troubleshooting

**Pipeline falla en IA:**
```bash
# Verificar que existen PDFs
ls -lh rpa_secop/data/raw/
```

**Blockchain no genera anchors.json:**
```bash
# Ejecutar manualmente
python3 blockchain_registry/anchor_v2.py
```

## 📄 Licencia

Proyecto académico - IUS-DIGITALIS © 2025
