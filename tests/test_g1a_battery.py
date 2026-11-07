import os, subprocess, sys
import numpy as np
import pandas as pd
import pytest
from rmti.masking import generate_mask, probabilities

F = pd.DataFrame({'anchor':np.linspace(-2,2,15),'a':np.arange(15),'b':np.arange(15)*2,'c':np.arange(15)*3,'target':np.arange(15)%2})
FEATURES=['a','b','c']

def run(mechanism='MCAR',seed=17,rate=.2):
    return generate_mask(F,FEATURES,mechanism,rate,seed,anchor_data=F[['anchor']] if mechanism=='MAR' else None)

def test_golden_toy():
    import pathlib
    p=pathlib.Path(__file__).parent/'golden_mask_mcar_seed17.csv'
    expected=np.loadtxt(p,delimiter=',',dtype=int)
    np.testing.assert_array_equal(run().astype(int),expected)

def test_structural_driver_exclusion():
    base=run('MAR')
    altered=F.copy(); altered['a']=999999; altered['b']=-123
    np.testing.assert_array_equal(base,generate_mask(altered,FEATURES,'MAR',.2,17,anchor_data=F[['anchor']]))
    with pytest.raises(ValueError): generate_mask(F,FEATURES,'MAR',.2,17,anchor_data=F[['a']])

def test_per_feature_counts():
    for mechanism in ('MCAR','MAR'):
        for rate in (.1,.2,.3):
            m=run(mechanism,rate=rate)
            assert np.all(m.sum(axis=0)==int(np.floor(rate*len(F)+.5)))

def test_target_never_masked():
    for seed in range(100):
        for mechanism in ('MCAR','MAR'):
            assert 'target' not in FEATURES
            assert run(mechanism,seed=seed).shape==(len(F),len(FEATURES))

def test_cross_process_determinism():
    code="import pandas as pd,numpy as np;from rmti.masking import generate_mask;f=pd.DataFrame({'x':range(15)});print(generate_mask(f,['x'],'MCAR',.2,17).astype(int).ravel().tolist())"
    env={**os.environ,'PYTHONHASHSEED':'random'}
    a=subprocess.check_output([sys.executable,'-c',code],env=env)
    env['PYTHONHASHSEED']='123'
    b=subprocess.check_output([sys.executable,'-c',code],env=env)
    assert a==b

def test_clipping_numerical_safety():
    p=probabilities(np.array([-1e6,0,1e6]),.2)
    assert np.isfinite(p).all() and np.all((p>=.01)&(p<=.99))
    assert abs(p.mean()-.2)<1e-9
