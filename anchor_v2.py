#!/usr/bin/env python3
"""
ANCHOR_V2.PY - Sistema de Anclaje Blockchain para Documentos Legales
=====================================================================

Módulo mejorado para anclaje inmutable de clasificaciones legales en
blockchain, garantizando trazabilidad y no-repudio.

Mejoras sobre versión anterior:
- Arquitectura modular con múltiples backends
- Validación exhaustiva de datos
- Manejo robusto de errores de red
- Logging estructurado
- Retry con backoff exponencial
- Simulación para desarrollo

Autor: Consultoría de Sistemas Legales Automatizados
Fecha: 2025-11-05
Versión: 2.0.0
"""

import os
import sys
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
import secrets

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('blockchain.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# CONFIGURACIÓN Y CONSTANTES
# ----------------------------------------------------------------------------

# Detectar directorio del proyecto
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent if (SCRIPT_DIR / '..').exists() else SCRIPT_DIR

# Directorios del proyecto
DATA_DIR = PROJECT_ROOT / "data"
BLOCKCHAIN_DIR = PROJECT_ROOT / "blockchain_data"
CONFIG_DIR = PROJECT_ROOT / "config"

# Crear directorios si no existen
for directory in [DATA_DIR, BLOCKCHAIN_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# ENUMS Y TIPOS
# ----------------------------------------------------------------------------

class BlockchainNetwork(Enum):
    """Redes blockchain soportadas"""
    SIMULATION = "simulation"  # Simulación local
    GANACHE = "ganache"  # Blockchain local de desarrollo
    SEPOLIA = "sepolia"  # Testnet Ethereum
    MAINNET = "mainnet"  # Mainnet Ethereum
    POLYGON = "polygon"  # Polygon/Matic
    BSC = "bsc"  # Binance Smart Chain

class TransactionStatus(Enum):
    """Estados de una transacción blockchain"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    UNKNOWN = "unknown"

# ----------------------------------------------------------------------------
# CLASES DE DATOS
# ----------------------------------------------------------------------------

@dataclass
class BlockchainRecord:
    """Registro inmutable en blockchain"""
    document_hash: str
    classification_data: Dict[str, Any]
    timestamp: str
    block_number: Optional[int] = None
    transaction_hash: Optional[str] = None
    network: str = "simulation"
    merkle_root: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convertir a JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def verify_hash(self) -> bool:
        """Verificar integridad del hash"""
        data_str = json.dumps(self.classification_data, sort_keys=True)
        calculated_hash = hashlib.sha256(data_str.encode()).hexdigest()
        return calculated_hash == self.document_hash


@dataclass
class AnchorConfig:
    """Configuración para anclaje blockchain"""
    network: BlockchainNetwork = BlockchainNetwork.SIMULATION
    rpc_url: Optional[str] = None
    private_key: Optional[str] = None
    contract_address: Optional[str] = None
    gas_limit: int = 300000
    max_retries: int = 3
    retry_delay: int = 2
    timeout: int = 30

# ----------------------------------------------------------------------------
# EXCEPCIONES PERSONALIZADAS
# ----------------------------------------------------------------------------

class BlockchainError(Exception):
    """Error base para operaciones blockchain"""
    pass

class NetworkError(BlockchainError):
    """Error de conexión a red blockchain"""
    pass

class ValidationError(BlockchainError):
    """Error de validación de datos"""
    pass

class TransactionError(BlockchainError):
    """Error en transacción blockchain"""
    pass

# ----------------------------------------------------------------------------
# BACKENDS DE BLOCKCHAIN
# ----------------------------------------------------------------------------

class BaseBlockchainBackend:
    """Clase base abstracta para backends de blockchain"""
    
    def __init__(self, config: AnchorConfig):
        self.config = config
        logger.info(f"Inicializando backend: {self.__class__.__name__}")
    
    def anchor(self, data: Dict) -> BlockchainRecord:
        """
        Anclar datos en blockchain
        
        Args:
            data: Datos a anclar
            
        Returns:
            BlockchainRecord con información del anclaje
        """
        raise NotImplementedError("Subclases deben implementar anchor()")
    
    def verify(self, record: BlockchainRecord) -> bool:
        """
        Verificar un registro en blockchain
        
        Args:
            record: Registro a verificar
            
        Returns:
            True si el registro es válido
        """
        raise NotImplementedError("Subclases deben implementar verify()")
    
    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        """
        Obtener estado de una transacción
        
        Args:
            tx_hash: Hash de la transacción
            
        Returns:
            TransactionStatus
        """
        raise NotImplementedError("Subclases deben implementar get_transaction_status()")


class SimulationBackend(BaseBlockchainBackend):
    """Backend de simulación para desarrollo y testing"""
    
    def __init__(self, config: AnchorConfig):
        super().__init__(config)
        self.chain: List[BlockchainRecord] = []
        self.block_number = 0
        logger.info("Modo simulación activado - Sin costos de gas")
    
    def anchor(self, data: Dict) -> BlockchainRecord:
        """Anclar en simulación (blockchain local en memoria)"""
        # Generar hash del documento
        data_str = json.dumps(data, sort_keys=True)
        document_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        # Generar transaction hash simulado
        tx_hash = "0xsim_" + secrets.token_hex(32)
        
        # Incrementar número de bloque
        self.block_number += 1
        
        # Calcular Merkle root (simulado)
        merkle_root = self._calculate_merkle_root([document_hash])
        
        # Crear registro
        record = BlockchainRecord(
            document_hash=document_hash,
            classification_data=data,
            timestamp=datetime.now().isoformat(),
            block_number=self.block_number,
            transaction_hash=tx_hash,
            network=self.config.network.value,
            merkle_root=merkle_root,
            metadata={
                "simulation": True,
                "chain_length": len(self.chain) + 1
            }
        )
        
        # Agregar a la cadena
        self.chain.append(record)
        
        logger.info(f"Anclaje simulado exitoso - Bloque: {self.block_number}, TX: {tx_hash}")
        
        return record
    
    def verify(self, record: BlockchainRecord) -> bool:
        """Verificar registro en simulación"""
        # Verificar hash
        if not record.verify_hash():
            logger.warning("Hash del documento no coincide")
            return False
        
        # Buscar en la cadena
        for chain_record in self.chain:
            if chain_record.transaction_hash == record.transaction_hash:
                logger.info(f"Registro verificado en bloque {chain_record.block_number}")
                return True
        
        logger.warning("Registro no encontrado en la cadena simulada")
        return False
    
    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        """Obtener estado de transacción simulada"""
        for record in self.chain:
            if record.transaction_hash == tx_hash:
                return TransactionStatus.CONFIRMED
        
        return TransactionStatus.UNKNOWN
    
    def _calculate_merkle_root(self, hashes: List[str]) -> str:
        """Calcular Merkle root de una lista de hashes"""
        if not hashes:
            return hashlib.sha256(b'').hexdigest()
        
        if len(hashes) == 1:
            return hashes[0]
        
        # Asegurar número par de hashes
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
        
        # Calcular nivel superior
        next_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i + 1]
            next_hash = hashlib.sha256(combined.encode()).hexdigest()
            next_level.append(next_hash)
        
        return self._calculate_merkle_root(next_level)
    
    def export_chain(self, output_path: Optional[Path] = None) -> Path:
        """Exportar cadena simulada a archivo"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = BLOCKCHAIN_DIR / f"simulated_chain_{timestamp}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = [record.to_dict() for record in self.chain]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cadena simulada exportada a: {output_path}")
        
        return output_path


class EthereumBackend(BaseBlockchainBackend):
    """Backend para Ethereum y redes compatibles"""
    
    def __init__(self, config: AnchorConfig):
        super().__init__(config)
        self.web3 = None
        self.account = None
        self.contract = None
        self._initialize_web3()
    
    def _initialize_web3(self):
        """Inicializar conexión Web3"""
        try:
            from web3 import Web3
            from eth_account import Account
            
            if not self.config.rpc_url:
                raise ValueError("RPC URL requerido para conexión Ethereum")
            
            # Conectar a la red
            self.web3 = Web3(Web3.HTTPProvider(
                self.config.rpc_url,
                request_kwargs={'timeout': self.config.timeout}
            ))
            
            if not self.web3.is_connected():
                raise NetworkError("No se pudo conectar a la red Ethereum")
            
            logger.info(f"Conectado a red Ethereum - Network ID: {self.web3.eth.chain_id}")
            
            # Configurar cuenta si hay private key
            if self.config.private_key:
                self.account = Account.from_key(self.config.private_key)
                logger.info(f"Cuenta configurada: {self.account.address}")
            
        except ImportError:
            logger.error("web3.py no disponible. Instala con: pip install web3")
            raise BlockchainError("web3.py no instalado")
        except Exception as e:
            logger.error(f"Error inicializando Web3: {e}")
            raise NetworkError(f"Error de conexión: {e}")
    
    def anchor(self, data: Dict) -> BlockchainRecord:
        """Anclar en blockchain Ethereum"""
        if not self.web3 or not self.account:
            raise BlockchainError("Backend Ethereum no inicializado correctamente")
        
        # Generar hash del documento
        data_str = json.dumps(data, sort_keys=True)
        document_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        try:
            # Preparar datos para transacción
            hash_bytes = bytes.fromhex(document_hash)
            
            # Si hay contrato, interactuar con él
            if self.contract:
                tx = self._send_contract_transaction(hash_bytes)
            else:
                # Enviar transacción simple con hash en data
                tx = self._send_simple_transaction(hash_bytes)
            
            # Crear registro
            record = BlockchainRecord(
                document_hash=document_hash,
                classification_data=data,
                timestamp=datetime.now().isoformat(),
                block_number=tx.get('blockNumber'),
                transaction_hash=tx.get('transactionHash').hex(),
                network=self.config.network.value,
                metadata={
                    "gas_used": tx.get('gasUsed'),
                    "block_hash": tx.get('blockHash').hex()
                }
            )
            
            logger.info(f"Anclaje exitoso en {self.config.network.value} - TX: {record.transaction_hash}")
            
            return record
            
        except Exception as e:
            logger.error(f"Error en anclaje Ethereum: {e}")
            raise TransactionError(f"Error en transacción: {e}")
    
    def _send_simple_transaction(self, data: bytes) -> Dict:
        """Enviar transacción simple"""
        nonce = self.web3.eth.get_transaction_count(self.account.address)
        
        tx = {
            'nonce': nonce,
            'to': self.account.address,  # Enviar a sí mismo
            'value': 0,
            'gas': self.config.gas_limit,
            'gasPrice': self.web3.eth.gas_price,
            'data': data,
            'chainId': self.web3.eth.chain_id
        }
        
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Esperar confirmación
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=self.config.timeout)
        
        return receipt
    
    def _send_contract_transaction(self, data: bytes) -> Dict:
        """Enviar transacción a contrato inteligente"""
        # Implementación específica de contrato
        # Depende del ABI y funciones del contrato
        pass
    
    def verify(self, record: BlockchainRecord) -> bool:
        """Verificar registro en blockchain Ethereum"""
        if not self.web3:
            raise BlockchainError("Backend Ethereum no inicializado")
        
        try:
            # Verificar hash local
            if not record.verify_hash():
                return False
            
            # Obtener transacción
            tx = self.web3.eth.get_transaction(record.transaction_hash)
            
            if not tx:
                logger.warning(f"Transacción no encontrada: {record.transaction_hash}")
                return False
            
            # Verificar datos
            tx_data = tx.get('input', b'').hex()
            expected_data = record.document_hash
            
            if expected_data in tx_data:
                logger.info("Registro verificado en blockchain")
                return True
            
            logger.warning("Datos no coinciden en blockchain")
            return False
            
        except Exception as e:
            logger.error(f"Error verificando registro: {e}")
            return False
    
    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        """Obtener estado de transacción"""
        if not self.web3:
            return TransactionStatus.UNKNOWN
        
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            if receipt:
                if receipt.get('status') == 1:
                    return TransactionStatus.CONFIRMED
                else:
                    return TransactionStatus.FAILED
            
            # Si no hay receipt, puede estar pending
            tx = self.web3.eth.get_transaction(tx_hash)
            if tx:
                return TransactionStatus.PENDING
            
            return TransactionStatus.UNKNOWN
            
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return TransactionStatus.UNKNOWN

# ----------------------------------------------------------------------------
# CLASE PRINCIPAL
# ----------------------------------------------------------------------------

class BlockchainAnchor:
    """Sistema principal de anclaje blockchain"""
    
    def __init__(self, config: Optional[AnchorConfig] = None):
        """
        Inicializar sistema de anclaje
        
        Args:
            config: Configuración de anclaje
        """
        self.config = config or AnchorConfig()
        self.backend = self._initialize_backend()
        logger.info("BlockchainAnchor inicializado correctamente")
    
    def _initialize_backend(self) -> BaseBlockchainBackend:
        """Inicializar backend apropiado"""
        backends = {
            BlockchainNetwork.SIMULATION: SimulationBackend,
            BlockchainNetwork.GANACHE: EthereumBackend,
            BlockchainNetwork.SEPOLIA: EthereumBackend,
            BlockchainNetwork.MAINNET: EthereumBackend,
            BlockchainNetwork.POLYGON: EthereumBackend,
            BlockchainNetwork.BSC: EthereumBackend
        }
        
        backend_class = backends.get(self.config.network, SimulationBackend)
        
        try:
            return backend_class(self.config)
        except Exception as e:
            logger.warning(f"Error inicializando backend {self.config.network.value}: {e}")
            logger.info("Fallback a modo simulación")
            self.config.network = BlockchainNetwork.SIMULATION
            return SimulationBackend(self.config)
    
    def anchor_classification(self, classification_data: Dict) -> BlockchainRecord:
        """
        Anclar resultado de clasificación en blockchain
        
        Args:
            classification_data: Datos de clasificación a anclar
            
        Returns:
            BlockchainRecord con información del anclaje
        """
        try:
            # Validar datos
            self._validate_data(classification_data)
            
            # Anclar con retry
            record = self._anchor_with_retry(classification_data)
            
            # Guardar registro localmente
            self._save_record(record)
            
            return record
            
        except Exception as e:
            logger.error(f"Error en anclaje: {e}")
            raise BlockchainError(f"Error anclando clasificación: {e}")
    
    def _validate_data(self, data: Dict) -> None:
        """Validar datos antes de anclar"""
        required_fields = ['text', 'predicted_label', 'confidence']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Campo requerido faltante: {field}")
        
        if not isinstance(data['confidence'], (int, float)):
            raise ValidationError("Confidence debe ser numérico")
        
        if not 0 <= data['confidence'] <= 1:
            raise ValidationError("Confidence debe estar entre 0 y 1")
    
    def _anchor_with_retry(self, data: Dict) -> BlockchainRecord:
        """Anclar con reintento automático"""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Intento de anclaje {attempt + 1}/{self.config.max_retries}")
                
                record = self.backend.anchor(data)
                
                logger.info("Anclaje exitoso")
                return record
                
            except Exception as e:
                last_error = e
                logger.warning(f"Intento {attempt + 1} fallido: {e}")
                
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Backoff exponencial
                    logger.info(f"Reintentando en {delay} segundos...")
                    time.sleep(delay)
        
        raise TransactionError(f"Falló después de {self.config.max_retries} intentos: {last_error}")
    
    def _save_record(self, record: BlockchainRecord) -> None:
        """Guardar registro localmente"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"anchor_record_{timestamp}.json"
        filepath = BLOCKCHAIN_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Registro guardado localmente: {filepath}")
    
    def verify_record(self, record: BlockchainRecord) -> bool:
        """
        Verificar un registro en blockchain
        
        Args:
            record: Registro a verificar
            
        Returns:
            True si el registro es válido
        """
        try:
            return self.backend.verify(record)
        except Exception as e:
            logger.error(f"Error verificando registro: {e}")
            return False
    
    def get_status(self, tx_hash: str) -> TransactionStatus:
        """
        Obtener estado de una transacción
        
        Args:
            tx_hash: Hash de la transacción
            
        Returns:
            TransactionStatus
        """
        try:
            return self.backend.get_transaction_status(tx_hash)
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return TransactionStatus.UNKNOWN


# ----------------------------------------------------------------------------
# UTILIDADES
# ----------------------------------------------------------------------------

def load_config_from_env() -> AnchorConfig:
    """Cargar configuración desde variables de entorno"""
    network_map = {
        'simulation': BlockchainNetwork.SIMULATION,
        'ganache': BlockchainNetwork.GANACHE,
        'sepolia': BlockchainNetwork.SEPOLIA,
        'mainnet': BlockchainNetwork.MAINNET,
        'polygon': BlockchainNetwork.POLYGON,
        'bsc': BlockchainNetwork.BSC
    }
    
    network = os.getenv('BLOCKCHAIN_NETWORK', 'simulation').lower()
    
    config = AnchorConfig(
        network=network_map.get(network, BlockchainNetwork.SIMULATION),
        rpc_url=os.getenv('BLOCKCHAIN_RPC_URL'),
        private_key=os.getenv('BLOCKCHAIN_PRIVATE_KEY'),
        contract_address=os.getenv('BLOCKCHAIN_CONTRACT_ADDRESS'),
        gas_limit=int(os.getenv('BLOCKCHAIN_GAS_LIMIT', '300000')),
        max_retries=int(os.getenv('BLOCKCHAIN_MAX_RETRIES', '3')),
        retry_delay=int(os.getenv('BLOCKCHAIN_RETRY_DELAY', '2')),
        timeout=int(os.getenv('BLOCKCHAIN_TIMEOUT', '30'))
    )
    
    return config


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    """Función principal para uso desde CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sistema de Anclaje Blockchain - IUS-DIGITALIS v2.0"
    )
    
    parser.add_argument(
        "file",
        type=Path,
        help="Archivo JSON con datos de clasificación"
    )
    
    parser.add_argument(
        "-n", "--network",
        choices=[n.value for n in BlockchainNetwork],
        default="simulation",
        help="Red blockchain a usar"
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
    
    # Validar archivo
    if not args.file.exists():
        logger.error(f"Archivo no encontrado: {args.file}")
        sys.exit(1)
    
    # Cargar datos
    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Configurar anclaje
    config = load_config_from_env()
    config.network = BlockchainNetwork(args.network)
    
    # Anclar
    try:
        anchor = BlockchainAnchor(config)
        record = anchor.anchor_classification(data)
        
        print("\n" + "=" * 70)
        print("ANCLAJE EXITOSO")
        print("=" * 70)
        print(f"Network: {record.network}")
        print(f"Block: {record.block_number}")
        print(f"TX Hash: {record.transaction_hash}")
        print(f"Document Hash: {record.document_hash}")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
