#!/usr/bin/env python3
"""R003 download-and-check script for an independently networked machine.

Usage:
  python scripts/r003_acquire_adult.py --url https://raw.githubusercontent.com/batuhansahincanel/UCIsAdultDataset/main/adult.data --out artifacts/source/adult.data
Do not commit adult.data unless dataset redistribution is separately approved.
No model fitting, splitting, or preprocessing occurs.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

REFERENCE = "5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"
DEFAULT_URL = "https://raw.githubusercontent.com/batuhansahincanel/UCIsAdultDataset/main/adult.data"

def audit(data: bytes, url: str):
    sha = hashlib.sha256(data).hexdigest()
    # Preserves original UCI source bytes, including line endings; never normalize before hashing.
    lines = [x for x in data.splitlines() if x.strip()]
    delim_counts = sorted({line.count(b",") for line in lines})
    return {
        "url":url,
        "retrieval_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "byte_size":len(data),
        "sha256":sha,
        "candidate_third_party_sha256":REFERENCE,
        "candidate_third_party_sha256_match":sha==REFERENCE,
        "uci_publisher_checksum_verified":False,
        "nonempty_rows":len(lines),
        "row_count_matches_original_adult_training":len(lines)==32561,
        "distinct_commas_per_line":delim_counts,
        "structure_15_columns":delim_counts==[14],
        "status":"CANDIDATE_MATCH_NEEDS_REVIEW" if sha==REFERENCE and len(lines)==32561 and delim_counts==[14] else "FAIL_OR_MISMATCH"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--out", default="artifacts/source/adult.data")
    p.add_argument("--audit", default="artifacts/source/adult_source_audit.json")
    args=p.parse_args()
    with urllib.request.urlopen(args.url,timeout=40) as resp:
        data=resp.read()
    report=audit(data,args.url)
    path=Path(args.audit)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    if report["status"]!="CANDIDATE_MATCH_NEEDS_REVIEW":
        print(json.dumps(report,indent=2))
        raise SystemExit("R003 NOT VERIFIED: actual bytes failed candidate identity/structure checks")
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
    print(json.dumps(report,indent=2))
    print("CANDIDATE SOURCE MATCH ONLY: two third-party references agree; not a UCI publisher-issued checksum.")

if __name__=="__main__":main()
