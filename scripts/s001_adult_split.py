#!/usr/bin/env python3
"""Generate OR independently verify S001 Adult row-index split. No model fitting.

python scripts/s001_adult_split.py --mode generate
python scripts/s001_adult_split.py --mode verify

Strict runtime: Python 3.12, numpy 2.1.3, sklearn 1.5.2.
"""
import argparse
import csv
import hashlib
import io
import json
import platform
from pathlib import Path

EXPECTED_SHA = "5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"
SEEDS = dict(split=20261107, masking=20261108, model_initialization=20261109,
             calibration_conformal=20261110, bootstrap_diagnostics=20261111)
FOLDER = Path("artifacts/splits")
SOURCE = Path("artifacts/source/adult.data")

def sha(b):
    return hashlib.sha256(b).hexdigest()

def build():
    import numpy as np
    import sklearn
    from sklearn.model_selection import train_test_split
    if platform.python_version_tuple()[:2] != ("3","12"):
        raise RuntimeError("S001 requires Python 3.12.x")
    if np.__version__ != "2.1.3" or sklearn.__version__ != "1.5.2":
        raise RuntimeError(f"S001 requires numpy=2.1.3/sklearn=1.5.2; got {np.__version__}/{sklearn.__version__}")
    if len(set(SEEDS.values())) != len(SEEDS):
        raise AssertionError("seed reuse across classes")
    raw = SOURCE.read_bytes()
    if sha(raw) != EXPECTED_SHA:
        raise RuntimeError("original Adult raw SHA mismatch")
    rows = [r for r in csv.reader(io.StringIO(raw.decode("utf-8"))) if r]
    if len(rows) != 32561 or any(len(r) != 15 for r in rows):
        raise RuntimeError("unexpected source structure")
    labels = np.array([r[-1].strip() for r in rows])
    if set(labels) != {"<=50K",">50K"}:
        raise RuntimeError("unexpected income classes")
    idx = np.arange(1,32562,dtype=np.int64)
    train, temp, train_y, temp_y = train_test_split(
        idx,labels,test_size=0.30,random_state=SEEDS["split"],shuffle=True,stratify=labels)
    val, test, _, _ = train_test_split(
        temp,temp_y,test_size=0.50,random_state=SEEDS["split"],shuffle=True,stratify=temp_y)
    arrays=dict(train=train,validation=val,test=test)
    combined=np.concatenate([train,val,test])
    if len(combined)!=32561 or len(np.unique(combined))!=32561 or not np.array_equal(np.sort(combined),idx):
        raise AssertionError("duplicate, missing or overlapping indices")
    bytes_map = {k:("".join(f"{int(x)}\n" for x in sorted(v))).encode("utf-8") for k,v in arrays.items()}
    meta = {
        "source_sha256":EXPECTED_SHA,"source_file":"adult.data only; adult.test not used",
        "split_seed":SEEDS["split"],"seed_taxonomy":SEEDS,
        "algorithm":"train_test_split twice, stratified on stripped raw income labels; first test_size=0.30, then temp test_size=0.50; both random_state=20261107; shuffle=True; 1-index raw rows; sorted only when writing",
        "versions":{"python":platform.python_version(),"numpy":np.__version__,"sklearn":sklearn.__version__},
        "role_of_income":"stratification ONLY; never an imputation input or masked feature",
        "index_base":1,
        "index_files":{},
    }
    for name,arr in arrays.items():
        ids = np.asarray(arr,dtype=np.int64)
        counts = {lab:int(np.sum(labels[ids-1]==lab)) for lab in sorted(set(labels))}
        meta["index_files"][name]={"path":f"adult_{name}_indices.txt","rows":int(len(ids)),
                                   "sha256":sha(bytes_map[name]),"income_balance":counts}
    meta["concatenation_order"]=["train","validation","test"]
    meta["concatenated_index_files_sha256"]=sha(bytes_map["train"]+bytes_map["validation"]+bytes_map["test"])
    manifest = (json.dumps(meta,sort_keys=True,indent=2)+"\n").encode("utf-8")
    return bytes_map,manifest

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["generate","verify"],required=True)
    args=parser.parse_args()
    files,manifest=build()
    if args.mode=="generate":
        if (FOLDER/"adult_split_manifest.json").exists():
            raise RuntimeError("Manifest already exists; use --mode verify; never silently regenerate")
        FOLDER.mkdir(parents=True,exist_ok=True)
        for split,payload in files.items():
            (FOLDER/f"adult_{split}_indices.txt").write_bytes(payload)
        (FOLDER/"adult_split_manifest.json").write_bytes(manifest)
        print("Generated S001 split indices; MUST verify before gate approval.")
    else:
        for split,payload in files.items():
            if (FOLDER/f"adult_{split}_indices.txt").read_bytes()!=payload:
                raise RuntimeError(f"REPRODUCIBILITY FAIL: {split} index bytes differ")
        if (FOLDER/"adult_split_manifest.json").read_bytes()!=manifest:
            raise RuntimeError("REPRODUCIBILITY FAIL: manifest bytes differ")
        print("VERIFIED S001 raw-source index files, manifest bytes, and SHA256 metadata")
    print(manifest.decode())

if __name__=="__main__":
    main()
