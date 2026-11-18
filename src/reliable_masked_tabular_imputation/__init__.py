"""Reproducible masking and evaluation tools for tabular imputation.

The public API currently covers MCAR masking and masked-cell metrics.
It does not certify MAR simulation or an imputation model.
"""
from .masking import apply_mask, make_mcar_mask
from .metrics import masked_mae, masked_rmse

__version__ = "0.1.0"
__all__ = ["make_mcar_mask", "apply_mask", "masked_mae", "masked_rmse"]
