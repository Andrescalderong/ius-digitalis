#!/usr/bin/env python3
"""
CLASSIFY_V2.PY - Sistema de Clasificación Legal Automatizada
=============================================================

Módulo mejorado para clasificación automática de textos legales usando
técnicas de Machine Learning y NLP.

Mejoras sobre versión anterior:
- Rutas relativas (no hardcodeadas)
- Manejo robusto de errores
- Logging estructurado
- Configuración mediante variables de entorno
- Validación de inputs
- Múltiples backends de clasificación

Autor: Consultoría de Sistemas Legales Automatizados
Fecha: 2025-11-05
Versión: 2.0.0
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('classification.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# CONFIGURACIÓN Y CONSTANTES
# ----------------------------------------------------------------------------

# Detectar directorio del proyecto (relativo al script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent if (SCRIPT_DIR / '..').exists() else SCRIPT_DIR

# Directorios del proyecto
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

# Crear directorios si no existen
for directory in [DATA_DIR, MODELS_DIR, CONFIG_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Categorías legales soportadas
LEGAL_CATEGORIES = [
    "civil",
    "penal",
    "constitucional",
    "administrativo",
    "laboral",
    "mercantil",
    "tributario",
    "internacional",
    "procesal",
    "ambiental"
]

# ----------------------------------------------------------------------------
# CLASES DE DATOS
# ----------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    """Resultado de una clasificación legal"""
    text: str
    predicted_label: str
    confidence: float
    timestamp: str
    method: str
    processing_time_ms: float
    text_hash: str
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convertir a JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


@dataclass
class ModelConfig:
    """Configuración del modelo de clasificación"""
    model_type: str = "sklearn"  # sklearn, transformers, rule-based
    model_path: Optional[Path] = None
    confidence_threshold: float = 0.5
    max_length: int = 512
    batch_size: int = 32
    use_gpu: bool = False

# ----------------------------------------------------------------------------
# EXCEPCIONES PERSONALIZADAS
# ----------------------------------------------------------------------------

class ClassificationError(Exception):
    """Error base para clasificación"""
    pass

class ModelNotFoundError(ClassificationError):
    """Modelo no encontrado"""
    pass

class InvalidInputError(ClassificationError):
    """Input inválido"""
    pass

# ----------------------------------------------------------------------------
# CLASIFICADORES
# ----------------------------------------------------------------------------

class BaseClassifier:
    """Clase base abstracta para clasificadores"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        logger.info(f"Inicializando clasificador: {self.__class__.__name__}")
    
    def classify(self, text: str) -> Tuple[str, float]:
        """
        Clasificar texto
        
        Args:
            text: Texto a clasificar
            
        Returns:
            Tupla (label, confidence)
        """
        raise NotImplementedError("Subclases deben implementar classify()")
    
    def validate_input(self, text: str) -> None:
        """Validar input de texto"""
        if not text or not isinstance(text, str):
            raise InvalidInputError("El texto debe ser una cadena no vacía")
        
        if len(text.strip()) == 0:
            raise InvalidInputError("El texto no puede estar vacío")
        
        if len(text) > 100000:
            logger.warning(f"Texto muy largo: {len(text)} caracteres")


class RuleBasedClassifier(BaseClassifier):
    """Clasificador basado en reglas y palabras clave"""
    
    KEYWORDS = {
        "civil": [
            "contrato", "propiedad", "herencia", "matrimonio", "divorcio",
            "obligaciones", "responsabilidad civil", "daños", "familia"
        ],
        "penal": [
            "delito", "pena", "prisión", "culpabilidad", "homicidio",
            "robo", "fraude", "condena", "sentencia", "código penal"
        ],
        "constitucional": [
            "constitución", "derechos fundamentales", "amparo", "garantías",
            "suprema corte", "inconstitucionalidad", "carta magna"
        ],
        "administrativo": [
            "administración pública", "funcionario", "procedimiento administrativo",
            "acto administrativo", "recurso", "permiso", "licencia"
        ],
        "laboral": [
            "trabajo", "empleado", "salario", "despido", "sindic", "jornada",
            "contrato laboral", "prestaciones", "seguridad social"
        ],
        "mercantil": [
            "comercio", "sociedad mercantil", "empresa", "compraventa",
            "títulos", "quiebra", "concurso mercantil", "comerciante"
        ]
    }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """Clasificar usando palabras clave"""
        self.validate_input(text)
        
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        if not scores or max(scores.values()) == 0:
            return "desconocido", 0.0
        
        best_category = max(scores, key=scores.get)
        total_matches = sum(scores.values())
        confidence = scores[best_category] / (total_matches + 1)
        
        return best_category, min(confidence, 1.0)


