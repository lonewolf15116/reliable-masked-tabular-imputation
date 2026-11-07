#!/usr/bin/env python3
"""S003 verify-only receipt, version 2; fails closed on structural invariants.

Run from repo root with the pinned local Python environment.
No raw dataset, masks, or prediction models are accessed.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

VERSION="S003-VERIFY-RECEIPT-v2"
OUT=Path("evidence/S003_VERIFY_RECEIPT.json")
PATHS=[
 "artifacts/source/adult_source_audit.json",
 "artifacts/splits/adult_split_manifest.json",
 "artifacts/splits/adult_train_indices.txt",
 "artifacts/splits/adult_validation_indices.txt",
 "artifacts/splits/adult_test_indices.txt",
 "artifacts/stats/adult_train_feature_stats.json",
 "artifacts/eligible_cells/adult_feature_eligibility.json",
 "protocol/A003_OWNER_APPROVAL_2026-11-07.md",
 "scripts/s003_eligible_features.py",
 "scripts/s003_verify_receipt.py",
]
COUNTS={"train":22792,"validation":4884,"test":4885}
EXPECTED_FEATURES=["age","workclass","fnlwgt","education","education-num",
 "marital-status","occupation","relationship","race","sex","capital-gain",
 "capital-loss","hours-per-week","native-country"]
ZERO={"capital-gain","capital-loss"}
EXPECTED_COMBINED="db42df2db7b844a30cd340aecb4c738c8ac7a056d0b4fb4088b6eb7319e5d667"

def hash_bytes(b): return hashlib.sha256(b).hexdigest()
def read_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def ensure(ok,msg):
    if not ok: raise RuntimeError("FAIL CLOSED: "+msg)

def main():
    run=subprocess.run([sys.executable,"scripts/s003_eligible_features.py","--mode","verify"],
                       capture_output=True,text=True,check=False)
    ensure(run.returncode==0 and "VERIFIED S003 feature-eligibility artifact" in run.stdout,
           "S003 reproducibility check failed: "+run.stdout+run.stderr)
    split=read_json("artifacts/splits/adult_split_manifest.json")
    stats=read_json("artifacts/stats/adult_train_feature_stats.json")
    elig=read_json("artifacts/eligible_cells/adult_feature_eligibility.json")
    audit=read_json("artifacts/source/adult_source_audit.json")
    approval=Path("protocol/A003_OWNER_APPROVAL_2026-11-07.md").read_text(encoding="utf-8")
    ensure(split["concatenated_index_files_sha256"]==EXPECTED_COMBINED,"S001 combined split hash")
    ensure(stats["s001_combined_assignment_sha256"]==EXPECTED_COMBINED,"S002 split linkage")
    ensure(elig["s001_combined_assignment_sha256"]==EXPECTED_COMBINED,"S003 split linkage")
    ensure(audit["row_count"]==sum(COUNTS.values()),"source row count mismatch")
    ids_by_split={}
    split_bytes=[]
    for name in ("train","validation","test"):
        info=split["index_files"][name]
        raw=Path("artifacts/splits",info["path"]).read_bytes()
        ensure(b"\\r" not in raw and hash_bytes(raw)==info["sha256"],name+" index raw bytes/hash")
        ids=[int(v) for v in raw.decode("ascii").splitlines()]
        ensure(len(ids)==COUNTS[name] and len(ids)==info["rows"],name+" counts")
        ensure(ids==sorted(set(ids)) and all(1<=v<=32561 for v in ids),name+" index uniqueness/order")
        ensure(elig["per_split"][name]["n_rows"]==len(ids),name+" eligible count")
        ensure(elig["per_split"][name]["row_index_sha256"]==info["sha256"],name+" eligible index hash")
        ensure(elig["per_split"][name]["all_predictor_cells"]==len(ids)*len(EXPECTED_FEATURES),
               name+" total predictor-cell count")
        ids_by_split[name]=ids
        split_bytes.append(raw)
    combined=set(ids_by_split["train"]+ids_by_split["validation"]+ids_by_split["test"])
    ensure(len(combined)==32561 and min(combined)==1 and max(combined)==32561,
           "overlap or missing row indices")
    ensure(hash_bytes(b"".join(split_bytes))==EXPECTED_COMBINED,"recomputed concatenated index hash")
    ensure(set(stats["imputation_feature_names"])==set(EXPECTED_FEATURES)
           and len(stats["imputation_feature_names"])==len(EXPECTED_FEATURES)
           and "income" not in stats["imputation_feature_names"],"actual S002 imputation feature names")
    ensure(audit["column_names"]==EXPECTED_FEATURES+["income"],"actual Adult source columns")
    ensure(set(stats["numeric_feature_stats"])=={"age","fnlwgt","education-num","capital-gain","capital-loss","hours-per-week"},"numeric stats scope")
    computed_zero={f for f,v in stats["numeric_feature_stats"].items() if v["iqr"]==0.0}
    ensure(computed_zero==ZERO and set(stats["exact_zero_iqr_numeric_features"])==ZERO
           and set(stats["primary_normalized_error_excludes"])==ZERO
           and stats["exact_zero_iqr_feature_count"]==2,"exact-zero-IQR feature lock")
    ensure(set(elig["eligible_definitions"]["zero_iqr_numeric"])==ZERO,"S003 zero-IQR lock")
    ensure("Adult" in approval and "`age`" in approval and "sole never-masked" in approval
           and "DESIGN APPROVED; NOT OPERATIONAL" in approval
           and "single" in approval.lower(),"A003 approval document lacks required conditions")
    for name in COUNTS:
        feat=elig["per_split"][name]["feature_eligibility"]
        ensure(set(feat)==set(EXPECTED_FEATURES) and "income" not in feat,
               name+" actual per-feature scope")
        ensure(feat["age"]["adult_mar_eligible_if_A003_approved"] is False
               and feat["age"]["adult_mar_driver_if_A003_approved"] is None,
               name+" reserved age flag")
        for f in EXPECTED_FEATURES:
            if f=="age": continue
            ensure(feat[f]["adult_mar_eligible_if_A003_approved"] is True
                   and feat[f]["adult_mar_driver_if_A003_approved"]=="age",
                   name+" MAR driver for "+f)
            ensure(feat[f]["included_in_primary_iqr_normalized_numeric_error"]==(f in stats["numeric_feature_stats"] and f not in ZERO),
                   name+" primary IQR flag "+f)
    ensure(audit["question_mark_count_per_column"]=={
        **{f:0 for f in EXPECTED_FEATURES+["income"] if f not in {"workclass","occupation","native-country"}},
        "workclass":1836,"occupation":1843,"native-country":583}, "literal question-mark source counts")
    checks={
       "source_rows":32561,"recomputed_split_rows":COUNTS,
       "recomputed_disjoint_full_coverage":True,
       "recomputed_combined_index_sha256":EXPECTED_COMBINED,
       "feature_set_excludes_income":True,
       "exact_zero_iqr_feature_names":sorted(ZERO),
       "mar_anchor_age_excluded_and_other_drivers_age":True,
       "a003_conditions_document_present":True,
       "question_mark_counts_match_source_audit":True
    }
    rec={"receipt_schema":VERSION,"python_version":sys.version.split()[0],
         "verification_command":"python scripts/s003_eligible_features.py --mode verify",
         "verification_exit_code":run.returncode,"verification_stdout":run.stdout,
         "structural_checks":checks,
         "sha256_by_file":{p:hash_bytes(Path(p).read_bytes()) for p in PATHS},
         "receipt_script_sha256":hash_bytes(Path(__file__).read_bytes()),
         "status":"S003 FEATURE-LEVEL VERIFIED; MASK-LEVEL CELL IDS NOT GENERATED",
         "dataset_source_sha256":audit["sha256_of_original_unmodified_bytes"]}
    payload=(json.dumps(rec,sort_keys=True,indent=2)+"\n").encode("utf-8")
    if OUT.exists() and OUT.read_bytes()!=payload:
        raise RuntimeError("receipt already exists but differs; no overwriting")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_bytes(payload)
    print("S003 STRUCTURE + REGEN VERIFIED")
    print("S003 RECEIPT SHA256:",hash_bytes(payload))
    print("Commit receipt; ledger must later record this hash after remote verification.")

if __name__=="__main__": main()
