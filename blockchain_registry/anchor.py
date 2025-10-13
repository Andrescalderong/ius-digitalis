from pathlib import Path
import pandas as pd
import hashlib, time, json

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "ia_classifier" / "outputs" / "classifications.csv"
OUT = Path(__file__).resolve().parent / "outputs" / "anchors.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def fake_tx_id(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:66]

def main():
    if not CSV.exists():
        raise SystemExit(f"No existe {CSV}. Ejecuta primero el clasificador.")
    df = pd.read_csv(CSV)
    anchors = []
    for _, r in df.iterrows():
        payload = f"{r['expediente_id']}|{r['sha256']}|{int(time.time())}"
        txid = fake_tx_id(payload)
        anchors.append({
            "expediente_id": r["expediente_id"],
            "sha256": r["sha256"],
            "categoria": r["categoria"],
            "tx_id": f"0x{txid}",
            "network": "polygon-testnet (simulado)",
            "status": "CONFIRMED"
        })
        print(f"[BC] {r['expediente_id']} -> tx {txid[:12]}... CONFIRMED")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"anchors": anchors}, f, ensure_ascii=False, indent=2)
    print(f"\nAnclas escritas en: {OUT}")

if __name__ == "__main__":
    main()
