#!/usr/bin/env python3
"""R003 source-byte acquisition and audit only. No model fitting or splits.

Run from repo root: python scripts/r003_acquire_adult.py
Adult input is 32,561 rows and 15 fields, last field being the downstream target.
Do not commit acquired raw bytes unless redistribution has been separately approved.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
from pathlib import Path
import urllib.request

REFERENCE = "5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"
DEFAULT_URL = "https://raw.githubusercontent.com/batuhansahincanel/UCIsAdultDataset/main/adult.data"
COLS = ["age","workclass","fnlwgt","education","education-num","marital-status",
        "occupation","relationship","race","sex","capital-gain","capital-loss",
        "hours-per-week","native-country","income"]
NUMERIC = {"age","fnlwgt","education-num","capital-gain","capital-loss","hours-per-week"}

def audit(data: bytes, url: str):
    sha = hashlib.sha256(data).hexdigest()
    decode_error = None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        decode_error = str(exc)
        text = data.decode("utf-8",errors="replace")
    rows = [[cell.strip() for cell in row] for row in csv.reader(io.StringIO(text))
            if any(cell.strip() for cell in row)]
    widths = sorted(set(map(len,rows)))
    widths_ok = widths == [len(COLS)]
    counts = {k:sum(row[j]=="?" for row in rows if len(row)>j) for j,k in enumerate(COLS)}
    dtype = {}
    for j,k in enumerate(COLS):
        values=[row[j] for row in rows if len(row)>j and row[j]!="?"]
        if k in NUMERIC:
            try:
                parsed=[float(v) for v in values]
                inferred = "integer" if all(v.is_integer() for v in parsed) else "float"
            except ValueError:
                inferred = "INVALID_NUMERIC"
        else:
            inferred = "categorical_string"
        dtype[k]={"expected": "numeric" if k in NUMERIC else "categorical", "inferred":inferred,
                  "distinct_observed_values":len(set(values))}
    report={
        "source_url":url,
        "retrieval_timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "byte_size":len(data),"sha256_of_original_unmodified_bytes":sha,
        "candidate_third_party_sha256":REFERENCE,
        "matches_candidate_third_party_record":sha==REFERENCE,
        "uci_issued_checksum_compared":False,
        "uci_identity_inference":"Candidate byte-identity consistent with published third-party records; not proven against UCI-issued checksum" if sha==REFERENCE else "No matching provenance",
        "row_count":len(rows),"column_count":len(COLS) if widths_ok else None,
        "observed_row_widths":widths,"column_names":COLS,
        "dtype_summary":dtype,"question_mark_count_per_column":counts,
        "question_marks_treated_as_observed_categories":True,
        "utf8_decode_error":decode_error,
    }
    report["candidate_identity_and_structure_match"]=(sha==REFERENCE and len(rows)==32561 and widths_ok and decode_error is None
        and all(dtype[k]["inferred"] in ("integer","float") for k in NUMERIC))
    report["status"]="CANDIDATE_MATCH_NEEDS_REVIEW" if report["candidate_identity_and_structure_match"] else "FAIL_OR_MISMATCH"
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--url",default=DEFAULT_URL)
    p.add_argument("--out",default="artifacts/source/adult.data")
    p.add_argument("--audit",default="artifacts/source/adult_source_audit.json")
    args=p.parse_args()
    with urllib.request.urlopen(args.url,timeout=40) as response:
        data=response.read()
    report=audit(data,args.url)
    output=Path(args.audit);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if not report["candidate_identity_and_structure_match"]:
        print(json.dumps(report,indent=2))
        raise SystemExit("R003 BLOCKED: source bytes did not match expected identity/structure.")
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
    print(json.dumps(report,indent=2))
    print("Candidate identity only; commit audit JSON for review, not raw source bytes.")

if __name__=="__main__":main()
