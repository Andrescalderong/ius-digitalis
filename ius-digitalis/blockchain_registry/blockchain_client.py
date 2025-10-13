# Cliente de ejemplo (no requiere Web3 para este placeholder)
import hashlib, json, pathlib

def sha256_bytes(path):
    data = pathlib.Path(path).read_bytes()
    return hashlib.sha256(data).hexdigest()

if __name__ == '__main__':
    print('Calcule el hash de un PDF y guárdelo para anclarlo on-chain más adelante.')
