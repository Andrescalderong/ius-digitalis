# CHECKLIST DE IMPLEMENTACIÓN: IUS-DIGITALIS
## Lista de Verificación para Aplicar Correcciones

**Fecha**: 5 de noviembre de 2025  
**Propósito**: Guía paso a paso para implementar las correcciones en el repositorio  
**Tiempo estimado**: 30-45 minutos  
**Prerequisitos**: Git instalado, acceso al repositorio

---

## FASE 1: PREPARACIÓN (5 minutos)

### Paso 1.1: Descargar Archivos
- [ ] Acceder a `/mnt/user-data/outputs/` en Claude
- [ ] Descargar los 12 archivos generados:
  - [ ] `RESUMEN_EJECUTIVO_IUS_DIGITALIS.md`
  - [ ] `ANALISIS_TECNICO_EXHAUSTIVO.md`
  - [ ] `README_MEJORADO.md`
  - [ ] `test_pipeline.py`
  - [ ] `setup.sh`
  - [ ] `requirements_consolidado.txt`
  - [ ] `github-actions-workflow.yml`
  - [ ] `INDICE_MAESTRO.md`
  - [ ] `RESUMEN_EJECUTIVO_1_PAGINA.md`
  - [ ] `classify_v2.py` (si fue creado en conversación anterior)
  - [ ] `anchor_v2.py` (si fue creado en conversación anterior)
  - [ ] Guías partes 1, 2, 3 (si fueron creadas en conversación anterior)

**Tip**: Guardar todos en una carpeta temporal, ej: `~/Downloads/ius-digitalis-audit/`

### Paso 1.2: Crear Backup del Repositorio Actual
```bash
cd /ruta/a/tu/repositorio/ius-digitalis
git branch backup-pre-audit
git push origin backup-pre-audit
```

- [ ] Branch de backup creado
- [ ] Branch de backup subido a GitHub

**Justificación**: Permite revertir cambios si algo sale mal

### Paso 1.3: Crear Branch para Implementación
```bash
git checkout -b feat/audit-corrections
```

- [ ] Branch `feat/audit-corrections` creado

---

## FASE 2: IMPLEMENTACIÓN DE ARCHIVOS (15 minutos)

### Paso 2.1: Estructura de Directorios
```bash
# Crear directorios si no existen
mkdir -p tests
mkdir -p scripts
mkdir -p docs/audit
mkdir -p output
mkdir -p logs
mkdir -p .github/workflows
```

- [ ] Directorios creados

### Paso 2.2: Copiar Archivos Técnicos

#### Tests
```bash
cp ~/Downloads/ius-digitalis-audit/test_pipeline.py tests/
chmod +x tests/test_pipeline.py
```
- [ ] `test_pipeline.py` copiado a `/tests/`

#### Scripts
```bash
cp ~/Downloads/ius-digitalis-audit/setup.sh scripts/
chmod +x scripts/setup.sh
```
- [ ] `setup.sh` copiado a `/scripts/`
- [ ] Permisos de ejecución establecidos

#### Requirements
```bash
# Hacer backup del requirements.txt anterior (si existe)
if [ -f requirements.txt ]; then
    mv requirements.txt requirements.txt.backup
fi

cp ~/Downloads/ius-digitalis-audit/requirements_consolidado.txt requirements.txt
```
- [ ] `requirements.txt` antiguo respaldado (si existía)
- [ ] Nuevo `requirements.txt` copiado a raíz

#### GitHub Actions
```bash
# Hacer backup del workflow anterior (si existe)
if [ -f .github/workflows/python-app.yml ]; then
    mv .github/workflows/python-app.yml .github/workflows/python-app.yml.backup
fi

cp ~/Downloads/ius-digitalis-audit/github-actions-workflow.yml .github/workflows/python-app.yml
```
- [ ] Workflow anterior respaldado (si existía)
- [ ] Nuevo workflow copiado a `.github/workflows/`

### Paso 2.3: Copiar Código Corregido

#### Clasificador v2
```bash
# Hacer backup del clasificador anterior
if [ -f classify/classify_v2.py ]; then
    mv classify/classify_v2.py classify/classify_v2.py.backup
fi

cp ~/Downloads/ius-digitalis-audit/classify_v2.py classify/
```
- [ ] Clasificador anterior respaldado
- [ ] Nuevo `classify_v2.py` copiado

#### Anclaje Blockchain v2
```bash
# Hacer backup del anclaje anterior
if [ -f blockchain/anchor_v2.py ]; then
    mv blockchain/anchor_v2.py blockchain/anchor_v2.py.backup
fi

cp ~/Downloads/ius-digitalis-audit/anchor_v2.py blockchain/
```
- [ ] Anclaje anterior respaldado
- [ ] Nuevo `anchor_v2.py` copiado

### Paso 2.4: Copiar Documentación

#### README
```bash
# Hacer backup del README anterior
mv README.md README.md.backup

cp ~/Downloads/ius-digitalis-audit/README_MEJORADO.md README.md
```
- [ ] README anterior respaldado
- [ ] Nuevo README copiado

