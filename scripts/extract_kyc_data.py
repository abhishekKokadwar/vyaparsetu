import os
import subprocess
import json

kyc_dir = 'udyam_digital_data/kyc_documents'
files = sorted(os.listdir(kyc_dir))

results = {}

for f in files:
    if not f.endswith('.png'):
        continue
    filepath = os.path.join(kyc_dir, f)
    cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'scripts/ocr_test.ps1', '-ImagePath', filepath]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        text = proc.stdout.strip()
        results[f] = text
        print(f"Done {f}: {len(text)} chars")
    except Exception as e:
        print(f"Error {f}: {e}")

with open('udyam_digital_data/kyc_extracted.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, indent=2)

print("Saved all extracted OCR data to udyam_digital_data/kyc_extracted.json")

