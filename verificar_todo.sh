#!/usr/bin/env bash
set -Eeuo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE"

ANCHORS="blockchain_registry/outputs/anchors.json"
PDFDIR="rpa_secop/data/raw"

if [[ ! -f "$ANCHORS" ]]; then
  echo "❌ No existe $ANCHORS"; exit 1
fi

ok=0; fail=0

for f in "$PDFDIR"/EXP-2025-00{1,2,3}.pdf; do
  file="$(basename "$f")"
  actual="$(shasum -a 256 "$f" | awk '{print $1}')"
  expected="$(python3 - <<'PY'
import json,sys,os
anchors="blockchain_registry/outputs/anchors.json"
file=os.environ.get("FILE")
with open(anchors,"r",encoding="utf-8") as fh:
    data=json.load(fh)
for a in data.get("anchors",[]):
    if a.get("expediente_id")==file:
        print(a.get("sha256","")); break
PY
)"
  export FILE="$file"  # para el bloque Python anterior
  echo
  echo "📄 $file"
  echo "   ACTUAL  : $actual"
  echo "   ESPERADO: $expected"
  if [[ -n "$expected" && "$actual" == "$expected" ]]; then
    echo "   ✅ Coinciden"
    ((ok++))
  else
    echo "   ❌ NO coincide"
    ((fail++))
  fi
done

echo
echo "Resumen: ✅ $ok  ❌ $fail"
[[ $fail -eq 0 ]]