class MLClassifier(BaseClassifier):
    """Clasificador basado en Machine Learning"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.model = None
        self.vectorizer = None
        self._load_model()
    
    def _load_model(self):
        """Cargar modelo entrenado"""
        if self.config.model_path is None:
            logger.warning("No se especificó ruta de modelo. Usando clasificador de respaldo")
            return
        
        model_file = Path(self.config.model_path)
        
        if not model_file.exists():
            logger.warning(f"Modelo no encontrado en {model_file}")
            return
        
        try:
            import joblib
            self.model = joblib.load(model_file)
            logger.info(f"Modelo cargado desde {model_file}")
            
            # Intentar cargar vectorizer si existe
            vectorizer_file = model_file.parent / "vectorizer.pkl"
            if vectorizer_file.exists():
                self.vectorizer = joblib.load(vectorizer_file)
                logger.info("Vectorizer cargado")
                
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            self.model = None
    
    def classify(self, text: str) -> Tuple[str, float]:
        """Clasificar usando modelo ML"""
        self.validate_input(text)
        
        if self.model is None or self.vectorizer is None:
            logger.warning("Modelo no disponible, usando clasificador de respaldo")
            fallback = RuleBasedClassifier(self.config)
            return fallback.classify(text)
        
        try:
            # Vectorizar texto
            X = self.vectorizer.transform([text])
            
            # Predecir
            prediction = self.model.predict(X)[0]
            
            # Obtener probabilidades si están disponibles
            if hasattr(self.model, 'predict_proba'):
                probas = self.model.predict_proba(X)[0]
                confidence = float(max(probas))
            else:
                confidence = 0.8  # Default si no hay probabilidades
            
            return prediction, confidence
            
        except Exception as e:
            logger.error(f"Error en clasificación ML: {e}")
            fallback = RuleBasedClassifier(self.config)
            return fallback.classify(text)


class TransformerClassifier(BaseClassifier):
    """Clasificador basado en modelos Transformers (BERT, etc.)"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Cargar modelo Transformer"""
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            import torch
            
            model_name = "dccuchile/bert-base-spanish-wwm-cased"
            
            if self.config.model_path and Path(self.config.model_path).exists():
                model_path = str(self.config.model_path)
            else:
                model_path = model_name
                logger.info(f"Usando modelo pre-entrenado: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            if self.config.use_gpu and torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("Usando GPU para inferencia")
            
            logger.info("Modelo Transformer cargado correctamente")
            
        except ImportError:
            logger.warning("Transformers no disponible. Instala con: pip install transformers torch")
            self.model = None
        except Exception as e:
            logger.error(f"Error cargando modelo Transformer: {e}")
            self.model = None
    
    def classify(self, text: str) -> Tuple[str, float]:
        """Clasificar usando Transformer"""
        self.validate_input(text)
        
        if self.model is None:
            logger.warning("Modelo Transformer no disponible, usando respaldo")
            fallback = RuleBasedClassifier(self.config)
            return fallback.classify(text)
        
        try:
            import torch
            
            # Tokenizar
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=self.config.max_length,
                truncation=True,
                padding=True
            )
            
            if self.config.use_gpu and torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Inferencia
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probas = torch.softmax(logits, dim=-1)
            
            # Obtener predicción
            predicted_class = torch.argmax(probas, dim=-1).item()
            confidence = float(probas[0][predicted_class])
            
            # Mapear a categoría
            label = LEGAL_CATEGORIES[predicted_class] if predicted_class < len(LEGAL_CATEGORIES) else "desconocido"
            
            return label, confidence
            
        except Exception as e:
            logger.error(f"Error en clasificación Transformer: {e}")
            fallback = RuleBasedClassifier(self.config)
            return fallback.classify(text)

# ----------------------------------------------------------------------------
# CLASE PRINCIPAL
# ----------------------------------------------------------------------------

