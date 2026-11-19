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
    # Validate selected scalar types before coercion: Decimal/Fraction and
    # arbitrary object-backed values are outside the float64 scoring contract.
    for value in (*truth_values, *pred_values):
        if not isinstance(value, (bool, np.bool_, int, np.integer, float, np.floating)):
            raise TypeError("selected cells must use supported Python/NumPy numeric scalar types")
        if isinstance(value, np.floating) and np.dtype(type(value)).itemsize > 8:
            raise TypeError("selected extended-precision floats are not supported")
        # float64 represents all integer values with abs(value) <= 2**53.
        if (isinstance(value, (int, np.integer))
                and not isinstance(value, (bool, np.bool_))
                and abs(int(value)) > 2**53):
            raise ValueError("selected integer exceeds float64 exactness boundary (abs(value) > 2**53)")
    try:
        actual = np.asarray(truth_values, dtype=float)
        predicted = np.asarray(pred_values, dtype=float)
    except (ValueError, TypeError) as exc:
        raise TypeError("selected truth and imputed cells must be numeric") from exc
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("selected cells must contain finite numeric values")
    with np.errstate(over="ignore", invalid="ignore"):
        errors = predicted - actual
    if not np.isfinite(errors).all():
        raise ValueError("numeric overflow when computing masked-cell errors")
    return errors


def masked_mae(truth: pd.DataFrame, imputed: pd.DataFrame, mask: pd.DataFrame) -> float:
    """Mean absolute error on hidden numeric cells only.

    Raise ValueError for selected integer values with abs(value) > 2**53,
    since conversion to float64 may silently lose integer precision.
    """
    errors = np.abs(_masked_errors(truth, imputed, mask))
    # A mean of finite errors is finite; scaled sum avoids accumulator overflow.
    scale = float(np.max(errors))
    if scale == 0.0:
        return 0.0
    return float(np.mean(errors / scale) * scale)


def masked_rmse(truth: pd.DataFrame, imputed: pd.DataFrame, mask: pd.DataFrame) -> float:
    """Root mean squared error on hidden numeric cells only.

    Raise ValueError for selected integer values with abs(value) > 2**53,
    since conversion to float64 may silently lose integer precision.
    """
    errors = _masked_errors(truth, imputed, mask)
    scale = float(np.max(np.abs(errors)))
    if scale == 0.0:
        return 0.0
    # Scale first so squaring large-but-finite errors cannot overflow.
    return float(np.sqrt(np.mean(np.square(errors / scale))) * scale)
