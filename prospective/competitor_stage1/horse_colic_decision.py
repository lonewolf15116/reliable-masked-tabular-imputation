"""Real-data decision trial. Exploratory competitor integrations; no v0.2 code."""
import datetime as dt
import hashlib
import importlib.metadata as md
import json
import sys
import time
import traceback
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/horse-colic/horse-colic.data"
SEEDS = (11, 23, 37, 53, 71)
COLS_ONE_INDEXED = (4, 5, 6, 16, 19, 20, 22)
NAMES = ("rectal_temperature","pulse","respiratory_rate","reflux_ph","packed_cell_volume","total_protein","abdominocentesis_protein")
OUT = Path("decision-results")
OUT.mkdir(exist_ok=True)
competitor = sys.argv[1]
report = {"competitor": competitor, "status": "RUNNING", "source_url": URL,
          "contract": "split first; train-only fit; fixed artificial test masks; per-feature scores",
          "not_matched": [], "errors": [], "seeds": [], "started_utc": dt.datetime.now(dt.timezone.utc).isoformat()}

def write():
    (OUT/f"{competitor}_decision_results.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
def digest(b):
    return hashlib.sha256(b).hexdigest()

class CustomMedian:
    def fit(self, frame):
        self.values = np.nanmedian(np.asarray(frame,dtype=float),axis=0)
        self.n_fit_rows = len(frame)
        return self
    def transform(self, frame):
        arr = np.asarray(frame,dtype=float).copy()
        r,c=np.where(np.isnan(arr))
        arr[r,c]=self.values[c]
        return pd.DataFrame(arr,index=frame.index,columns=frame.columns)
    def fit_transform(self, frame, y=None):
        return self.fit(frame).transform(frame)

def get_data():
    with urllib.request.urlopen(URL, timeout=30) as h:
        raw=h.read()
    (OUT/"horse-colic.data").write_bytes(raw)
    report["dataset"]={"sha256":digest(raw),"bytes":len(raw),
        "download_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_file":"horse-colic.data"}
    df=pd.read_csv(OUT/"horse-colic.data",sep=r"\s+",header=None,na_values=["?"],engine="python")
    if len(df)!=300 or df.shape[1]!=28:
        raise AssertionError(f"Unexpected source geometry {df.shape}")
    x=df.iloc[:,[i-1 for i in COLS_ONE_INDEXED]].apply(pd.to_numeric,errors="raise")
    x.columns=NAMES
    report["dataset"].update({"raw_shape":list(df.shape),"selected_shape":list(x.shape),
        "natural_missing_per_feature":x.isna().sum().astype(int).to_dict()})
    return x

def errors_per_column(truth,pred,mask):
    scores={}
    for c in truth.columns:
        eligible=mask[c].to_numpy(dtype=bool)
        if not eligible.any():
            scores[c]={"n":0,"mae":None,"rmse":None}
            continue
        delta=pred.loc[eligible,c].to_numpy(dtype=float)-truth.loc[eligible,c].to_numpy(dtype=float)
        scores[c]={"n":len(delta),"mae":float(np.mean(abs(delta))),"rmse":float(np.sqrt(np.mean(delta*delta)))}
    return scores

def fixed_trials(x):
    for seed in SEEDS:
        train_id,test_id=train_test_split(np.arange(len(x)),test_size=0.2,random_state=seed)
        train=x.iloc[train_id].copy()
        test=x.iloc[test_id].copy()
        eligible=test.notna().to_numpy()
        rng=np.random.default_rng(seed*100+7)
        positions=np.flatnonzero(eligible.ravel())
        chosen=rng.choice(positions,size=int(np.floor(0.2*len(positions))),replace=False)
        mask_np=np.zeros(test.shape,dtype=bool)
        mask_np.flat[chosen]=True
        mask=pd.DataFrame(mask_np,index=test.index,columns=test.columns)
        fit=CustomMedian().fit(train)
        if fit.n_fit_rows!=len(train): raise AssertionError("Training fit contamination")
        pred=fit.transform(test.mask(mask))
        if not np.isfinite(pred.to_numpy()[mask_np]).all(): raise AssertionError("Nonfinite scored prediction")
        row={"seed":seed,"train_rows":len(train),"test_rows":len(test),
             "mask_sha256":digest(mask_np.astype("u1").tobytes()),
             "train_split_sha256":digest(np.sort(train_id).astype("<i8").tobytes()),
             "test_split_sha256":digest(np.sort(test_id).astype("<i8").tobytes()),
             "artificial_masks_total":int(mask_np.sum()),
             "per_feature_masks":mask.sum().astype(int).to_dict(),
             "per_feature_realized_mask_fraction_of_observed":
             {c:float(mask[c].sum()/max(1,test[c].notna().sum())) for c in test.columns},
             "per_feature_metric":errors_per_column(test,pred,mask)}
        report["seeds"].append(row)
        yield train,test,mask,row

def run_native_qolmat(x):
    from qolmat.benchmark import comparator,missing_patterns
    from qolmat.imputations import imputers
    generator=missing_patterns.UniformHoleGenerator(n_splits=2,ratio_masked=0.2)
    # Limited to native feature/API check. Not the matched split-first test.
    cmp=comparator.Comparator({"native_qolmat_median":imputers.ImputerSimple(strategy="median")},
                              generator_holes=generator,metrics=["mae"])
    t=time.perf_counter()
    result=cmp.compare(x.copy())
    report["native_check"]={"status":"PASS","seconds":time.perf_counter()-t,
                             "shape":list(result.shape),"columns":list(map(str,result.columns))}
    report["not_matched"].append("qolmat native Comparator refits by its own hole-generator/split protocol; not identical to external train-only fitted test masks.")

def run_native_missmecha(test):
    from missmecha import MissMechaGenerator
    gen=MissMechaGenerator(mechanism="mcar",mechanism_type=1,missing_rate=0.2,seed=115)
    original=test.copy()
    result=np.asarray(gen.fit_transform(original),dtype=float)
    if result.shape!=test.shape: raise AssertionError("Unexpected generated shape")
    if not np.isnan(result[test.isna().to_numpy()]).all(): raise AssertionError("Original NaNs lost")
    report["native_check"]={"status":"PASS","generated_shape":list(result.shape),
                           "newly_masked_observed":int((np.isnan(result)&test.notna().to_numpy()).sum())}
    report["not_matched"].append("MissMecha native generator uses own mask, not fixed test mask; external train-only evaluator supplies matched metrics.")

try:
    x=get_data()
    t=time.perf_counter()
    trials=list(fixed_trials(x))
    report["external_reference"]={"status":"PASS","seconds":time.perf_counter()-t,
                                  "seeds":len(trials),"method":"custom median, train-only fit"}
    if competitor=="qolmat":
        run_native_qolmat(x)
        report["custom_imputer_adaptation"]={"adapter_extra_lines":0,"note":"CustomMedian already provides fit_transform and returns labelled DataFrame; no library patch"}
    elif competitor=="missmecha":
        run_native_missmecha(trials[0][1])
    elif competitor=="baseline":
        report["native_check"]={"status":"NOT_APPLICABLE"}
    else:
        raise ValueError(competitor)
    report["status"]="PASS_WITH_MATCHING_LIMITATIONS"
except BaseException as exc:
    report["status"]="FAIL"
    report["errors"].append({"exception":repr(exc),"traceback":traceback.format_exc()})
finally:
    report["finished_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    report["versions"]={}
    for package in ("numpy","pandas","scikit-learn","qolmat","missmecha-py"):
        try: report["versions"][package]=md.version(package)
        except md.PackageNotFoundError: pass
    write()
    print(json.dumps({"status":report["status"],"competitor":competitor,
          "dataset":report.get("dataset"),"error":report["errors"],"native":report.get("native_check"),
          "seed_count":len(report["seeds"]),"not_matched":report["not_matched"]},indent=2))
    if report["status"]=="FAIL":sys.exit(1)
