#!/usr/bin/env python3
"""S003 feature-level eligible-cell population, independent of any model or mask.

Runs against committed S001/S002 JSON and split-index files; never opens Adult raw
rows or S001 test labels. A003 MAR anchor remains proposed, not approved.
Usage:
  python scripts/s003_eligible_features.py --mode generate
  python scripts/s003_eligible_features.py --mode verify
"""
import argparse
import hashlib
import json
from pathlib import Path

SPLIT=Path("artifacts/splits/adult_split_manifest.json")
STATS=Path("artifacts/stats/adult_train_feature_stats.json")
OUT=Path("artifacts/eligible_cells/adult_feature_eligibility.json")
SOURCE_SHA="5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"
NUM={"age","fnlwgt","education-num","capital-gain","capital-loss","hours-per-week"}
FEATURES=["age","workclass","fnlwgt","education","education-num","marital-status",
          "occupation","relationship","race","sex","capital-gain","capital-loss",
          "hours-per-week","native-country"]

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def build():
    sp=SPLIT.read_bytes()
    st=STATS.read_bytes()
    split=json.loads(sp)
    stats=json.loads(st)
    if split["source_sha256"]!=SOURCE_SHA or stats["source_sha256"]!=SOURCE_SHA:
        raise RuntimeError("source identity mismatch")
    if stats["s001_combined_assignment_sha256"]!=split["concatenated_index_files_sha256"]:
        raise RuntimeError("S001/S002 assignment mismatch")
    if stats["s001_train_index_sha256"]!=split["index_files"]["train"]["sha256"]:
        raise RuntimeError("S001/S002 training split mismatch")
    if stats["num_train_rows"]!=split["index_files"]["train"]["rows"]:
        raise RuntimeError("training count mismatch")
    if stats["imputation_feature_names"]!=FEATURES or "income" in FEATURES:
        raise RuntimeError("imputation feature list unexpected or income leaked")
    zero=stats["exact_zero_iqr_numeric_features"]
    if sorted(zero)!=["capital-gain","capital-loss"] or zero!=stats["primary_normalized_error_excludes"]:
        raise RuntimeError("S002 zero IQR lock mismatch")
    if not set(zero)<=NUM:
        raise RuntimeError("non-numeric feature marked zero-IQR")
    records={}
    overall={}
    for split_name in ("train","validation","test"):
        info=split["index_files"][split_name]
        fname=Path("artifacts/splits")/info["path"]
        raw=fname.read_bytes()
        if digest(raw)!=info["sha256"] or b"\r" in raw:
            raise RuntimeError(f"index hash / line ending mismatch: {split_name}")
        ids=[int(s) for s in raw.decode("ascii").splitlines()]
        if len(ids)!=info["rows"] or ids!=sorted(set(ids)):
            raise RuntimeError(f"duplicate / unsorted / count error: {split_name}")
        per_feature={}
        for feature in FEATURES:
            per_feature[feature]={
                "potentially_mask_eligible_cells_before_A003_and_mask_seed":len(ids),
                "ground_truth":"all original observed Adult cells; literal ? is observed category",
                "numeric":feature in NUM,
                "included_in_primary_iqr_normalized_numeric_error":feature in NUM and feature not in zero,
                "separate_raw_unit_numeric_reporting":feature in zero,
                "categorical_primary_reporting":feature not in NUM,
                "adult_mar_driver_if_A003_approved":"age" if feature!="age" else None,
                "adult_mar_eligible_if_A003_approved":feature!="age",
                "adult_mar_anchor_status":"reserved; not MAR maskable" if feature=="age" else "candidate MAR mask target",
            }
        records[split_name]={
            "row_index_file":info["path"],"row_index_sha256":info["sha256"],
            "n_rows":len(ids),"feature_eligibility":per_feature,
            "all_predictor_cells":len(ids)*len(FEATURES),
            "numeric_primary_eligible_cells_pre_mask":len(ids)*(len(NUM)-len(zero)),
            "numeric_zero_iqr_separate_cells":len(ids)*len(zero),
            "categorical_cells_pre_mask":len(ids)*(len(FEATURES)-len(NUM)),
            "proposed_mar_target_cells":len(ids)*(len(FEATURES)-1),
        }
    result={
        "protocol":"S003_FEATURE_ELIGIBILITY_ONLY",
        "status":"PREMASK_FEATURE_LEVEL; A003 NOT APPROVED",
        "source_sha256":SOURCE_SHA,
        "split_manifest_sha256":digest(sp),
        "s001_combined_assignment_sha256":split["concatenated_index_files_sha256"],
        "s002_train_stats_sha256":digest(st),
        "per_split":records,
        "eligible_definitions":{
          "target":"income NEVER an imputation input, mask target, or eligible comparison cell",
          "question_mark":"literal ? observed categorical ground truth; no missing coercion",
          "rows":"all 32561 original rows retained in the locked partitions",
          "zero_iqr_numeric":zero,
          "zero_iqr_policy":"excluded from primary IQR-normalized numeric error numerator and denominator; separately report in raw units; not deleted",
          "mar_anchor":"age proposed by A003, never MAR-masked if approved",
          "mar_generalization":"single-anchor Adult simulation conditional on age only, if A003 approved",
          "mask_selected_cell_set":"NOT GENERATED; requires approved A003 then fixed seed/mask manifest shared across methods",
        },
        "no_raw_test_row_values_read":True,
        "no_predictions_or_model_fitting":True
    }
    return (json.dumps(result,sort_keys=True,indent=2)+"\n").encode("utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=["generate","verify"])
    args=p.parse_args()
    payload=build()
    if args.mode=="generate":
        if OUT.exists():
            raise RuntimeError("Existing S003 artifact; verify instead, never silently overwrite")
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_bytes(payload)
        print("GENERATED S003 feature eligibility; A003 and mask-level eligibility remain pending")
    else:
        if not OUT.is_file() or OUT.read_bytes()!=payload:
            raise RuntimeError("S003 REGRESSION FAILURE: eligibility artifact differs")
        print("VERIFIED S003 feature-eligibility artifact against frozen S001 and S002")
    print("S003 SHA256:",digest(payload))

if __name__=="__main__":
    main()
