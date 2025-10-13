# RPA SECOP (Starter)

Robot de ejemplo que **simula** la descarga de expedientes creando tres PDFs dummy en `./out`.

## Ejecutar con Docker
```bash
docker build -t rpa-sec .
docker run --rm -v "$PWD/out:/app/out" rpa-sec
```
Los PDFs quedarán en `rpa_secop/out`.

## Ejecutar con Python (sin Docker)
```bash
pip install -r requirements.txt
python -m src.scraper
```
