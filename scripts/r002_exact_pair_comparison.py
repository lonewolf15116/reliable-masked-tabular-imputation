#!/usr/bin/env python3
"""R002 frozen 45-category generator frequency, marginal and mutation tests.
Uses spec-only reference committed before this sampler comparison.
No model fitting, no test-partition access.
"""
import hashlib
import json
import math
import sys
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
from scipy.stats import chi2
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.rmti.masking import generate_mask, stable_seed

REFERENCE=Path("evidence/R002_SPEC_ONLY_EXACT_PAIR_REFERENCE.json")
OUT=Path("evidence/R002_EXACT_PAIR_COMPARISON_RECEIPT.json")
VERSION="R002-EXACT-PAIR-v1"
TRIALS=12000
GEN_SEED=20261112
MUTANT_SEED=20261113
ALPHA=.01
MARGINAL_ABS_Z_LIMIT=4.0
def sha(x):return hashlib.sha256(x).hexdigest()
def assert_ok(x,msg):
    if not x:raise RuntimeError("R002 exact-pair test FAILED: "+msg)
def chi2_test(obs,prob):
    e=TRIALS*prob
    assert_ok(np.min(e)>=5,"sparse expected counts")
    stat=float(np.sum((obs-e)**2/e))
    return stat,float(chi2.sf(stat,len(obs)-1))
def main():
    ref_bytes=REFERENCE.read_bytes()
    ref=json.loads(ref_bytes)
    assert_ok(ref["status"]=="SPEC_ONLY_REFERENCE_FROZEN_BEFORE_SAMPLER_FREQUENCY_COMPARISON","reference freeze")
    assert_ok(ref["n"]==10 and ref["k"]==2 and ref["feature"]=="occupation","reference config")
    z=np.asarray(ref["z"],dtype=np.float64)
    p=np.asarray([v["probability"] for v in ref["pairs"]],dtype=np.float64)
    marg=np.asarray(ref["marginals"],dtype=np.float64)
    assert_ok(len(p)==45 and abs(float(p.sum())-1)<1e-12,"pair law normalization")
    assert_ok(abs(float(marg.sum())-2)<1e-12,"marginal normalization")
    pairs=[tuple(x["indices"]) for x in ref["pairs"]]
    assert_ok(pairs==[(i,j) for i in range(10) for j in range(i+1,10)],"pair ordering")
    frame=pd.DataFrame({"occupation":["?"]*10})
    anchor=pd.DataFrame({"age":z})
    def sample_generator(seed_start):
        c=Counter()
        for t in range(TRIALS):
            b=generate_mask(frame,["occupation"],"MAR",0.2,seed_start+t,anchor_data=anchor)
            idx=tuple(int(v) for v in np.flatnonzero(b[:,0]))
            assert_ok(len(idx)==2,"fixed-k")
            c[idx]+=1
        return np.array([c[pa] for pa in pairs],dtype=np.int64)
    observed=sample_generator(GEN_SEED)
    statistic,p_value=chi2_test(observed,p)
    empirical_marg=np.array([sum(observed[j] for j,pa in enumerate(pairs) if i in pa)/TRIALS for i in range(10)])
    zscores=np.abs(empirical_marg-marg)/np.sqrt(marg*(1-marg)/TRIALS)
    marginal_pass=bool(np.max(zscores)<MARGINAL_ABS_Z_LIMIT)
    assert_ok(p_value>=ALPHA,"generator chi-square rejects spec law")
    assert_ok(marginal_pass,"generator marginal test fails")
    # Deliberate defect: replace heterogeneous clipped-logistic weights with uniform
    # weights while preserving fixed k=2 and same Gumbel-top-k sampling framework.
    # This targets specifically the failure to use MAR selection weights.
    mutant=Counter()
    for t in range(TRIALS):
        rng=np.random.default_rng(stable_seed(MUTANT_SEED+t,"occupation"))
        u=np.clip(rng.random(10),np.finfo(float).tiny,1-np.finfo(float).eps)
        g=-np.log(-np.log(u))
        idx=tuple(int(v) for v in sorted(np.argpartition(g,-2)[-2:]))
        mutant[idx]+=1
    mutant_observed=np.array([mutant[pa] for pa in pairs],dtype=np.int64)
    mutant_stat,mutant_p=chi2_test(mutant_observed,p)
    mutant_rejected=bool(mutant_p<ALPHA)
    assert_ok(mutant_rejected,"deliberately uniform-weight mutant was not detected")
    record={
      "schema":VERSION,"status":"PASS_IMPLEMENTATION_INDEPENDENT_REFERENCE_AND_MUTATION; NOT_INDEPENDENT_AUTHOR_REVIEW",
      "spec_reference_sha256":sha(ref_bytes),
      "source_generator_sha256":sha(Path("src/rmti/masking.py").read_bytes()),
      "test_script_sha256":sha(Path(__file__).read_bytes()),
      "sample_size_each":TRIALS,"alpha":ALPHA,
      "generator_seed_stream_start":GEN_SEED,"mutant_seed_stream_start":MUTANT_SEED,
      "generator_chi_square":statistic,"generator_p_value":p_value,
      "generator_category_counts":observed.tolist(),
      "expected_category_counts":(p*TRIALS).tolist(),
      "analytic_marginals":marg.tolist(),"empirical_marginals":empirical_marg.tolist(),
      "max_marginal_z_score":float(np.max(zscores)),
      "marginal_z_cutoff":MARGINAL_ABS_Z_LIMIT,
      "mutant":"uniform positive weights instead of A002 clipped-logistic weights; fixed k=2 unchanged",
      "mutant_chi_square":mutant_stat,"mutant_p_value":mutant_p,
      "mutant_rejected":mutant_rejected,
      "independence_scope":"reference frozen before frequency comparison; independently derived from spec, not independent author",
      "models_trained":False,"test_partition_evaluated":False
    }
    b=(json.dumps(record,sort_keys=True,indent=2)+"\n").encode("utf-8")
    if OUT.exists() and OUT.read_bytes()!=b:
        raise RuntimeError("receipt exists and differs; no overwrite")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(b)
    print("R002 SPEC LAW / MARGINALS / MUTANT PASS")
    print("Generator chi-square p:",p_value,"max marginal z:",float(np.max(zscores)))
    print("Defective generator chi-square p:",mutant_p)
    print("REFERENCE SHA256:",sha(ref_bytes),"RECEIPT SHA256:",sha(b))
if __name__=="__main__":main()