#### Documentación de Auditoría
```bash
cp ~/Downloads/ius-digitalis-audit/RESUMEN_EJECUTIVO_IUS_DIGITALIS.md docs/audit/
cp ~/Downloads/ius-digitalis-audit/ANALISIS_TECNICO_EXHAUSTIVO.md docs/audit/
cp ~/Downloads/ius-digitalis-audit/INDICE_MAESTRO.md docs/audit/
cp ~/Downloads/ius-digitalis-audit/RESUMEN_EJECUTIVO_1_PAGINA.md docs/audit/
```
- [ ] Documentos de auditoría copiados a `docs/audit/`

#### Guías de Usuario (si existen)
```bash
# Solo si fueron generadas en conversación anterior
if [ -f ~/Downloads/ius-digitalis-audit/GUIA_COMPLETA_PARTE1.md ]; then
    cp ~/Downloads/ius-digitalis-audit/GUIA_COMPLETA_PARTE*.md docs/
fi
```
- [ ] Guías de usuario copiadas (si aplica)

---

## FASE 3: VERIFICACIÓN LOCAL (10 minutos)

### Paso 3.1: Ejecutar Script de Setup
```bash
./scripts/setup.sh --dev
```

**Output esperado**:
```
==================================
  Detectando Entorno
==================================

✓ Sistema operativo detectado: [tu SO]
✓ Python 3.x encontrado
✓ pip encontrado

[... más output ...]

✓ Setup completado exitosamente
```

- [ ] Script de setup ejecutado sin errores
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas

### Paso 3.2: Activar Entorno Virtual
```bash
# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

- [ ] Entorno virtual activado (ver `(venv)` en prompt)

### Paso 3.3: Verificar Instalación de Dependencias
```bash
pip list | grep -E "(anthropic|web3|spacy|pytest)"
```

**Output esperado**:
```
anthropic           0.5.x
web3                6.x.x
spacy               3.5.x
pytest              7.4.x
```

- [ ] Dependencias críticas instaladas correctamente

### Paso 3.4: Ejecutar Tests Localmente
```bash
pytest tests/ --verbose
```

**Output esperado**:
```
tests/test_pipeline.py::TestImports::test_classify_module_imports PASSED
tests/test_pipeline.py::TestImports::test_blockchain_module_imports PASSED
[... más tests ...]

===================== X passed in Y.YY seconds =====================
```

- [ ] Tests ejecutados exitosamente
- [ ] Sin fallos críticos

**Nota**: Algunos tests pueden skipearse si módulos opcionales no están disponibles. Esto es normal.

### Paso 3.5: Verificar Ausencia de Rutas Hardcodeadas
```bash
# Buscar rutas problemáticas en Python
grep -r "/home/" --include="*.py" --exclude-dir="venv" --exclude-dir=".venv"
grep -r "/Users/" --include="*.py" --exclude-dir="venv" --exclude-dir=".venv"
grep -r "C:\\" --include="*.py" --exclude-dir="venv" --exclude-dir=".venv"

# Buscar en scripts shell
grep -r "$HOME/Documents" --include="*.sh"
```

**Output esperado**: Ninguna coincidencia (o solo en archivos de backup)

- [ ] Sin rutas hardcodeadas encontradas

---

## FASE 4: COMMIT Y PUSH (5 minutos)

### Paso 4.1: Review de Cambios
```bash
git status
git diff
```

- [ ] Revisar que solo se modificaron archivos esperados
- [ ] Sin cambios accidentales en otros archivos

### Paso 4.2: Stage de Archivos
```bash
git add .
```

- [ ] Archivos staged para commit

### Paso 4.3: Commit con Mensaje Descriptivo
```bash
git commit -m "feat: corregir pipeline CI/CD, estandarizar rutas y consolidar dependencias

- Agregar tests unitarios en /tests/test_pipeline.py para validar pipeline
- Implementar script de setup universal sin rutas hardcodeadas
- Consolidar dependencias en requirements.txt único en raíz
- Corregir workflow de GitHub Actions (.github/workflows/python-app.yml)
- Actualizar classify_v2.py con detección de entorno automática
- Actualizar anchor_v2.py con rutas adaptativas
- Mejorar README con instrucciones de instalación actualizadas
- Agregar documentación de auditoría en docs/audit/

Resolves: #[número de issue si existe]"
```

- [ ] Commit realizado con mensaje descriptivo

### Paso 4.4: Push a GitHub
```bash
git push origin feat/audit-corrections
```

- [ ] Branch subido a GitHub

---

## FASE 5: VERIFICACIÓN EN GITHUB (5 minutos)

### Paso 5.1: Crear Pull Request
1. Ir a: `https://github.com/[usuario]/ius-digitalis/pulls`
2. Click en "New pull request"
3. Base: `main` ← Compare: `feat/audit-corrections`
4. Título: "Correcciones de auditoría técnica: Pipeline CI/CD, rutas y dependencias"
5. Descripción: Copiar desde commit message
6. Click "Create pull request"

