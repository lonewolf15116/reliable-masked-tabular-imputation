# G1A MAR anchor mapping — Decision A003, proposed frozen pre-experiment design

Recorded: 2026-11-07. This is a **new design decision**, not documentation of a previously existing per-feature allowlist. The high-level rule "explicit never-masked anchors" was approved earlier, but concrete Adult/Bank/Housing assignments were **never recorded or established**. This is the candidate map to review and sign off *before G1A PASS*. No model or baseline fitting is authorized.

## Shared rule

Only the single continuous column listed under `anchor` drives the MAR missingness score for each eligible feature in each dataset: z=(anchor - mean_train(anchor))/sd_train(anchor), where mean and sd are computed on the training split only; if train sd=0 the dataset configuration fails and is not silently changed. Anchor must remain observed, must never be masked, and cannot be used as a candidate masked feature. A feature's own value and the downstream target are forbidden from its mask probability. The mapping is explicit feature-by-feature; it is not an inferred fallback from any dataset metadata. The implementation already supports a one-column anchor; validation of this configuration remains outstanding.

For all listed eligible target features, use A002 p_ij=clip(sigmoid(a_j + 1.0*z_i), 0.01,0.99), with a_j calibrated on eligible cells to mean target rate and **exact** k_j=round-half-up(rate*n_eligible,j) selected with Gumbel-top-k scores log(p_ij)+G_ij. Rates: 0.10,0.20,0.30; MCAR uses uniform scores. The weights are not exact marginal inclusion probabilities of the fixed-count law.

## Per-dataset allowlists

### Adult — original 32,561-row `adult.data` (not combined OpenML v2)
- `anchor`: `age`
- `eligible_features`: `workclass`, `fnlwgt`, `education`, `education-num`, `marital-status`, `occupation`, `relationship`, `race`, `sex`, `capital-gain`, `capital-loss`, `hours-per-week`, `native-country`
- Feature-specific driver allowlist: **{age} for each** eligible feature above; none for `age` itself.
- Downstream target `income`: never masked and never used as an imputation predictor.
- Primary handling: `?` retained as observed categorical level in workclass/occupation/native-country; if alternative handling is desired, separate sensitivity protocol is mandatory.

### UCI Bank Marketing — `bank-full.csv` schema (45,211-row variant only; not `bank-additional-full.csv`)
- `anchor`: `age`
- `eligible_features`: `job`, `marital`, `education`, `default`, `balance`, `housing`, `loan`, `contact`, `day`, `month`, `duration`, `campaign`, `pdays`, `previous`, `poutcome`
- Feature-specific driver allowlist: **{age} for each** eligible feature above; none for `age` itself.
- Downstream target `y`: never masked and never used as an imputation predictor.
- Existing unknown levels remain observed categorical levels in the primary evaluation.

### California Housing — `sklearn.datasets.fetch_california_housing` original 20,640-row feature naming
- `anchor`: `HouseAge`
- `eligible_features`: `MedInc`, `AveRooms`, `AveBedrms`, `Population`, `AveOccup`, `Latitude`, `Longitude`
- Feature-specific driver allowlist: **{HouseAge} for each** eligible feature above; none for `HouseAge` itself.
- Target `MedHouseVal`: never masked and never used as an imputation predictor.

## Audit requirements, before the map is promoted to locked operational configuration

Every dataset schema/variant must be verified against actual bytes and the feature names checked. Freeze dataset-specific immutable split indices, train-only standardization stats, feature eligibility, and the config/hash in `configs/masks/g1a_frozen.yaml` before fitting. Any changed anchor or eligible feature requires a dated amendment and a re-run of masking reference verification. The present mapping deliberately uses one numeric never-masked anchor per dataset; the restricted driver diversity is a scientific limitation to disclose, not a license to silently add drivers.

**Status: proposed-for-review design specification recorded; not a retroactive freeze, not G1A PASS.**

## Gate 1 scope and anchor-exclusion interpretation (recorded before A003 approval)

**This is an intentionally narrow single-anchor MAR design.** Every eligible feature's missingness is conditioned exclusively on its listed anchor, with no feature-specific alternative drivers. Accordingly the Adult MAR design means "all simulated MAR missingness conditioned on age"; Bank uses age and California Housing uses HouseAge. Results must be labelled **single-anchor simulated MAR**, not generalized to all MAR mechanisms. This is a scientific limitation, not a generator defect.

**Anchors themselves cannot be masked in these MAR experiments.** Adult `age`, Bank `age`, and Housing `HouseAge` are excluded from MAR-masked eligible-cell populations. They may be included in a **separately labelled MCAR-only** masking evaluation, provided MCAR eligibility and consistent comparison populations are preregistered. If age (or HouseAge) appears in tables, mark `MCAR only / MAR not applicable: reserved anchor`. Never interpret missing MAR-age results as an omitted experiment, and never mix MCAR-only age rows into aggregate MAR risk/coverage comparisons.

A003 is still **PROPOSED**: the anchor selection has not been signed off, external dataset schemas have not been audited, and no G1A freeze is implied.
