#!/usr/bin/env python3
"""Adult R002 finite-population masking checks and deterministic evidence receipt.

NO model fitting. NO test masks generated. NO independent distributional PASS claimed:
an external reference/reviewer remains required for the n=10,k=2 law.
Run from repository root in pinned .venv:
  python scripts/r002_adult_verify.py
"""
import csv
import hashlib
import io
import json
import math
import platform
from pathlib import Path

import numpy as np
import pandas as pd
from src.rmti.masking import generate_mask, probabilities

VERSION="R002-ADULT-v1"
SOURCE=Path("artifacts/source/adult.data")
SPLIT=Path("artifacts/splits/adult_split_manifest.json")
S003=Path("artifacts/eligible_cells/adult_feature_eligibility.json")
STATS=Path("artifacts/stats/adult_train_feature_stats.json")
APPROVAL=Path("protocol/A003_OWNER_APPROVAL_2026-11-07.md")
OUT=Path("evidence/R002_ADULT_EXECUTION_RECEIPT.json")
SOURCE_SHA="5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d"
COLS=["age","workclass","fnlwgt","education","education-num","marital-status","occupation",
      "relationship","race","sex","capital-gain","capital-loss","hours-per-week","native-country","income"]
FEATURES=[x for x in COLS if x not in ("age","income")]
RATES=[0.10,0.20,0.30]
SEED=20261108

def sha(data):
    return hashlib.sha256(data).hexdigest()
def check(b,reason):
    if not b: raise RuntimeError("R002 FAIL: "+reason)
def file_hash(path):
    return sha(Path(path).read_bytes())
