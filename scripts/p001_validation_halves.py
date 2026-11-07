#!/usr/bin/env python3
"""P001 frozen deterministic validation halves, no data values accessed.

From repo root (pinned Python 3.12.10, numpy 2.1.3, sklearn 1.5.2):
    .venv\\Scripts\\python.exe scripts/p001_validation_halves.py --mode generate
    .venv\\Scripts\\python.exe scripts/p001_validation_halves.py --mode verify

Never regenerate over a locked manifest. This performs no masking, fit or evaluation.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path

ROOT=Path("artifacts/p001")
S001=Path("artifacts/splits/adult_split_manifest.json")
VALIDATION=Path("artifacts/splits/adult_validation_indices.txt")
SEED=20261114
EXPECTED_VAL_SHA="48add8759a60eeaf7b12cdbed787dfb5ff3a78ec9161ab1b92c49cabb5b02e03"
EXPECTED_ALL_SHA="db42df2db7b844a30cd340aecb4c738c8ac7a056d0b4fb4088b6eb7319e5d667"

def sha(b):return hashlib.sha256(b).hexdigest()

def build():
    import numpy as np
    import sklearn
    if platform.python_version()!="3.12.10" or np.__version__!="2.1.3" or sklearn.__version__!="1.5.2":
        raise RuntimeError("P001 validation split requires Python 3.12.10 numpy 2.1.3 sklearn 1.5.2")
    s001_bytes=S001.read_bytes()
    s001=json.loads(s001_bytes)
    if s001["concatenated_index_files_sha256"]!=EXPECTED_ALL_SHA:
        raise RuntimeError("S001 combined assignment differs")
    if s001["index_files"]["validation"]["sha256"]!=EXPECTED_VAL_SHA:
        raise RuntimeError("S001 validation SHA differs")
    data=VALIDATION.read_bytes()
    if sha(data)!=EXPECTED_VAL_SHA or b"\\r" in data:
        raise RuntimeError("S001 validation indices byte SHA / LF mismatch")
    ids=np.array([int(v) for v in data.decode("ascii").splitlines()],dtype=np.int64)
    if len(ids)!=4884 or len(set(ids.tolist()))!=4884 or list(ids)!=sorted(ids.tolist()):
        raise RuntimeError("S001 validation IDs not 4884 distinct sorted values")
    reserved=set(s001["seed_taxonomy"].values())
    if SEED in reserved:
        raise RuntimeError("seed collision with S001 taxonomy")
    shuffled=np.random.default_rng(SEED).permutation(ids)
    first=np.sort(shuffled[:2442])
    second=np.sort(shuffled[2442:])
    if len(first)!=2442 or len(second)!=2442 or len(set(first)&set(second))!=0:
        raise RuntimeError("bad half sizes or overlap")
    if not np.array_equal(np.sort(np.concatenate([first,second])),ids):
        raise RuntimeError("halves do not cover exactly S001 validation")
    bytes_map={
        "selection":("".join(f"{int(x)}\\n" for x in first)).encode("ascii"),
        "reporting":("".join(f"{int(x)}\\n" for x in second)).encode("ascii"),
    }
    manifest={
        "schema":"P001_VALIDATION_HALVES_v1",
        "status":"INDEX_PREPARATION_ONLY; PILOT_NOT_AUTHORIZED",
        "algorithm":"sort S001 validation row indices ascending; numpy.random.default_rng(20261114).permutation(ids); first 2442 selection remainder 2442 reporting; sort within each half; 1-index source row IDs; LF",
        "seed_name":"pilot_validation_partition",
        "seed":SEED,
        "source_validation_sha256":EXPECTED_VAL_SHA,
        "source_s001_combined_sha256":EXPECTED_ALL_SHA,
        "source_s001_manifest_sha256":sha(s001_bytes),
        "python_version":platform.python_version(),
        "numpy_version":np.__version__,
        "sklearn_version":sklearn.__version__,
        "indices":{
            name:{"path":f"adult_validation_{name}_indices.txt",
                  "rows":2442,"sha256":sha(b)} for name,b in bytes_map.items()
        },
        "source_validation_id_count":4884,
        "halves_disjoint_and_complete":True,
        "no_raw_dataset_values_accessed":True,
        "no_model_fitting_or_mask_generation":True,
        "reporting_half_role":"held-out for one preregistered evaluation; do not tune or calibrate on it",
    }
    return bytes_map,(json.dumps(manifest,sort_keys=True,indent=2)+"\\n").encode("utf-8")

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--mode",required=True,choices=["generate","verify"])
    mode=arg.parse_args().mode
    halves,manifest=build()
    expected={ROOT/"adult_validation_halves_manifest.json":manifest}
    expected.update({ROOT/f"adult_validation_{k}_indices.txt":v for k,v in halves.items()})
    if mode=="generate":
        if any(p.exists() for p in expected):
            raise RuntimeError("P001 index or manifest already exists; use --mode verify; no overwrite")
        ROOT.mkdir(parents=True,exist_ok=True)
        for p,b in expected.items():p.write_bytes(b)
        print("P001 INDEX HALVES GENERATED; must verify and commit before prereg freeze")
    else:
        for p,b in expected.items():
            if not p.is_file() or p.read_bytes()!=b:
                raise RuntimeError(f"P001 SPLIT REGRESSION FAILURE: {p}")
        print("P001 VALIDATION HALVES VERIFIED against S001 source and pinned algorithm")
    print("P001 MANIFEST SHA256:",sha(manifest))
    for k,b in halves.items():print(k,"rows=2442","SHA256=",sha(b))
if __name__=="__main__":main()
