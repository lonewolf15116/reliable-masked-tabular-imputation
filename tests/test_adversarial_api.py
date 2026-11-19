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


def test_plain_int_dtype_converts_to_nullable_without_precision_loss():
    frame = pd.DataFrame({"x": [1, 2, 3]})
    mask = pd.DataFrame({"x": [False, True, False]})
    out = apply_mask(frame, mask)
    assert str(out["x"].dtype) == "Int64"
    assert pd.isna(out.loc[1, "x"])
    assert frame["x"].tolist() == [1, 2, 3]


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


@pytest.mark.parametrize("dtype,values,expected_dtype", [
    ("int64", [2**63 - 1, 2**63 - 2, 2**63 - 3], "Int64"),
    ("uint64", [2**64 - 1, 2**64 - 2, 2**64 - 3], "UInt64"),
    ("Int64", [2**63 - 1, 2**63 - 2, 2**63 - 3], "Int64"),
    ("UInt64", [2**64 - 1, 2**64 - 2, 2**64 - 3], "UInt64"),
])
def test_masking_preserves_unmasked_integer_boundaries(dtype, values, expected_dtype):
    frame = pd.DataFrame({"x": pd.Series(values, dtype=dtype), "note": ["a", "b", "c"]})
    original = frame.copy(deep=True)
    mask = pd.DataFrame({"x": [False, False, True], "note": [False] * 3})
    out = apply_mask(frame, mask)
    assert str(out["x"].dtype) == expected_dtype
    assert int(out.loc[0, "x"]) == values[0]
    assert int(out.loc[1, "x"]) == values[1]
    assert pd.isna(out.loc[2, "x"])
    assert out["note"].tolist() == ["a", "b", "c"]
    pd.testing.assert_frame_equal(frame, original)
    pd.testing.assert_frame_equal(mask, pd.DataFrame({"x": [False, False, True], "note": [False] * 3}))


@pytest.mark.parametrize("dtype,values", [
    ("int64", [2**63 - 1, 2**63 - 2]),
    ("uint64", [2**64 - 1, 2**64 - 2]),
    ("Int64", [2**63 - 1, 2**63 - 2]),
    ("UInt64", [2**64 - 1, 2**64 - 2]),
])
def test_scoring_rejects_integer_boundary_precision_loss(dtype, values):
    actual = pd.DataFrame({"x": pd.Series([values[0]], dtype=dtype)})
    predicted = pd.DataFrame({"x": pd.Series([values[1]], dtype=dtype)})
    mask = pd.DataFrame({"x": [True]})
    before_actual, before_pred = actual.copy(deep=True), predicted.copy(deep=True)
    for scorer in (masked_mae, masked_rmse):
        with pytest.raises(ValueError, match="exactness boundary"):
            scorer(actual, predicted, mask)
    pd.testing.assert_frame_equal(actual, before_actual)
    pd.testing.assert_frame_equal(predicted, before_pred)


@pytest.mark.parametrize("actual,predicted,raises", [
    (2**53, 2**53 - 1, False),
    (-(2**53), -(2**53) + 1, False),
    (2**53 + 1, 2**53, True),
    (-(2**53) - 1, -(2**53), True),
])
def test_metric_integer_exactness_boundary(actual, predicted, raises):
    truth = pd.DataFrame({"x": pd.Series([actual], dtype=object)})
    estimate = pd.DataFrame({"x": pd.Series([predicted], dtype=object)})
    mask = pd.DataFrame({"x": [True]})
    for scorer in (masked_mae, masked_rmse):
        if raises:
            with pytest.raises(ValueError, match="exactness boundary"):
                scorer(truth, estimate, mask)
        else:
            assert scorer(truth, estimate, mask) == pytest.approx(1)


def test_nonfinite_eligibility_and_scoring_policy():
    frame = pd.DataFrame({"x": pd.Series([np.nan, np.inf, -np.inf, 3.0], dtype="Float64"),
                          "y": pd.Series([pd.NA, 2.0, 3.0, 4.0], dtype="Float64")})
    mask = make_mcar_mask(frame, 1.0, random_state=10)
    assert mask["x"].tolist() == [False, True, True, True]
    assert mask["y"].tolist() == [False, True, True, True]
    for scorer in (masked_mae, masked_rmse):
        with pytest.raises(ValueError, match="finite"):
            scorer(frame[["x"]], frame[["x"]], mask[["x"]])


def test_mixed_columns_keep_nonselected_dtypes_and_input_immutability():
    frame = pd.DataFrame({
        "big": pd.Series([2**63 - 1, 2**63 - 2], dtype="int64"),
        "category": pd.Categorical(["a", "b"]),
        "nullable": pd.Series([1, pd.NA], dtype="Int64"),
    })
    before = frame.copy(deep=True)
    mask = pd.DataFrame({"big": [True, False], "category": [False, False], "nullable": [False, False]})
    out = apply_mask(frame, mask)
    assert int(out.loc[1, "big"]) == 2**63 - 2
    assert str(out["big"].dtype) == "Int64"
    assert str(out["nullable"].dtype) == "Int64"
    assert str(out["category"].dtype) == "category"
    pd.testing.assert_frame_equal(frame, before)
