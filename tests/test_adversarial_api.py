"""Adversarial public API tests derived from conditional external review C1-C5."""
import numpy as np
import pandas as pd
import pytest
from reliable_masked_tabular_imputation import make_mcar_mask, apply_mask, masked_mae, masked_rmse


def test_global_budget_and_original_nulls():
    frame = pd.DataFrame({"a": [1., 2., 3., 4.], "b": [np.nan, np.nan, np.nan, 5.]})
    mask = make_mcar_mask(frame, 0.5, random_state=0)
    assert int(mask.to_numpy().sum()) == 2
    assert not mask.iloc[:3, 1].any()
    assert mask.shape == frame.shape


def test_seeded_sampling_invariants_across_sizes():
    for rows in (0, 1, 4, 23):
        frame = pd.DataFrame({"x": np.arange(rows, dtype=float),
                              "y": np.arange(rows, dtype=float)})
        if rows:
            frame.loc[0, "y"] = np.nan
        for rate in (0, .1, .5, 1):
            mask = make_mcar_mask(frame, rate, random_state=91)
            eligible = frame.notna().to_numpy()
            assert int(mask.to_numpy().sum()) == int(np.floor(rate * eligible.sum()))
            assert not np.logical_and(mask.to_numpy(), ~eligible).any()
            assert mask.equals(make_mcar_mask(frame, rate, random_state=91))


@pytest.mark.parametrize("dtype,values", [
    ("Int64", [1, 2, 3]),
    ("Float64", [1., 2., 3.]),
    ("boolean", [True, False, True]),
    ("string", ["a", "b", "c"]),
    ("category", ["a", "b", "a"]),
])
def test_nullable_and_categorical_dtype_preservation(dtype, values):
    frame = pd.DataFrame({"x": pd.Series(values, dtype=dtype)})
    mask = pd.DataFrame({"x": [False, True, False]})
    out = apply_mask(frame, mask)
    assert str(out.dtypes["x"]) == str(frame.dtypes["x"])
    assert bool(pd.isna(out.loc[1, "x"]))
    assert not pd.isna(frame.loc[1, "x"])


def test_plain_int_dtype_promotes_when_masked():
    frame = pd.DataFrame({"x": [1, 2, 3]})
    mask = pd.DataFrame({"x": [False, True, False]})
    out = apply_mask(frame, mask)
    assert pd.api.types.is_float_dtype(out["x"])
    assert pd.isna(out.loc[1, "x"])


def test_multiindex_axes_and_tuple_columns():
    index = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1)])
    columns = pd.MultiIndex.from_tuples([("x", "one"), ("x", "two")])
    frame = pd.DataFrame([[1., 2.], [3., 4.], [5., 6.]], index=index, columns=columns)
    mask = make_mcar_mask(frame, 0.5, random_state=4)
    assert mask.index.equals(frame.index)
    assert mask.columns.equals(frame.columns)
    assert int(apply_mask(frame, mask).isna().to_numpy().sum()) == 3


def test_invalid_or_missing_selected_values():
    truth = pd.DataFrame({"x": [1.0, np.nan]})
    pred = pd.DataFrame({"x": [0.0, 0.0]})
    mask = pd.DataFrame({"x": [False, True]})
    with pytest.raises(ValueError, match="finite"):
        masked_mae(truth, pred, mask)


def test_overflow_on_subtraction_rejected():
    truth = pd.DataFrame({"x": [1e308]})
    pred = pd.DataFrame({"x": [-1e308]})
    mask = pd.DataFrame({"x": [True]})
    with pytest.raises(ValueError, match="overflow"):
        masked_mae(truth, pred, mask)
    with pytest.raises(ValueError, match="overflow"):
        masked_rmse(truth, pred, mask)


def test_large_finite_errors_do_not_spuriously_overflow_rmse():
    truth = pd.DataFrame({"x": [0., 0.]})
    pred = pd.DataFrame({"x": [1e200, 1e200]})
    mask = pd.DataFrame({"x": [True, True]})
    assert masked_rmse(truth, pred, mask) == pytest.approx(1e200)
    assert masked_mae(truth, pred, mask) == pytest.approx(1e200)


def test_missing_boolean_mask_rejected():
    frame = pd.DataFrame({"x": [1., 2.]})
    mask = pd.DataFrame({"x": pd.Series([True, pd.NA], dtype="boolean")})
    with pytest.raises(ValueError, match="missing"):
        apply_mask(frame, mask)
