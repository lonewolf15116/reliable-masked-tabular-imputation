"""Metrics restricted to artificially hidden numeric cells."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _masked_errors(truth: pd.DataFrame, imputed: pd.DataFrame, mask: pd.DataFrame) -> np.ndarray:
    for name, obj in (("truth", truth), ("imputed", imputed), ("mask", mask)):
        if not isinstance(obj, pd.DataFrame):
            raise TypeError(f"{name} must be a pandas DataFrame")
    if not truth.index.equals(imputed.index) or not truth.columns.equals(imputed.columns):
        raise ValueError("truth and imputed axes must match exactly")
    if not truth.index.equals(mask.index) or not truth.columns.equals(mask.columns):
        raise ValueError("mask axes must match truth exactly")
    if not all(pd.api.types.is_bool_dtype(dtype) for dtype in mask.dtypes):
        raise TypeError("mask must be boolean")
    if mask.isna().to_numpy().any():
        raise ValueError("mask cannot contain missing values")
    selected = mask.to_numpy(dtype=bool)
    if not selected.any():
        raise ValueError("mask has no selected cells")
    # Convert only selected cells; unrelated categorical columns may coexist.
    truth_values = truth.to_numpy(dtype=object)[selected]
    pred_values = imputed.to_numpy(dtype=object)[selected]
    try:
        actual = np.asarray(truth_values, dtype=float)
        predicted = np.asarray(pred_values, dtype=float)
    except (ValueError, TypeError) as exc:
        raise TypeError("selected truth and imputed cells must be numeric") from exc
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("selected cells must contain finite numeric values")
    return predicted - actual


def masked_mae(truth: pd.DataFrame, imputed: pd.DataFrame, mask: pd.DataFrame) -> float:
    """Mean absolute error on hidden numeric cells only."""
    return float(np.abs(_masked_errors(truth, imputed, mask)).mean())


def masked_rmse(truth: pd.DataFrame, imputed: pd.DataFrame, mask: pd.DataFrame) -> float:
    """Root mean squared error on hidden numeric cells only."""
    errors = _masked_errors(truth, imputed, mask)
    return float(np.sqrt(np.mean(np.square(errors))))
