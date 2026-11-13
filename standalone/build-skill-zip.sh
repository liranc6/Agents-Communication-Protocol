#!/bin/bash
# Builds a zip of the COP skill for upload to claude.ai (Settings > Customize > Skills).
# Usage: standalone/build-skill-zip.sh [output.zip]   (default: dist/cop.zip)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist/cop.zip}"
mkdir -p "$(dirname "$OUT")"
OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
rm -f "$OUT"
python3 - "$ROOT/skills" "$OUT" <<'PY'
import os, sys, zipfile
base, out = sys.argv[1:3]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for d, _, files in os.walk(os.path.join(base, "cop")):
        for f in sorted(files):
            if f == ".cop-managed":
                continue
            p = os.path.join(d, f)
            z.write(p, os.path.relpath(p, base))
PY
echo "wrote $OUT"
echo "Upload it in Claude: Settings > Customize > Skills."
