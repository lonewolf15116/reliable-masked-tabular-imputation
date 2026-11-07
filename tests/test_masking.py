import numpy as np
import pandas as pd
import pytest
from rmti.masking import generate_mask

@pytest.fixture
def toy():
    return pd.DataFrame({'age':[20,30,40,50,60], 'salary':[1,2,3,4,5], 'city':['a','b','c','d','e'], 'income':[0,1,0,1,0]})

def test_deterministic_and_count(toy):
    a = generate_mask(toy,['salary','city'],'MCAR',.2,42)
    assert np.array_equal(a,generate_mask(toy,['salary','city'],'MCAR',.2,42))
    assert a.shape == (5,2) and a.sum() == 2

def test_mar_driver_never_masked(toy):
    a = generate_mask(toy,['salary','city'],'MAR',.2,42,anchor_data=toy[['age']])
    assert a.sum() == 2
    with pytest.raises(ValueError):
        generate_mask(toy,['age','city'],'MAR',.2,42,anchor_data=toy[['age']])

def test_invalid_inputs(toy):
    with pytest.raises(ValueError):
        generate_mask(toy,['salary'],'MCAR',1.0,1)
    with pytest.raises(ValueError):
        generate_mask(toy,['missing'],'MCAR',.2,1)
