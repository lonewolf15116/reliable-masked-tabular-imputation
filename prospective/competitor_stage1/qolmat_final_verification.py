"""Final, narrow qolmat 0.2.0 reproduction. No RMTI API or dependency changes."""
import hashlib
import inspect
import json
import time
import traceback
from pathlib import Path
import numpy as np
import pandas as pd
from qolmat.benchmark import missing_patterns, comparator
from qolmat.imputations import imputers

O=Path("qolmat-final-results");O.mkdir(exist_ok=True)
out={"library":"qolmat","version":"0.2.0","cases":[],"source_inspection":{},"workaround":{}}
def record(case, fn):
    start=time.perf_counter()
    try:
        result=fn()
        out["cases"].append({"case":case,"status":"PASS","elapsed_seconds":time.perf_counter()-start,"result":result})
    except Exception as e:
        out["cases"].append({"case":case,"status":"FAIL","elapsed_seconds":time.perf_counter()-start,"error":repr(e),"trace":traceback.format_exc()[-3000:]})
def gen(n=100, present=10, seed=37):
    x=np.arange(n,dtype=float)
    a=np.full(n,np.nan)
    a[np.random.default_rng(seed).choice(n,present,replace=False)]=x[:present]
    b=np.linspace(0,10,n)
    return pd.DataFrame({"sparse":a,"complete":b})
def trial(n=100,present=10,rate=.2,splits=1):
    df=gen(n,present)
    hole=missing_patterns.UniformHoleGenerator(n_splits=splits,subset=df.columns,ratio_masked=rate,random_state=np.random.RandomState(11))
    mask=hole.split(df)
    return {"rows":n,"observed_sparse":int(df["sparse"].notna().sum()),"requested_n_approximately":int(rate*n),
            "mask_counts":[x.sum().astype(int).to_dict() for x in mask]}

for present in (5,10,19,20,30,90):
    record(f"100rows_observed{present}_rate20_split1",lambda present=present:trial(present=present))
for rate in (.01,.05,.10,.20):
    record(f"100rows_observed10_rate{rate}",lambda rate=rate:trial(present=10,rate=rate))
record("HorseColic_surrogate_300rows_53observed_rate20",lambda:trial(n=300,present=53,rate=.2))
for name, fn in [("UniformHoleGenerator.generate_mask",missing_patterns.UniformHoleGenerator.generate_mask),
                 ("UniformHoleGenerator.split",missing_patterns.UniformHoleGenerator.split),
                 ("Comparator.compare",comparator.Comparator.compare)]:
    source=inspect.getsource(fn)
    (O/(name.replace(".","_")+".txt")).write_text(source)
    out["source_inspection"][name]={"sha256":hashlib.sha256(source.encode()).hexdigest(),"source_lines":len(source.splitlines())}
# Demonstrate an externally specified mask can be passed through a PUBLIC generator
# contract. This does not claim train-only fitting; Comparator calls fit_transform internally.
df=gen(100,75)
fixed=np.zeros(df.shape,dtype=bool)
eligible=np.flatnonzero(df.notna().to_numpy().ravel())
chosen=np.random.default_rng(12).choice(eligible,size=10,replace=False)
fixed.flat[chosen]=True
fixed_df=pd.DataFrame(fixed,index=df.index,columns=df.columns)
class SuppliedMaskGenerator(missing_patterns.UniformHoleGenerator):
    def __init__(self,fixed):
        super().__init__(n_splits=1,subset=fixed.columns,ratio_masked=.1)
        self.fixed=fixed
    def split(self,X):
        assert X.index.equals(self.fixed.index) and X.columns.equals(self.fixed.columns)
        assert not (self.fixed.to_numpy()&X.isna().to_numpy()).any()
        return [self.fixed.copy()]
def compare_with_external_mask():
    g=SuppliedMaskGenerator(fixed_df)
    c=comparator.Comparator({"median":imputers.ImputerSimple(strategy="median")},
                            generator_holes=g,metrics=["mae"])
    result=c.compare(df.copy())
    return {"metric_shape":list(result.shape),"value_text":result.to_string(),
            "injection":"public generator_holes argument, subclass override of split",
            "fixed_mask_sha256":hashlib.sha256(fixed.tobytes()).hexdigest(),
            "train_only_fit_enforced":False}
record("external_supplied_mask_generator",compare_with_external_mask)
out["sampling_logic"] = [
    line.strip() for line in inspect.getsource(missing_patterns.UniformHoleGenerator.generate_mask).splitlines()
    if any(term in line for term in ("choice(", "ratio_masked", "n_masked", "n_obs", "notna", "isna", "size=", "indices"))
]
out["interpretation"]=[
 "Generated-mask counts and failures depend on native API choices; never equate with real-world prevalence without proof.",
 "Supplied-mask generator integration is not proof of deployment-style train-only fit.",
 "A subclass is a user-side compatibility adaptation, not built-in fixed-mask support."
]
(O/"qolmat_final_results.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
