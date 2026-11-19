"""Deterministic, exact-budget MCAR masking for pandas DataFrames."""
from __future__ import annotations

from collections.abc import Sequence
import numpy as np
import pandas as pd


def make_mcar_mask(
    frame: pd.DataFrame,
    rate: float,
    *,
    random_state: int | np.random.Generator = 0,
    columns: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Choose exactly floor(rate * eligible_cells) observed cells uniformly.

    Eligible cells are originally nonmissing cells in selected columns. The
    returned boolean mask is True *only* for newly hidden cells. Selection is
    uniform over eligible cells, not stratified by column; per-column rates
    may differ. The caller's DataFrame is never modified.

    For repeatability, supply an integer seed. A supplied Generator is
    advanced and therefore is not reset between calls.
    """
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")
    if isinstance(rate, (bool, np.bool_)) or not isinstance(rate, (int, float, np.integer, np.floating)):
        raise TypeError("rate must be a real number in [0, 1]")
    if not np.isfinite(rate) or not 0 <= rate <= 1:
        raise ValueError("rate must be finite and in [0, 1]")
    if not frame.columns.is_unique or not frame.index.is_unique:
        raise ValueError("frame must have unique column and index labels")
    if columns is None:
        positions = list(range(frame.shape[1]))
    else:
        if isinstance(columns, str):
            raise TypeError("columns must be a sequence of names, not a string")
        selected = list(columns)
        if len(selected) != len(set(selected)):
            raise ValueError("columns contains duplicates")
        unknown = [c for c in selected if c not in frame.columns]
        if unknown:
            raise KeyError(f"Unknown columns: {unknown!r}")
        positions = [frame.columns.get_loc(c) for c in selected]
    eligible = np.zeros(frame.shape, dtype=bool)
    if positions:
        eligible[:, positions] = frame.iloc[:, positions].notna().to_numpy()
    candidates = np.flatnonzero(eligible.ravel())
    budget = int(np.floor(float(rate) * len(candidates)))
    generator = random_state if isinstance(random_state, np.random.Generator) else np.random.default_rng(random_state)
    chosen = generator.choice(candidates, size=budget, replace=False)
    mask = np.zeros(frame.shape, dtype=bool)
    mask.ravel()[chosen] = True
    return pd.DataFrame(mask, index=frame.index, columns=frame.columns)


def apply_mask(frame: pd.DataFrame, mask: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with True mask positions set missing; never mutate inputs.

    Require identical ordered axes to prevent silent pandas alignment bugs.
    Masked NumPy integer columns are converted to nullable pandas Int64/UInt64
    (preserving unmasked integer values exactly) rather than promoted to float.
    """
    if not isinstance(frame, pd.DataFrame) or not isinstance(mask, pd.DataFrame):
        raise TypeError("frame and mask must be pandas DataFrames")
    if not frame.index.equals(mask.index) or not frame.columns.equals(mask.columns):
        raise ValueError("mask index and columns must match frame exactly")
    if not all(pd.api.types.is_bool_dtype(dtype) for dtype in mask.dtypes):
        raise TypeError("mask must contain only boolean values")
    if mask.isna().to_numpy().any():
        raise ValueError("mask cannot contain missing values")
    result = frame.copy(deep=True)
    for column in frame.columns:
        dtype = frame[column].dtype
        if (mask[column].to_numpy(dtype=bool).any()
                and isinstance(dtype, np.dtype) and dtype.kind in ("i", "u")):
            nullable_dtype = "Int64" if dtype.kind == "i" else "UInt64"
            result[column] = frame[column].astype(nullable_dtype)
    return result.mask(mask)
