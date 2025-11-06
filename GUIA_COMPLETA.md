# GUÍA COMPLETA: IUS-DIGITALIS
## Sistema de Clasificación Legal Automatizada y Anclaje Blockchain

**Versión:** 2.0.0  
**Fecha:** 2025-11-05  
**Autor:** Consultoría de Sistemas Legales Automatizados

---

## ÍNDICE

1. [Instalación y Configuración](#1-instalación-y-configuración)
2. [Uso Básico](#2-uso-básico)
3. [Uso Avanzado](#3-uso-avanzado)
4. [Personalización](#4-personalización)
5. [Producción y Despliegue](#5-producción-y-despliegue)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. INSTALACIÓN Y CONFIGURACIÓN

### 1.1 Requisitos del Sistema

**Requisitos mínimos:**
- Python 3.9 o superior
- 4GB RAM
- 10GB espacio en disco
- Sistema operativo: Linux, macOS, Windows 10+

**Requisitos recomendados:**
- Python 3.10+
- 8GB RAM
- 20GB espacio en disco
- GPU (opcional, para modelos Transformer)

### 1.2 Instalación Rápida

#### Opción A: Instalación Automática (Recomendada)

```bash
# 1. Clonar repositorio
git clone https://github.com/usuario/ius-digitalis.git
cd ius-digitalis

# 2. Ejecutar script de setup
./setup.sh

# 3. Activar entorno virtual
source venv/bin/activate

# 4. Verificar instalación
python test_pipeline.py
```

#### Opción B: Instalación Manual

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Actualizar pip
python -m pip install --upgrade pip setuptools wheel

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Descargar modelo spaCy
python -m spacy download es_core_news_sm

# 5. Configurar variables de entorno
cp .env.template .env
# Editar .env con tus configuraciones

# 6. Crear estructura de directorios
mkdir -p data/{raw,processed,models}
mkdir -p models/{classification,blockchain}
mkdir -p logs tests notebooks
```

### 1.3 Configuración Inicial

#### Archivo `.env`

```bash
# CONFIGURACIÓN GENERAL
PROJECT_NAME=ius-digitalis
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# BLOCKCHAIN (Modo simulación para desarrollo)
BLOCKCHAIN_NETWORK=simulation
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
BLOCKCHAIN_PRIVATE_KEY=your_key_here

# BASE DE DATOS
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ius_digitalis
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# MACHINE LEARNING
ML_MODEL_PATH=models/classification/model.pkl
ML_BATCH_SIZE=32
ML_USE_GPU=false
```

### 1.4 Verificación de Instalación

```bash
# Ejecutar tests
python test_pipeline.py

# Verificar versiones
python --version
pip list | grep -E "transformers|torch|scikit-learn"

# Test de clasificación
python classify_v2.py "Artículo 123 del Código Civil"

# Test de blockchain (simulación)
python anchor_v2.py test_data.json -n simulation
```

---

## 2. USO BÁSICO

### 2.1 Clasificación de Texto Simple

#### Desde Línea de Comandos

```bash
# Clasificar texto directo
python classify_v2.py "El contrato establece obligaciones mutuas entre las partes"

# Clasificar desde archivo
python classify_v2.py -f documento.txt -o resultado.json

# Usar modelo específico
python classify_v2.py -f doc.txt -m sklearn --model-path models/trained_model.pkl

# Modo verbose
python classify_v2.py -f doc.txt -v
```

#### Desde Python

```python
from classify_v2 import LegalClassifier, ModelConfig

# Inicializar clasificador
config = ModelConfig(model_type="rule-based")
classifier = LegalClassifier(config)

# Clasificar texto
text = "El artículo 123 del Código Penal establece..."
result = classifier.classify_text(text)

print(f"Categoría: {result.predicted_label}")
print(f"Confianza: {result.confidence:.2%}")
print(f"Tiempo: {result.processing_time_ms:.2f}ms")

# Guardar resultado
classifier.save_results(result, "output.json")
```

### 2.2 Clasificación por Lotes

```python
from classify_v2 import LegalClassifier, ModelConfig

classifier = LegalClassifier()

# Lista de textos
texts = [
    "Contrato de compraventa...",
    "Delito tipificado en...",
    "Amparo constitucional..."
]

# Clasificar lote
results = classifier.classify_batch(texts)

# Analizar resultados
for i, result in enumerate(results):
    print(f"\nDocumento {i+1}:")
    print(f"  Categoría: {result.predicted_label}")
    print(f"  Confianza: {result.confidence:.2%}")

# Guardar todos los resultados
classifier.save_results(results, "batch_results.json")
```

### 2.3 Anclaje en Blockchain

#### Modo Simulación (Desarrollo)

```python
from anchor_v2 import BlockchainAnchor, AnchorConfig, BlockchainNetwork

# Configurar en modo simulación
config = AnchorConfig(network=BlockchainNetwork.SIMULATION)
anchor = BlockchainAnchor(config)

# Datos a anclar
classification_data = {
    "text": "Documento legal...",
    "predicted_label": "civil",
    "confidence": 0.92,
    "timestamp": "2025-11-05T12:00:00"
}

# Anclar
record = anchor.anchor_classification(classification_data)

print(f"Anclado en bloque: {record.block_number}")
print(f"TX Hash: {record.transaction_hash}")
print(f"Document Hash: {record.document_hash}")

# Verificar
is_valid = anchor.verify_record(record)
print(f"Verificación: {'✓ Válido' if is_valid else '✗ Inválido'}")
```

#### Modo Red Real (Testnet)

```python
from anchor_v2 import BlockchainAnchor, AnchorConfig, BlockchainNetwork

# Configurar para Sepolia testnet
config = AnchorConfig(
    network=BlockchainNetwork.SEPOLIA,
    rpc_url="https://sepolia.infura.io/v3/YOUR_API_KEY",
    private_key="YOUR_PRIVATE_KEY",
    gas_limit=300000
)

anchor = BlockchainAnchor(config)

# Anclar (requiere ETH en testnet)
record = anchor.anchor_classification(classification_data)
```

### 2.4 Pipeline Completo

```python
from classify_v2 import LegalClassifier, ModelConfig
from anchor_v2 import BlockchainAnchor, AnchorConfig
import json

# 1. Clasificar
classifier = LegalClassifier(ModelConfig(model_type="rule-based"))
text = "Documento legal a procesar..."
classification = classifier.classify_text(text)

print(f"Clasificado como: {classification.predicted_label}")

# 2. Convertir a dict para blockchain
data = classification.to_dict()

# 3. Anclar en blockchain
anchor = BlockchainAnchor(AnchorConfig())
record = anchor.anchor_classification(data)

print(f"Anclado en blockchain: {record.transaction_hash}")

# 4. Guardar evidencia completa
evidence = {
    "classification": classification.to_dict(),
    "blockchain_record": record.to_dict()
}

with open("evidencia_completa.json", "w") as f:
    json.dump(evidence, f, indent=2)
```

---

## 3. USO AVANZADO

### 3.1 Entrenamiento de Modelos Personalizados

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib

# 1. Preparar datos de entrenamiento
texts = [...]  # Tus textos legales
labels = [...]  # Categorías correspondientes

# 2. Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42
)

# 3. Crear pipeline
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
    ('classifier', MultinomialNB())
])

# 4. Entrenar
pipeline.fit(X_train, y_train)

# 5. Evaluar
accuracy = pipeline.score(X_test, y_test)
print(f"Accuracy: {accuracy:.2%}")

# 6. Guardar modelo
joblib.dump(pipeline, 'models/classification/custom_model.pkl')
joblib.dump(pipeline.named_steps['vectorizer'], 'models/classification/vectorizer.pkl')
```

### 3.2 Fine-tuning de Modelos Transformer

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import TrainingArguments, Trainer
import torch

# 1. Cargar modelo base
model_name = "dccuchile/bert-base-spanish-wwm-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=len(LEGAL_CATEGORIES)
)

# 2. Preparar dataset
class LegalDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(texts, truncation=True, padding=True)
        self.labels = labels
    
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    
    def __len__(self):
        return len(self.labels)

train_dataset = LegalDataset(X_train, y_train, tokenizer)
test_dataset = LegalDataset(X_test, y_test, tokenizer)

# 3. Configurar entrenamiento
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    eval_strategy="epoch"
)

# 4. Entrenar
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

trainer.train()

# 5. Guardar
model.save_pretrained('models/classification/bert_finetuned')
tokenizer.save_pretrained('models/classification/bert_finetuned')
```

### 3.3 API REST con FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from classify_v2 import LegalClassifier, ModelConfig
from anchor_v2 import BlockchainAnchor, AnchorConfig
import uvicorn

app = FastAPI(title="IUS-DIGITALIS API", version="2.0.0")

# Inicializar servicios
classifier = LegalClassifier(ModelConfig())
anchor = BlockchainAnchor(AnchorConfig())

class ClassificationRequest(BaseModel):
    text: str
    anchor_to_blockchain: bool = False

class ClassificationResponse(BaseModel):
    predicted_label: str
    confidence: float
    processing_time_ms: float
    blockchain_tx: str = None

@app.post("/classify", response_model=ClassificationResponse)
async def classify_text(request: ClassificationRequest):
    try:
        # Clasificar
        result = classifier.classify_text(request.text)
        
        # Anclar si se solicita
        tx_hash = None
        if request.anchor_to_blockchain:
            record = anchor.anchor_classification(result.to_dict())
            tx_hash = record.transaction_hash
        
        return ClassificationResponse(
            predicted_label=result.predicted_label,
            confidence=result.confidence,
            processing_time_ms=result.processing_time_ms,
            blockchain_tx=tx_hash
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.4 Procesamiento Distribuido con Multiprocessing

```python
from multiprocessing import Pool, cpu_count
from classify_v2 import LegalClassifier, ModelConfig
from tqdm import tqdm

def classify_single(text):
    """Función para clasificar un texto (debe ser top-level para pickling)"""
    classifier = LegalClassifier(ModelConfig())
    return classifier.classify_text(text)

def classify_parallel(texts, n_workers=None):
    """Clasificar textos en paralelo"""
    if n_workers is None:
        n_workers = cpu_count()
    
    print(f"Procesando {len(texts)} textos con {n_workers} workers...")
    
    with Pool(n_workers) as pool:
        results = list(tqdm(
            pool.imap(classify_single, texts),
            total=len(texts)
        ))
    
    return results

# Uso
texts = [...]  # Lista grande de textos
results = classify_parallel(texts, n_workers=4)
```

---

## 4. PERSONALIZACIÓN

### 4.1 Agregar Nuevas Categorías Legales

```python
# En classify_v2.py, modificar:
LEGAL_CATEGORIES = [
    "civil",
    "penal",
    # ... categorías existentes
    "ambiental",  # Nueva categoría
    "ciberseguridad",  # Nueva categoría
    "propiedad_intelectual"  # Nueva categoría
]

# Actualizar keywords en RuleBasedClassifier:
class RuleBasedClassifier(BaseClassifier):
    KEYWORDS = {
        # ... keywords existentes
        "ambiental": [
            "medio ambiente", "contaminación", "recursos naturales",
            "impacto ambiental", "biodiversidad", "cambio climático"
        ],
        "ciberseguridad": [
            "datos personales", "privacidad", "ciberseguridad",
            "protección de datos", "GDPR", "habeas data"
        ]
    }
```

### 4.2 Configuración Personalizada de Blockchain

```python
from anchor_v2 import AnchorConfig, BlockchainNetwork

# Configuración personalizada para Polygon
polygon_config = AnchorConfig(
    network=BlockchainNetwork.POLYGON,
    rpc_url="https://polygon-rpc.com",
    private_key=os.getenv("POLYGON_PRIVATE_KEY"),
    gas_limit=500000,  # Gas más alto para Polygon
    max_retries=5,  # Más reintentos
    retry_delay=3,  # Delay más largo
    timeout=60  # Timeout extendido
)

# Configuración para múltiples redes
class MultiChainAnchor:
    def __init__(self):
        self.anchors = {
            "ethereum": BlockchainAnchor(AnchorConfig(
                network=BlockchainNetwork.MAINNET,
                rpc_url=os.getenv("ETH_RPC")
            )),
            "polygon": BlockchainAnchor(AnchorConfig(
                network=BlockchainNetwork.POLYGON,
                rpc_url=os.getenv("POLYGON_RPC")
            ))
        }
    
    def anchor_multi(self, data):
        """Anclar en múltiples blockchains simultáneamente"""
        records = {}
        for chain, anchor in self.anchors.items():
            try:
                records[chain] = anchor.anchor_classification(data)
            except Exception as e:
                print(f"Error en {chain}: {e}")
        return records
```

### 4.3 Plugins y Extensiones

```python
# Plugin para exportar a diferentes formatos
class ExportPlugin:
    @staticmethod
    def to_pdf(result, output_path):
        """Exportar resultado a PDF"""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(output_path, pagesize=letter)
        c.drawString(100, 750, "IUS-DIGITALIS - Reporte de Clasificación")
        c.drawString(100, 730, f"Categoría: {result.predicted_label}")
        c.drawString(100, 710, f"Confianza: {result.confidence:.2%}")
        c.save()
    
    @staticmethod
    def to_excel(results, output_path):
        """Exportar múltiples resultados a Excel"""
        import pandas as pd
        
        df = pd.DataFrame([r.to_dict() for r in results])
        df.to_excel(output_path, index=False)

# Uso
from classify_v2 import LegalClassifier
classifier = LegalClassifier()
result = classifier.classify_text("...")

ExportPlugin.to_pdf(result, "reporte.pdf")
```

---

## 5. PRODUCCIÓN Y DESPLIEGUE

### 5.1 Despliegue con Docker

**Dockerfile:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo spaCy
RUN python -m spacy download es_core_news_sm

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p data logs models blockchain_data

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:pass@db:5432/ius_digitalis
      - BLOCKCHAIN_NETWORK=polygon
      - BLOCKCHAIN_RPC_URL=${BLOCKCHAIN_RPC_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./models:/app/models
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=ius_digitalis
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    environment:
      - ENVIRONMENT=production
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

### 5.2 Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ius-digitalis
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ius-digitalis
  template:
    metadata:
      labels:
        app: ius-digitalis
    spec:
      containers:
      - name: api
        image: ius-digitalis:2.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ius-digitalis-service
spec:
  selector:
    app: ius-digitalis
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 5.3 Monitoreo y Observabilidad

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Métricas
classifications_total = Counter(
    'classifications_total',
    'Total de clasificaciones realizadas',
    ['category', 'model_type']
)

classification_duration = Histogram(
    'classification_duration_seconds',
    'Duración de clasificaciones'
)

blockchain_anchors = Counter(
    'blockchain_anchors_total',
    'Total de anclajes blockchain',
    ['network', 'status']
)

model_confidence = Gauge(
    'model_confidence',
    'Confianza promedio del modelo'
)

# Uso en clasificador
class MonitoredClassifier(LegalClassifier):
    @classification_duration.time()
    def classify_text(self, text):
        result = super().classify_text(text)
        
        classifications_total.labels(
            category=result.predicted_label,
            model_type=self.config.model_type
        ).inc()
        
        model_confidence.set(result.confidence)
        
        return result

# Iniciar servidor de métricas
if __name__ == "__main__":
    start_http_server(9090)
    print("Métricas disponibles en http://localhost:9090")
```

### 5.4 CI/CD Pipeline

El archivo `python-app-fixed.yml` ya incluye un pipeline completo de CI/CD con:
- Linting y análisis estático
- Tests unitarios multi-versión
- Tests de integración
- Análisis de seguridad
- Build y artifacts
- Reporte final

**Despliegue automático (agregar al workflow):**

```yaml
deploy:
  name: Deploy to Production
  runs-on: ubuntu-latest
  needs: [build]
  if: github.ref == 'refs/heads/main'
  
  steps:
  - name: Deploy to Kubernetes
    uses: azure/k8s-deploy@v1
    with:
      manifests: |
        k8s/deployment.yaml
        k8s/service.yaml
      images: |
        ius-digitalis:${{ github.sha }}
```

---

## 6. TROUBLESHOOTING

### 6.1 Problemas Comunes

#### Error: "Module not found"
```bash
# Solución: Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### Error: "CUDA not available" (GPU)
```bash
# Verificar instalación de PyTorch con CUDA
pip install torch==2.0.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
python -c "import torch; print(torch.cuda.is_available())"
```

#### Error: "Cannot connect to blockchain"
```python
# Usar modo simulación para desarrollo
config = AnchorConfig(network=BlockchainNetwork.SIMULATION)
```

#### Error: "Permission denied" en scripts
```bash
chmod +x setup.sh classify_v2.py anchor_v2.py
```

### 6.2 Debugging

```python
# Activar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Modo verbose en CLI
python classify_v2.py -f documento.txt -v

# Profiling de rendimiento
import cProfile
cProfile.run('classifier.classify_text(text)', 'profile_stats')

# Análisis de profile
import pstats
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### 6.3 Logs y Auditoría

```bash
# Ver logs en tiempo real
tail -f logs/classification.log
tail -f logs/blockchain.log

# Buscar errores
grep -i error logs/*.log

# Analizar performance
grep "processing_time_ms" logs/classification.log | \
  python -c "import sys, json; times = [json.loads(line)['processing_time_ms'] for line in sys.stdin]; print(f'Avg: {sum(times)/len(times):.2f}ms')"
```

---

## CONCLUSIÓN

Esta guía cubre los aspectos esenciales de IUS-DIGITALIS v2.0. Para consultas adicionales:

- **Documentación técnica**: Ver archivos en `/docs`
- **Ejemplos**: Ver notebooks en `/notebooks`
- **Issues**: Reportar en GitHub
- **Contacto**: soporte@ius-digitalis.com

**Próximos pasos recomendados:**
1. Completar instalación y verificar tests
2. Experimentar con clasificación básica
3. Entrenar modelo personalizado con tus datos
4. Configurar blockchain para tu caso de uso
5. Desplegar en producción gradualmente

---

*Documento generado: 2025-11-05*  
*Versión del Sistema: 2.0.0*  
*Licencia: Ver LICENSE file*
