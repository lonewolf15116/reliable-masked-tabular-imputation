#!/usr/bin/env python3
"""S002 training-only Adult feature audit. Generate once; verify against committed lock.

From repository root:
  .venv\\Scripts\\python.exe scripts/s002_adult_train_stats.py --mode generate
  .venv\\Scripts\\python.exe scripts/s002_adult_train_stats.py --mode verify
"""
import argparse
import csv
import hashlib
import io
import json
import platform
from pathlib import Path

SOURCE=Path("artifacts/source/adult.data")
TRAIN=Path("artifacts/splits/adult_train_indices.txt")
SPLIT=Path("artifacts/splits/adult_split_manifest.json")
OUTPUT=Path("artifacts/stats/adult_train_feature_stats.json")
SOURCE_SHA="5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"
NUM=["age","fnlwgt","education-num","capital-gain","capital-loss","hours-per-week"]
COLS=["age","workclass","fnlwgt","education","education-num","marital-status","occupation",
      "relationship","race","sex","capital-gain","capital-loss","hours-per-week",
      "native-country","income"]

def hash_bytes(b):
    return hashlib.sha256(b).hexdigest()

def construct():
    import numpy as np
    import sklearn
    if platform.python_version_tuple()[:2] != ("3","12"):
        raise RuntimeError("S002 requires Python 3.12.x")
    if np.__version__ != "2.1.3" or sklearn.__version__ != "1.5.2":
        raise RuntimeError("S002 requires numpy 2.1.3 and scikit-learn 1.5.2")
    raw=SOURCE.read_bytes()
    if hash_bytes(raw)!=SOURCE_SHA:
        raise RuntimeError("source raw bytes SHA mismatch")
    split=json.loads(SPLIT.read_text(encoding="utf-8"))
    if split.get("source_sha256")!=SOURCE_SHA:
        raise RuntimeError("S001 split source SHA mismatch")
    train_bytes=TRAIN.read_bytes()
    if hash_bytes(train_bytes)!=split["index_files"]["train"]["sha256"]:
        raise RuntimeError("S001 train index SHA mismatch (including line endings)")
    if b"\r" in train_bytes:
        raise RuntimeError("S001 index file must have LF, not CRLF")
    ids=[int(v) for v in train_bytes.decode("ascii").splitlines()]
    if len(ids)!=22792 or len(ids)!=len(set(ids)) or ids!=sorted(ids) or not all(1<=x<=32561 for x in ids):
        raise RuntimeError("invalid training index set")
    rows=list(csv.reader(io.StringIO(raw.decode("utf-8"))))
    if len(rows)!=32561 or any(len(r)!=15 for r in rows):
        raise RuntimeError("invalid raw Adult schema")
    selected=[[v.strip() for v in rows[i-1]] for i in ids]
    # These are the only rows inspected for train feature statistics.
    numeric_stats={}
    for name in NUM:
        j=COLS.index(name)
        values=np.array([float(r[j]) for r in selected],dtype=np.float64)
        if not np.isfinite(values).all():
            raise RuntimeError(f"nonfinite train value in {name}")
        q1,median,q3=[float(x) for x in np.quantile(values,[.25,.5,.75],method="linear")]
        iqr=q3-q1
        numeric_stats[name]={"n_train":len(values),"q25":q1,"median":median,"q75":q3,
                             "iqr":iqr,"exact_zero_iqr":bool(iqr==0.0),
                             "min":float(values.min()),"max":float(values.max())}
    cats={}
    for name in COLS:
        if name not in NUM and name!="income":
            j=COLS.index(name)
            observed=sorted({r[j] for r in selected})
            if any(v=="" for v in observed):
                raise RuntimeError(f"unexpected empty categorical token in {name}")
            cats[name]={"n_levels":len(observed),"levels":observed,
                        "question_mark_is_literal_level":"?" in observed,
                        "question_mark_train_count":sum(r[j]=="?" for r in selected)}
    zero=sorted(k for k,v in numeric_stats.items() if v["exact_zero_iqr"])
    out={
        "protocol":"S002_TRAIN_STATS_ZERO_IQR_LOCK",
        "source_sha256":SOURCE_SHA,
        "s001_train_index_sha256":hash_bytes(train_bytes),
        "s001_combined_assignment_sha256":split["concatenated_index_files_sha256"],
        "num_train_rows":len(ids),
        "numpy_version":np.__version__,
        "sklearn_version":sklearn.__version__,
        "python_version":platform.python_version(),
        "quantile_method":"numpy.quantile([0.25,0.5,0.75], method='linear') float64, train rows only",
        "numeric_feature_stats":numeric_stats,
        "categorical_training_vocabularies":cats,
        "exact_zero_iqr_numeric_features":zero,
        "exact_zero_iqr_feature_count":len(zero),
        "primary_normalized_error_excludes":zero,
        "zero_iqr_reporting_policy":"exclude from primary IQR-normalized aggregate numerator and denominator; report separately in raw units",
        "income_role":"stratification label only; not imputation feature",
        "imputation_feature_names":[x for x in COLS if x!="income"],
        "question_mark_policy":"observed categorical token, never coerced to missing",
        "no_validation_or_test_statistics_used":True,
        "no_model_fitting_performed":True,
    }
    assert "income" not in out["imputation_feature_names"]
    assert out["primary_normalized_error_excludes"]==out["exact_zero_iqr_numeric_features"]
    return (json.dumps(out,sort_keys=True,indent=2,ensure_ascii=True)+"\n").encode("utf-8"),out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=["generate","verify"],required=True)
    args=ap.parse_args()
    payload,out=construct()
    if args.mode=="generate":
        if OUTPUT.exists():
            raise RuntimeError("S002 lock already exists: use --mode verify; no silent overwrite")
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_bytes(payload)
        print("S002 GENERATED: verification + commit required before freeze")
    else:
        if not OUTPUT.exists() or OUTPUT.read_bytes()!=payload:
            raise RuntimeError("S002 REGRESSION FAILURE: source, indices, quantiles, vocab or zero-IQR lock changed")
        print("S002 VERIFIED: source, S001 indices, full train-only stats, category vocab and exact-zero-IQR set")
    print(json.dumps({"numeric_iqrs":{k:v["iqr"] for k,v in out["numeric_feature_stats"].items()},
                      "exact_zero_iqr_numeric_features":out["exact_zero_iqr_numeric_features"],
                      "exact_zero_iqr_feature_count":out["exact_zero_iqr_feature_count"],
                      "stats_file_sha256":hash_bytes(payload)},indent=2))

if __name__=="__main__":
    main()
