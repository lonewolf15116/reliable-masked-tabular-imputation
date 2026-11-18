# Migration and namespace guide

RMTI v0.1.0 deliberately ships **two separate APIs**. These functions must not be treated as interchangeable:

| Property | Stable utility API | Existing experimental research API |
|---|---|---|
| Import | `reliable_masked_tabular_imputation.make_mcar_mask` | `rmti.masking.generate_mask` |
| Mechanism | Fixed-count MCAR only | Experimental MCAR/MAR |
| Mask budget | Global, floor(rate × eligible cells) | Per feature, floor(rate × eligible + 0.5) |
| Seed semantics | NumPy `default_rng` using supplied seed | `stable_seed(seed, feature)` using Blake2b |
| Result | Labelled boolean pandas DataFrame with full original shape | Boolean NumPy array restricted to selected features |
| Input missingness | Automatically excludes original missing cells | Uses supplied eligibility mask or assumes all eligible |
| Research status | Utility API subject to software tests | MAR verification unresolved: R002 |

**Do not substitute one function for the other in an existing experiment.** Different counts, eligibility, seeds and output types mean a substitution changes experiment semantics. Even when both are called 'MCAR', their fixed-count conditional distributions are different.

The experimental module remains under its existing name to avoid silently breaking archived research protocols. It is **not endorsed as a validated public MAR interface**. In a future major release it may be separated from the general-purpose distribution after a formal migration and reproducibility audit. There is no automatic migration or silent alias.

For a fresh utility application, use the new public package. For reproduction of frozen G1A work, use exactly the legacy revision and protocol originally specified.

Tests for the utility public API must not be interpreted as scientific authorisation for G1B.
