import numpy as np
import pandas as pd
import pytest

from reliable_masked_tabular_imputation import (
    apply_mask,
    make_mcar_mask,
    masked_mae,
    masked_rmse,
)


def test_exact_budget_repeatability_and_no_mutation():
    frame = pd.DataFrame({"a": range(10), "b": range(10, 20)})
    original = frame.copy(deep=True)
    first = make_mcar_mask(frame, 0.35, random_state=123)
    second = make_mcar_mask(frame, 0.35, random_state=123)
    assert first.equals(second)
    assert first.to_numpy().sum() == 7
    assert frame.equals(original)
    masked = apply_mask(frame, first)
    assert masked.isna().to_numpy().sum() == 7
    assert frame.equals(original)


def test_preexisting_nulls_and_column_selection():
    frame = pd.DataFrame({"a": [1, np.nan, 3, 4], "b": [10, 11, 12, 13]})
    mask = make_mcar_mask(frame, 1, columns=["a"])
    assert mask["a"].tolist() == [True, False, True, True]
    assert not mask["b"].any()
    assert apply_mask(frame, mask).isna().to_numpy().sum() == 4


def test_metrics_only_evaluate_hidden_cells():
    truth = pd.DataFrame({"x": [1, 2, 3], "note": ["a", "b", "c"]})
    predicted = pd.DataFrame({"x": [2, 4, 999], "note": ["z", "z", "z"]})
    mask = pd.DataFrame({"x": [True, True, False], "note": [False] * 3})
    assert masked_mae(truth, predicted, mask) == pytest.approx(1.5)
    assert masked_rmse(truth, predicted, mask) == pytest.approx(np.sqrt(2.5))


def test_invalid_inputs_fail_loudly():
    frame = pd.DataFrame({"x": [1, 2, 3]})
    for rate in [-0.1, 1.1, float("nan")]:
        with pytest.raises(ValueError):
            make_mcar_mask(frame, rate)
    with pytest.raises(KeyError):
        make_mcar_mask(frame, 0.5, columns=["absent"])
    with pytest.raises(ValueError):
        apply_mask(frame, pd.DataFrame({"other": [True, False, False]}))
    with pytest.raises(ValueError):
        masked_mae(frame, frame, pd.DataFrame({"x": [False] * 3}))
    with pytest.raises(ValueError):
        masked_rmse(frame, frame, pd.DataFrame({"x": [True, False]}, index=[0, 1]))
