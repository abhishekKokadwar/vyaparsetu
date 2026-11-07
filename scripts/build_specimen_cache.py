"""Build app/specimen_ocr.json: SHA-256 of each hackathon specimen image -> transcription from the local Windows OCR.

The live site serves these known specimens from this file (reported as backend "specimen") so a demo does not depend
on a cloud OCR quota. Any image whose hash is not listed still goes through live OCR.
Run on Windows from the repo root:  .venv\\Scripts\\python scripts\\build_specimen_cache.py
"""
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "udyam_digital_data" / "kyc_documents"
PS1 = ROOT / "scripts" / "ocr_test.ps1"
OUT = ROOT / "app" / "specimen_ocr.json"

cache = {}
for img in sorted(DOCS.glob("*.png")):
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(PS1), "-ImagePath", str(img)],
                         capture_output=True, text=True, timeout=30)
    text = res.stdout.strip()
    if not text:
        print("EMPTY", img.name)
        continue
    cache[hashlib.sha256(img.read_bytes()).hexdigest()] = text
    print("ok", img.name, len(text))

OUT.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
print(f"wrote {len(cache)} specimens to {OUT}")
