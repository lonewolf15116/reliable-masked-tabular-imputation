import numpy as np
import pandas as pd
import pytest

from reliable_masked_tabular_imputation import (
    make_mcar_mask,
    apply_mask,
    masked_mae,
    masked_rmse,
)


def test_synthetic_mcar_mean_baseline():
    rng = np.random.default_rng(42)

    original = pd.DataFrame({
        "feature_a": rng.normal(10, 2, 100),
        "feature_b": rng.normal(20, 5, 100),
        "feature_c": rng.normal(30, 8, 100),
    })

    mask = make_mcar_mask(original, rate=0.20, random_state=42)
    masked = apply_mask(original, mask)
    imputed = masked.fillna(masked.mean())

    assert int(mask.to_numpy().sum()) == 60
    assert masked_mae(original, imputed, mask) == pytest.approx(
        3.77526901862113
    )
    assert masked_rmse(original, imputed, mask) == pytest.approx(
        5.803242712249292
    )
