"""Stage 1 live competitor API probe. Exploratory, NOT a matched benchmark.
Run in separate clean GitHub Actions environments; records structured failures.
"""
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

competitor = sys.argv[1]
outdir = Path("competitor-results")
outdir.mkdir(exist_ok=True)
report = {
    "competitor": competitor,
    "status": "IN_PROGRESS",
    "scope": "Initial real-install/API trial, not matched 10k×20 benchmark or v0.2 differentiation evidence",
    "python": sys.version,
    "platform": platform.platform(),
    "checks": {},
    "limitations": [
        "Synthetic numeric data only; no verified real dataset.",
        "Native comparator protocols may not match the external train-only fitting contract.",
        "No human-observed setup or documentation reading time."
    ],
}
def check(name, fn):
    t0 = time.perf_counter()
    try:
        result = fn()
        report["checks"][name] = {"status": "PASS", "seconds": time.perf_counter()-t0, "result": result}
    except Exception as exc:
        report["checks"][name] = {"status": "FAIL", "seconds": time.perf_counter()-t0,
                                   "exception": repr(exc), "traceback": traceback.format_exc()[-8000:]}
        print("FAIL", name, repr(exc), flush=True)

def package_versions():
    return {p: importlib.metadata.version(p) for p in ["numpy","pandas","scikit-learn", "qolmat" if competitor=="qolmat" else "missmecha-py"]}

check("installed_versions", package_versions)
rng = np.random.default_rng(4201)
latent = rng.normal(size=(400,3))
data = latent @ rng.normal(size=(3,6)) + rng.normal(scale=0.2,size=(400,6))
data[rng.random(data.shape)<0.05]=np.nan
frame = pd.DataFrame(data, columns=[f"f{x}" for x in range(6)])
train_id, test_id = train_test_split(np.arange(400), test_size=0.2, random_state=71)
train = frame.iloc[train_id].copy()
test = frame.iloc[test_id].copy()
observed = test.notna().to_numpy()
mask = np.zeros(test.shape, dtype=bool)
elig = np.flatnonzero(observed.ravel())
chosen = np.random.default_rng(115).choice(elig, size=int(0.2*len(elig)), replace=False)
mask.flat[chosen]=True
masked = test.mask(mask)
assert not np.any(mask & ~observed)
report["contract"] = {
    "split_first": True,
    "fit_scope": "train_only for custom evaluation (native library comparison audited separately)",
    "train_rows": len(train), "test_rows": len(test),
    "natural_missing_test": int((~observed).sum()),
    "artificially_hidden_test": int(mask.sum()),
    "mask_sha256": hashlib.sha256(mask.astype("u1").tobytes()).hexdigest(),
    "train_id_sha256": hashlib.sha256(np.sort(train_id).astype("<i8").tobytes()).hexdigest(),
    "test_id_sha256": hashlib.sha256(np.sort(test_id).astype("<i8").tobytes()).hexdigest(),
}

class CustomMedian:
    """External user imputer, standard fit/transform, no sklearn inheritance."""
    def fit(self, X):
        self.v = np.nanmedian(np.asarray(X, dtype=float), axis=0)
        self.fitted_n = len(X)
        return self
    def transform(self, X):
        a = np.asarray(X, dtype=float).copy()
        i,j = np.where(np.isnan(a))
        a[i,j] = self.v[j]
        return a

def custom_train_only():
    imputer = CustomMedian().fit(train)
    assert imputer.fitted_n == len(train)
    pred = imputer.transform(masked)
    actual = test.to_numpy()[mask]
    err = pred[mask]-actual
    return {"rmse": float(np.sqrt(np.mean(err*err))), "n": len(actual),
            "custom_imputer_fit_transform": True}
check("custom_imputer_baseline", custom_train_only)

if competitor == "qolmat":
    def native_comparator():
        from qolmat.benchmark import comparator, missing_patterns
        from qolmat.imputations import imputers
        generator = missing_patterns.UniformHoleGenerator(n_splits=2, ratio_masked=0.2)
        compare = comparator.Comparator(
            {"median_qolmat": imputers.ImputerSimple(strategy="median")},
            generator_holes=generator, metrics=["mae"]
        )
        # This is the library's documented-style comparator, NOT train-only eval.
        comparison = compare.compare(frame.copy())
        return {"comparison_type": type(comparison).__name__,
                "comparison": comparison.to_string()[:3000]}
    check("native_comparator", native_comparator)
    class QolmatCustomMedian(CustomMedian):
        """Documented adapter: qolmat expects fit_transform and labelled DataFrames."""
        def transform(self, X):
            result = super().transform(X)
            return pd.DataFrame(result, index=X.index, columns=X.columns)
        def fit_transform(self, X, y=None):
            return self.fit(X).transform(X)
    def native_custom():
        from qolmat.benchmark import comparator, missing_patterns
        compare = comparator.Comparator(
            {"custom_median": QolmatCustomMedian()},
            generator_holes=missing_patterns.UniformHoleGenerator(n_splits=2,ratio_masked=0.2),
            metrics=["mae"]
        )
        comparison = compare.compare(frame.copy())
        return {"comparison": comparison.to_string()[:3000]}
    check("native_custom_imputer", native_custom)
elif competitor == "missmecha":
    def native_generator():
        from missmecha import MissMechaGenerator
        gen = MissMechaGenerator(mechanism="mcar",mechanism_type=1,missing_rate=0.2,seed=115)
        generated = gen.fit_transform(test.copy())
        generated = np.asarray(generated, dtype=float)
        newly_missing = np.isnan(generated)&observed
        return {"shape": list(generated.shape), "new_masked_observed": int(newly_missing.sum()),
                "original_nan_preserved": bool(np.isnan(generated[~observed]).all())}
    check("native_generator", native_generator)
else:
    raise ValueError(f"Unknown competitor: {competitor}")

report["status"] = "PASS" if all(v["status"]=="PASS" for v in report["checks"].values()) else "PARTIAL_OR_FAILED"
(outdir/f"{competitor}_results.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2),flush=True)
sys.exit(0 if report["status"]=="PASS" else 1)
