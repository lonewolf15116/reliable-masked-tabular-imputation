#!/usr/bin/env python3
"""Capture a reproducible, committable S003 verify-only receipt.

Run from repository root:
    .venv\\Scripts\\python.exe scripts/s003_verify_receipt.py
This invokes S003 --mode verify. It never regenerates or overwrites S003.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT=Path("evidence/S003_VERIFY_RECEIPT.json")
INPUTS=[
 "artifacts/source/adult_source_audit.json",
 "artifacts/splits/adult_split_manifest.json",
 "artifacts/stats/adult_train_feature_stats.json",
 "artifacts/eligible_cells/adult_feature_eligibility.json",
 "scripts/s003_eligible_features.py",
]
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    result=subprocess.run([sys.executable,"scripts/s003_eligible_features.py","--mode","verify"],
                          capture_output=True,text=True,check=False)
    if result.returncode!=0 or "VERIFIED S003 feature-eligibility artifact" not in result.stdout:
        print(result.stdout+result.stderr)
        raise SystemExit("S003 verification FAILED; no receipt produced")
    record={"procedure":"S003 verify-only",
            "command":"python scripts/s003_eligible_features.py --mode verify",
            "exit_code":result.returncode,"stdout":result.stdout,
            "sha256_by_file":{p:sha(p) for p in INPUTS},
            "s003_not_regenerated":True,
            "source_bytes_not_committed":True}
    payload=(json.dumps(record,sort_keys=True,indent=2)+"\n").encode("utf-8")
    if OUT.exists() and OUT.read_bytes()!=payload:
        raise SystemExit("Receipt exists and differs. Do not silently overwrite.")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(payload)
    print("S003 VERIFIED; receipt:",OUT,"sha256:",hashlib.sha256(payload).hexdigest())
if __name__=="__main__":
    main()