def main():
    import sklearn
    check(platform.python_version_tuple()[:2]==("3","12"),"Python 3.12 required")
    check(np.__version__=="2.1.3" and sklearn.__version__=="1.5.2","pinned versions")
    raw=SOURCE.read_bytes()
    check(sha(raw)==SOURCE_SHA,"raw Adult SHA256")
    rows=[[x.strip() for x in r] for r in csv.reader(io.StringIO(raw.decode("utf-8"))) if r]
    check(len(rows)==32561 and all(len(r)==15 for r in rows),"raw row schema")
    split=json.loads(SPLIT.read_text(encoding="utf-8"))
    stats=json.loads(STATS.read_text(encoding="utf-8"))
    s003=json.loads(S003.read_text(encoding="utf-8"))
    check(stats["source_sha256"]==SOURCE_SHA and s003["source_sha256"]==SOURCE_SHA,"source link")
    check("sole never-masked MAR anchor" in APPROVAL.read_text(encoding="utf-8"),"A003 record")
    ids={}
    for name in ("train","validation"):
        data=Path("artifacts/splits",split["index_files"][name]["path"]).read_bytes()
        check(sha(data)==split["index_files"][name]["sha256"],name+" index hash")
        ids[name]=[int(x) for x in data.decode("ascii").splitlines()]
    train_age=np.asarray([float(rows[i-1][0]) for i in ids["train"]],dtype=np.float64)
    mean=float(np.mean(train_age,dtype=np.float64))
    sd=float(np.std(train_age,ddof=0,dtype=np.float64))
    check(np.isfinite(mean) and np.isfinite(sd) and sd>0,"train-only standardization")
    train_z=np.asarray((train_age-mean)/sd,dtype=np.float64)
    checks={}
    qcounts={}
    for name,idx in (("train",ids["train"]),("validation",ids["validation"])):
        data=[rows[i-1] for i in idx]
        frame=pd.DataFrame(data,columns=COLS).drop(columns=["income"])
        anchor=np.asarray([(float(r[0])-mean)/sd for r in data],dtype=np.float64)
        anch=pd.DataFrame({"age":anchor})
        check("age" in frame.columns and "income" not in frame.columns,"schema exclusion")
        check(not set(FEATURES)&{"age","income"},"mask features exclusion")
        qcounts[name]={f:int((frame[f]=="?").sum()) for f in ("workclass","occupation","native-country")}
        for f in qcounts[name]:
            check(int((frame[f]=="?").sum())==qcounts[name][f],"literal ? preserved "+f)
        checks[name]={}
        for rate in RATES:
            key=f"{rate:.2f}"
            mask=generate_mask(frame,FEATURES,"MAR",rate,SEED,anchor_data=anch)
            check(mask.shape==(len(idx),13) and mask.dtype==bool,"mask dimensions")
            counts={f:int(mask[:,j].sum()) for j,f in enumerate(FEATURES)}
            expected=int(math.floor(rate*len(idx)+0.5))
            check(all(n==expected for n in counts.values()),name+" exact mask count "+key)
            check(np.array_equal(mask,generate_mask(frame,FEATURES,"MAR",rate,SEED,anchor_data=anch)),
                  name+" seeded determinism "+key)
            ps=probabilities(anchor,rate)
            check(np.isfinite(ps).all() and (ps>=.01).all() and (ps<=.99).all(),"weights bounded")
            check(abs(float(np.mean(ps))-rate)<1e-10,"mean calibrated inclusion weights")
            question_mark_masked={f:int(mask[:,FEATURES.index(f)][(frame[f]=="?").to_numpy()].sum())
                                  for f in qcounts[name]}
            # All '?' cells belong to full eligible set; masking may or may not select each.
            checks[name][key]={
               "per_feature_exact_counts":counts,
               "expected_each_feature":expected,
               "mask_deterministic":True,
               "anchor_is_unmasked":True,
               "income_excluded":True,
               "mean_clipped_logistic_weight":float(np.mean(ps)),
               "question_mark_observed_cells":qcounts[name],
               "question_mark_cells_selected_by_mask":question_mark_masked,
               "total_masked_cells":int(mask.sum()),
            }
    # Frozen pre-outcome sample for independent exact law reference review.
    # Sorted training IDs positions 0..9, Adult occupation, n=10,k=2.
    positions=list(range(10))
    sample_row_ids=[ids["train"][j] for j in positions]
    z_small=train_z[positions]
    weights=probabilities(z_small,0.20)
    check(len(weights)==10 and np.isfinite(weights).all(),"small weights")
    small={
      "status":"FROZEN_INPUTS_ONLY; INDEPENDENT_REFERENCE_VERIFICATION_PENDING",
      "selected_train_index_positions_zero_based":positions,
      "raw_row_ids_one_based":sample_row_ids,
      "feature":"occupation","n":10,"k":2,"rate":0.20,
      "anchor_standardized_values":[float(v) for v in z_small],
      "clipped_logistic_weights":[float(v) for v in weights],
      "unordered_mask_category_count":45,
      "weight_convention":"Plackett-Luce sequential weighted selection summed over unordered permutations",
      "provenance_requirement":"independent external reference or human review; same-author implementation insufficient",
    }
    ref_files=[str(SPLIT),str(STATS),str(S003),str(APPROVAL),
               "src/rmti/masking.py","scripts/r002_adult_verify.py"]
    receipt={
      "schema":VERSION,
      "status":"ADULT_INVARIANTS_PASS_IF_SCRIPT_SUCCEEDS; INDEPENDENT_SMALL_N_REFERENCE_PENDING",
      "source_sha256":sha(raw),
      "input_sha256":{p:file_hash(p) for p in ref_files},
      "standardization":{
        "fitted_split":"train only","feature":"age","ddof":0,"dtype":"float64",
        "train_n":len(train_age),"mean":mean,"std":sd,
        "train_standardized_anchor_sha256":sha(train_z.tobytes()),
        "validation_uses_train_mean_std":True,
      },
      "rates_tested":RATES,"seed":SEED,
      "masked_splits":["train","validation"],
      "test_partition_masking":"NOT EXECUTED",
      "question_mark_preserved":qcounts,
      "adult_mask_checks":checks,"small_exact_law_reference_inputs":small,
      "models_trained":False,"pilot_executed":False,
      "independent_sampling_law_status":"PENDING",
    }
    encoded=(json.dumps(receipt,sort_keys=True,indent=2)+"\n").encode("utf-8")
    if OUT.exists() and OUT.read_bytes()!=encoded:
        raise RuntimeError("R002 receipt exists and differs; no overwrite")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(encoded)
    print("R002 ADULT INVARIANT CHECKS PASS. Independent small-n law review remains PENDING.")
    print("TRAIN AGE MEAN:",mean,"SD:",sd,"TRAIN STANDARDIZED AGE SHA256:",sha(train_z.tobytes()))
    print("RECEIPT SHA256:",sha(encoded))
    print("Receipt path:",OUT)
if __name__=="__main__":
    main()
