"""Compatibility checks for the pre-existing experimental namespace.

These imports and sanity tests do not validate MAR research claims.
"""
import numpy as np
import pandas as pd

from rmti.masking import generate_mask, stable_seed
from rmti.schema import FIELDS, validate


def test_legacy_mcar_repeatable_fixed_count():
    frame = pd.DataFrame({"x": np.arange(10)})
    m1 = generate_mask(frame, ["x"], "MCAR", rate=0.3, seed=7)
    m2 = generate_mask(frame, ["x"], "MCAR", rate=0.3, seed=7)
    assert m1.shape == (10, 1)
    assert m1.dtype == np.dtype("bool")
    assert m1.sum() == 3
    assert np.array_equal(m1, m2)


def test_legacy_seed_determinism():
    assert stable_seed(5, "x") == stable_seed(5, "x")
    assert stable_seed(5, "x") != stable_seed(5, "y")


def test_legacy_schema_contract():
    record = {name: None for name in FIELDS}
    record.update(split="train", mechanism="MCAR", accepted_flag=False)
    assert validate([record]) is True
