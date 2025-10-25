# 📖 Guía de Usuario - IUS-DIGITALIS

## 🎯 ¿Qué hace este sistema?

IUS-DIGITALIS automatiza el ciclo completo de gestión documental legal:

1. **Genera** documentos PDF automáticamente
2. **Clasifica** el tipo de documento (Contrato, Póliza, Acta, etc.)
3. **Ancla** cada documento en blockchain para verificación de integridad

## 🚀 Uso Básico

### Paso 1: Ejecutar el Pipeline
```bash
# Desde el directorio ius-digitalis
python3 run_pipeline.py
```

Verás algo como:
```
============================================================
🚀 IUS-DIGITALIS PIPELINE COMPLETO
⏰ Inicio: 19:53:25
============================================================

▶️  FASE: 📄 RPA - Generación PDFs
[OK] Generado EXP-2025-001.pdf
[OK] Generado EXP-2025-002.pdf
[OK] Generado EXP-2025-003.pdf
✅ 📄 RPA completado

▶️  FASE: �� IA - Clasificación
📊 Resumen:
   Acta: 1
   Contrato: 1
   Poliza: 1
✅ 🤖 IA completado

▶️  FASE: ⛓️  Blockchain - Anclaje
[BC] EXP-2025-001.pdf -> tx 5e4d263f... CONFIRMED
[BC] EXP-2025-002.pdf -> tx f33abff1... CONFIRMED
[BC] EXP-2025-003.pdf -> tx 116b42fb... CONFIRMED
✅ ⛓️  Blockchain completado

✅ PIPELINE COMPLETADO
⏱️  Duración: 18.01s
```

### Paso 2: Ver Resultados
```bash
# Ver anclajes blockchain
cat blockchain_registry/outputs/anchors.json | python3 -m json.tool

# Ver clasificaciones
cat ia_classifier/outputs/classifications.csv
```

## 🔍 Verificar Integridad de un Documento

Cada documento tiene un **SHA-256** único. Para verificar:
```bash
# Calcular SHA-256 del PDF
shasum -a 256 rpa_secop/data/raw/EXP-2025-001.pdf

# Comparar con el anchor blockchain
grep "EXP-2025-001" blockchain_registry/outputs/anchors.json
```

Si los hashes coinciden → ✅ Documento íntegro
Si no coinciden → ⚠️ Documento modificado

## 📊 Interpretar los Resultados

### Archivo: `anchors.json`
```json
{
  "expediente_id": "EXP-2025-001.pdf",
  "categoria": "Contrato",
  "sha256": "0b7fa917...",        ← Hash del documento
  "txid": "d4d3cc64...",          ← ID de transacción blockchain
  "network": "ethereum-mainnet",  ← Red blockchain
  "timestamp": 1761353758         ← Tiempo Unix (cuando se ancló)
}
```

### Archivo: `classifications.csv`
```csv
file,label
EXP-2025-001.pdf,Contrato
EXP-2025-002.pdf,Poliza
EXP-2025-003.pdf,Acta
```

## 🆘 Preguntas Frecuentes

**P: ¿Qué es SHA-256?**
R: Un hash criptográfico que identifica unívocamente un archivo. Si cambias un bit del PDF, el SHA-256 cambia completamente.

**P: ¿Es blockchain real?**
R: Esta versión simula transacciones. Para producción se integraría con Ethereum, Polygon, etc.

**P: ¿Puedo agregar más categorías?**
R: Sí, edita `ia_classifier/classify_v2.py` y agrega nuevas categorías al diccionario.

**P: ¿Cómo limpio los datos?**
R: `rm -rf */outputs/* rpa_secop/data/raw/*` y vuelve a ejecutar el pipeline.

## 🎯 Casos de Uso

1. **Auditoría Legal**: Verificar que contratos no han sido alterados
2. **Compliance**: Demostrar integridad de documentos ante reguladores
3. **Due Diligence**: Validar autenticidad de documentación corporativa
4. **Gestión Documental**: Clasificación automática de repositorios legales

## 📞 Soporte

Para reportar bugs o sugerencias:
- Issues: [GitHub](https://github.com/tu-repo/ius-digitalis/issues)
- Email: soporte@ius-digitalis.com