- [ ] Pull request creado

### Paso 5.2: Verificar GitHub Actions
1. En el PR, ir a la pestaña "Checks"
2. Esperar a que GitHub Actions ejecute (2-5 minutos)

**Checks esperados**:
- [ ] ✅ Linting (black, flake8) → Pasó
- [ ] ✅ Tests (pytest) → Pasó
- [ ] ✅ Security (safety) → Pasó

**Si hay fallos**:
- [ ] Revisar logs en GitHub Actions
- [ ] Corregir localmente
- [ ] Hacer nuevo commit y push

### Paso 5.3: Merge del Pull Request
Una vez que todos los checks pasen:

- [ ] Review del código (opcional, por otro desarrollador)
- [ ] Click en "Merge pull request"
- [ ] Click en "Confirm merge"
- [ ] Click en "Delete branch" (opcional, limpieza)

---

## FASE 6: VERIFICACIÓN POST-MERGE (5 minutos)

### Paso 6.1: Actualizar Branch Local
```bash
git checkout main
git pull origin main
```

- [ ] Branch `main` actualizado localmente

### Paso 6.2: Verificar en Producción (si aplica)
Si el repositorio tiene deployment automático:

- [ ] Verificar que el deployment se ejecutó
- [ ] Probar funcionalidad básica en producción
- [ ] Monitorear logs por errores

### Paso 6.3: Notificar al Equipo
- [ ] Enviar mensaje al equipo con resumen de cambios
- [ ] Compartir enlace a documentación en `docs/audit/`
- [ ] Solicitar que todos actualicen sus entornos locales:
  ```bash
  git pull origin main
  ./scripts/setup.sh --dev
  ```

---

## TROUBLESHOOTING

### Problema: Tests fallan localmente
**Solución**:
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# Verificar estructura de directorios
ls -la tests/
ls -la .github/workflows/

# Ejecutar tests con más verbose
pytest tests/ -vv
```

### Problema: GitHub Actions falla en "Install dependencies"
**Solución**:
- Verificar que `requirements.txt` está en la raíz del repositorio
- Revisar logs de GitHub Actions para ver qué dependencia específica falla
- Verificar que versiones en `requirements.txt` son compatibles

### Problema: Script setup.sh no tiene permisos
**Solución**:
```bash
chmod +x scripts/setup.sh
git add scripts/setup.sh
git commit -m "fix: agregar permisos de ejecución a setup.sh"
git push
```

### Problema: Rutas aún hardcodeadas en archivos antiguos
**Solución**:
- Identificar archivos con `grep -r "/home/" --include="*.py"`
- Editar manualmente para usar rutas relativas
- Ejemplo de corrección:
  ```python
  # Antes
  file_path = "/home/usuario/Documents/ius-digitalis/data.json"
  
  # Después
  import os
  base_dir = os.path.dirname(os.path.abspath(__file__))
  file_path = os.path.join(base_dir, "data.json")
  ```

---

## VALIDACIÓN FINAL

### Checklist de Validación Completa

- [ ] ✅ Pipeline CI/CD funciona (GitHub Actions pasa)
- [ ] ✅ Instalación funciona en 1 comando (`pip install -r requirements.txt`)
- [ ] ✅ No hay rutas hardcodeadas en código
- [ ] ✅ Tests unitarios ejecutan exitosamente
- [ ] ✅ Documentación actualizada y accesible
- [ ] ✅ Código corregido funcionando (classify_v2.py, anchor_v2.py)
- [ ] ✅ Equipo notificado de cambios
- [ ] ✅ Backup de versión anterior disponible

---

## MÉTRICAS DE ÉXITO

Después de implementar las correcciones, deberías observar:

| Métrica | Antes | Después | ✓ |
|---------|-------|---------|---|
| Tiempo de setup | 45-60 min | 5-10 min | [ ] |
| Éxito de pipeline | 0% | 100% | [ ] |
| Conflictos de instalación | 3-5 | 0 | [ ] |
| Compatibilidad entre SOs | 30% | 100% | [ ] |
| Tests ejecutando | No | Sí | [ ] |

---

## CONTACTO PARA SOPORTE

Si encuentras problemas durante la implementación:

1. **Revisar documentación detallada**:
   - `docs/audit/ANALISIS_TECNICO_EXHAUSTIVO.md` (análisis profundo)
   - `docs/audit/INDICE_MAESTRO.md` (navegación de archivos)

2. **Buscar en GitHub Issues**:
   - Buscar issues similares
   - Crear nuevo issue con logs completos

3. **Revertir si es necesario**:
   ```bash
   git checkout backup-pre-audit
   git push origin backup-pre-audit --force
   ```

---

**Checklist creado por**: Sistema de Auditoría Técnica  
**Última actualización**: 5 de noviembre de 2025  
**Versión**: 1.0  
**Tiempo estimado total**: 30-45 minutos
