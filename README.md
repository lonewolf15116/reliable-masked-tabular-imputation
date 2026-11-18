# Reliable Masked Tabular Imputation (RMTI)

A small, installable Python toolkit for **reproducible MCAR masking** and **masked-cell imputation evaluation** on pandas tables.

> **Scope:** The software API below is a utility library, not a validated imputation estimator. The accompanying research programme remains **REVISE — G1A IN PROGRESS; G1B BLOCKED**. R002 full MAR verification and R003 original Adult dataset byte provenance are unresolved. No model fitting, baseline fitting, test-set evaluation or scientific performance claim is authorised by this release.

## Install

Requires Python 3.10 or later.

```bash
python -m pip install -e ".[test]"
python -m pytest
```

The package is installed from this repository. **It is not claimed to be published on PyPI.**

## Quick start

```python
import pandas as pd
from reliable_masked_tabular_imputation import (
    make_mcar_mask, apply_mask, masked_mae, masked_rmse
)

truth = pd.DataFrame({"age": [20., 30., 40., 50.], "score": [1., 2., 3., 4.]})
mask = make_mcar_mask(truth, rate=0.25, random_state=42)
incomplete = apply_mask(truth, mask)

# Illustrative baseline only, not an endorsed research experiment:
filled = incomplete.fillna(incomplete.mean())
print("MAE:", masked_mae(truth, filled, mask))
print("RMSE:", masked_rmse(truth, filled, mask))
```

### API contracts

- `make_mcar_mask(frame, rate, random_state=0, columns=None)` uniformly samples **exactly floor(rate × eligible observed cells)** without replacement. The boolean mask marks *newly* hidden cells only. It never targets originally missing cells. An integer seed repeats the result; a supplied NumPy Generator is consumed. Selection is global, not column-stratified.
- `apply_mask(frame, mask)` returns a masked copy, preserving the input. The mask must have identical ordered index/columns and boolean entries.
- `masked_mae(truth, imputed, mask)` and `masked_rmse(...)` score **only True mask cells**. These cells must be finite numeric values in both truth and prediction. Empty masks raise `ValueError`. Other categorical columns are allowed.
- Unique row and column labels are required for mask generation. A rate of 0 or no eligible cells yields an all-False mask.

This library deliberately does **not** label MCAR simulations as MAR, provide a learned imputer, assert non-inferiority, or certify scientific results.

## Legacy research modules

The distribution also retains the existing experimental `rmti.masking` and `rmti.schema` modules for compatibility with the repository's G1A work. These are **not aliases** of the new public API: legacy `generate_mask` uses per-feature counts and supports an experimental MAR branch; new `make_mcar_mask` uses a global exact-budget MCAR sampler and returns a labelled DataFrame. Do not interchange their masks or assume they have identical sampling or validation contracts. The experimental MAR implementation remains **unverified** and outside the supported v0.1.0 utility API.

## Quality and release

Run `python -m pytest`; CI tests Python 3.10–3.12. Before publishing a distribution, run `python -m build` and `python -m twine check dist/*`, verify the wheel in a clean environment, review dependencies and licence, and record release provenance. Do not interpret passing unit tests as a research gate.

## Research status

R001 was closed by reducing inferential scope. Prespecified non-inferiority procedures failed validation under skewness, so downstream comparisons remain descriptive. R002 (MAR verification) and R003 (original Adult bytes) remain unresolved. Scientific discoveries confirmed: **0**. Retain the project's research decision ledger for the detailed gate record.
