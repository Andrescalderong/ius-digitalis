# Manual de Instalación y Ejecución — IUS-Digitalis (Starter)

Este paquete es un esqueleto funcional mínimo para crear el repositorio `ius-digitalis`.

## Requisitos
- Git, GitHub Desktop (opcional)
- Docker (para RPA)
- Python 3.9+ y pip
- Node.js 18+ (para blockchain, opcional en este starter)

## Estructura
- `rpa_secop/`: robot de ingesta de ejemplo (descarga simulada)
- `ia_classifier/`: notebook demostrativo
- `blockchain_registry/`: contrato Solidity mínimo y cliente Python
- `infra/`: diagrama de arquitectura (Mermaid) y README

## Pasos rápidos
1) `cd rpa_secop && docker build -t rpa-sec . && docker run --rm -v "$PWD/out:/app/out" rpa-sec`
2) Abra el notebook `ia_classifier/notebook_clasificador_trl6.ipynb` en Jupyter/Colab.
3) Para blockchain (local), revise `blockchain_registry/README.md`.