class LegalClassifier:
    """Sistema principal de clasificación legal"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Inicializar clasificador
        
        Args:
            config: Configuración del modelo
        """
        self.config = config or ModelConfig()
        self.classifier = self._initialize_classifier()
        logger.info("LegalClassifier inicializado correctamente")
    
    def _initialize_classifier(self) -> BaseClassifier:
        """Inicializar el clasificador apropiado"""
        model_type = self.config.model_type.lower()
        
        classifiers = {
            "rule-based": RuleBasedClassifier,
            "sklearn": MLClassifier,
            "ml": MLClassifier,
            "transformers": TransformerClassifier,
            "bert": TransformerClassifier
        }
        
        classifier_class = classifiers.get(model_type, RuleBasedClassifier)
        
        try:
            return classifier_class(self.config)
        except Exception as e:
            logger.error(f"Error inicializando clasificador {model_type}: {e}")
            logger.info("Usando clasificador de respaldo basado en reglas")
            return RuleBasedClassifier(self.config)
    
    def classify_text(self, text: str) -> ClassificationResult:
        """
        Clasificar un texto legal
        
        Args:
            text: Texto a clasificar
            
        Returns:
            ClassificationResult con la predicción
        """
        start_time = datetime.now()
        
        try:
            # Clasificar
            label, confidence = self.classifier.classify(text)
            
            # Calcular hash del texto
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Crear resultado
            result = ClassificationResult(
                text=text[:500],  # Truncar texto largo para output
                predicted_label=label,
                confidence=confidence,
                timestamp=datetime.now().isoformat(),
                method=self.config.model_type,
                processing_time_ms=processing_time,
                text_hash=text_hash
            )
            
            logger.info(f"Clasificación exitosa: {label} (confianza: {confidence:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en clasificación: {e}")
            raise ClassificationError(f"Error clasificando texto: {e}")
    
    def classify_batch(self, texts: List[str]) -> List[ClassificationResult]:
        """
        Clasificar múltiples textos
        
        Args:
            texts: Lista de textos a clasificar
            
        Returns:
            Lista de ClassificationResult
        """
        results = []
        
        logger.info(f"Clasificando lote de {len(texts)} textos...")
        
        for i, text in enumerate(texts):
            try:
                result = self.classify_text(text)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Progreso: {i + 1}/{len(texts)}")
                    
            except Exception as e:
                logger.error(f"Error clasificando texto {i}: {e}")
                continue
        
        logger.info(f"Lote completado: {len(results)}/{len(texts)} exitosos")
        
        return results
    
    def save_results(self, results: Union[ClassificationResult, List[ClassificationResult]], 
                    output_path: Optional[Path] = None) -> Path:
        """
        Guardar resultados en archivo JSON
        
        Args:
            results: Resultado(s) a guardar
            output_path: Ruta de salida (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = DATA_DIR / "processed" / f"classification_results_{timestamp}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir a lista si es un solo resultado
        if isinstance(results, ClassificationResult):
            results = [results]
        
        # Convertir a diccionarios
        data = [r.to_dict() for r in results]
        
        # Guardar
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados guardados en: {output_path}")
        
        return output_path

# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    """Función principal para uso desde CLI"""
    parser = argparse.ArgumentParser(
        description="Sistema de Clasificación Legal Automatizada - IUS-DIGITALIS v2.0"
    )
    
    parser.add_argument(
        "text",
        nargs="?",
        help="Texto a clasificar"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=Path,
        help="Archivo de texto a clasificar"
    )
    
    parser.add_argument(
        "-m", "--model-type",
        choices=["rule-based", "sklearn", "transformers"],
        default="rule-based",
        help="Tipo de modelo a usar"
    )
    
    parser.add_argument(
        "--model-path",
        type=Path,
        help="Ruta al modelo entrenado"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Archivo de salida para resultados"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Output detallado"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Obtener texto
    if args.file:
        if not args.file.exists():
            logger.error(f"Archivo no encontrado: {args.file}")
            sys.exit(1)
        
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)
    
    # Configurar modelo
    config = ModelConfig(
        model_type=args.model_type,
        model_path=args.model_path
    )
    
    # Clasificar
    try:
        classifier = LegalClassifier(config)
        result = classifier.classify_text(text)
        
        # Mostrar resultado
        print("\n" + "=" * 70)
        print("RESULTADO DE CLASIFICACIÓN")
        print("=" * 70)
        print(f"Categoría: {result.predicted_label}")
        print(f"Confianza: {result.confidence:.2%}")
        print(f"Método: {result.method}")
        print(f"Tiempo: {result.processing_time_ms:.2f}ms")
        print("=" * 70)
        
        # Guardar si se especificó
        if args.output:
            classifier.save_results(result, args.output)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
