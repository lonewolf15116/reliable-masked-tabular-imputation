# RMTI Scientific Experiment Protocol v1 — DRAFT / NOT AUTHORISED

**Date:** 2026-11-20  
**Status:** planning only; no new scientific experiment, baseline fitting, real-data processing, inferential claim, v0.2 work or commercial activity is authorised by this document.  
**Repository:** `lonewolf15116/reliable-masked-tabular-imputation`  
**Proposed study:** Conditions under which imputation ranking by masked-cell reconstruction error is unstable or misleading under controlled *MCAR* masking.

> **Gate inheritance:** The repository README reports **REVISE — G1A IN PROGRESS; G1B BLOCKED**. R002 full MAR verification and R003 original Adult-dataset byte provenance are unresolved. R001's prior non-inferiority inference was not accepted. This proposal does not bypass or replace those decisions. The existing v0.2 and commercial hold through **2026-12-17 23:59 UTC** remains in force; expiry itself does not confer authorisation. This file is a protocol candidate, not a research approval.

## 1. Motivation and bounded research question

RMTI already provides a small public masking/evaluation *utility*, not a fitted imputation estimator. Its tested MCAR sampler and masked-cell error metrics can support a controlled comparison designed to ask:

**Primary question (candidate, not a discovery):** Under which prespecified dataset and masking characteristics do baseline imputation methods change rank when evaluated by (a) overall masked-cell MAE versus (b) per-feature normalised masked-cell error and (c) a separate, leakage-free downstream task metric?

A proposed observable failure mode is that pooled unnormalised masked-cell MAE can be dominated by features with larger numerical scales and thus give a different ranking from dimensionless per-feature metrics. This is a **plausible, known measurement consideration**, not a claim of novelty. A novelty review must establish whether any proposed *conditional reliability boundary* adds new evidence to the literature.

**Primary null framing:** No stable and practically relevant discrepancy in ranking across the prespecified evaluation definitions under the tested MCAR conditions. Any positive result requires a prespecified effect-size threshold and independent replication.

Do **not** reuse the published 100×3, seed-42 demonstration as inferential evidence. Its purpose is to check software determinism and database wiring.

## 2. Connection to the released Python library

All authorised experiment drivers would **import** the existing installed distribution:

```python
from reliable_masked_tabular_imputation import (
    make_mcar_mask,
    apply_mask,
    masked_mae,
    masked_rmse,
)
```

| Existing public function | Research responsibility | Important constraint |
|---|---|---|
| `make_mcar_mask(frame, rate, random_state, columns=None)` | Sample an exact global MCAR masking budget over currently observed eligible cells | Not per-column MCAR; `floor(rate × eligible observed cells)` and column allocations vary |
| `apply_mask(frame, mask)` | Return a copy with newly hidden entries | Preserve pre-existing missing values; distinguish artificial mask from original missingness |
| `masked_mae(truth, imputed, mask)` | Measure error on newly masked numerical cells | Unnormalised, pooled across selected cells; not a downstream outcome |
| `masked_rmse(truth, imputed, mask)` | Secondary masked-cell error metric | Same selection and finite-value requirements; susceptible to feature scales |

RMTI **does not** supply mean/median/KNN estimators, normalisation procedures, benchmark harnesses, or a validated MAR/MNAR generator. Those are proposed *separate research-layer dependencies* and must not silently enter `src/reliable_masked_tabular_imputation/`.

Proposed project layout (**not yet implemented**):

```text
research/
  PROTOCOL_V1.md                 # this draft
  literature_novelty_matrix.md   # required before approval
  preregistration_frozen.yaml    # create only after protocol review
  manifests/                     # dataset, split, mask and environment hashes
  reports/                       # descriptive and inferential outputs after approval
```

The optional local PostgreSQL demonstration is documented in `docs/POSTGRESQL_EXPERIMENT_EXAMPLE.md`. It is **not currently a scientific-grade provenance ledger**: it stores `code_commit=NULL` and does not persist dataset, mask, environment or result-artefact digests. PostgreSQL must remain an optional logging backend, not an RMTI installation requirement.

## 3. Study design candidate — to freeze *before* execution

### 3.1 Datasets and eligibility

- Begin with generated, **fully observed, finite, numeric tabular data** for a synthetic design/debugging plan only; no substantive experimental run until authorised.
- Define a small **preselected** set of genuine tabular datasets only after verifying right-to-use, source URLs, original-byte SHA-256, version/date, data dictionary and target/feature definitions. The unresolved original Adult-dataset R003 provenance must **not** be bypassed using a different download.
- Document existing missingness explicitly. If present, define an eligibility rule; never label a dataset with pre-existing unknown missingness as entirely MCAR after adding artificial MCAR.
- Separate training, model-selection/validation and sealed test partitions **before** creating any imputation statistics; group/time-aware splitting when the data structure demands it.
- Define numeric-feature scaling using **training-only** estimates and record zero-variance/constant-column behaviour.

### 3.2 MCAR design

- Candidate masking rates: `{0.05, 0.10, 0.20, 0.40}` (proposed; not approved).
- Candidate seeds: `{11, 23, 37, 53, 71}` for distinct mask realisations (proposed, not a power calculation).
- Use the same eligible-cell mask for all methods within each dataset/split/rate/seed cell.
- For each run record exact number of eligible and newly masked cells, per-column mask counts, seed, split and SHA-256 of a canonical boolean-mask representation.
- Exclude/flag zero-selected-cell cases (`masked_mae` and `masked_rmse` reject empty masks); define minimum per-feature masking support before feature-normalised metrics.
- MCAR is a **simulation intervention** here, not a general claim about original real-world missingness. MAR/MNAR experiments are explicitly excluded.

### 3.3 Baseline methods and leakage control

Candidate descriptive comparator set (selection requires authorisation and compatibility review): observed-column **mean**, observed-column **median**, and **KNN imputation** for numeric features; optionally add a no-information training-only constant baseline. The released package contains none of these algorithms.

**Critical procedure:** The current synthetic smoke example computes observed column means on the *same masked table*, which is acceptable for a self-contained illustration but **not** an approved train/test benchmark protocol. For a scientific evaluation, fit all imputers and preprocessing transformations **exclusively on the training partition** under a documented missingness design. Apply frozen parameters to validation/test inputs; never compute imputation values from held-out test distributions. KNN's reference points and learned transforms must come from the training partition. The sealed test must not influence method selection.

### 3.4 Evaluation outcomes

- **Primary candidate contrast:** Frequency and magnitude of pairwise method-ranking changes between pooled masked-cell MAE and a **preregistered per-feature normalised MAE** (training-only scaling). Define ties and normalisation before running.
- **Secondary:** masked-cell RMSE, absolute error by feature, per-column support, masking-rate sensitivity, aggregate-versus-per-feature ranking stability.
- **Separate downstream endpoint (if a legitimate supervised target exists):** choose and freeze one downstream estimator, its train-only tuning procedure, target metric and sealed-test evaluation; distinguish imputation-reconstruction evaluation from prediction performance. Avoid using true hidden test values during fit or tuning.
- Report both raw and scale-adjusted metrics; never relabel a per-feature metric as `masked_mae`, since its aggregation is different.
- Include failure cases: imputers that cannot fill selected entries, nonfinite values, zero-variance features, categorical columns and no masked observations; do not silently drop failing seeds/methods.

### 3.5 Statistical plan — must be finalised prior to unblinding

- Treat independent **datasets** as the major external unit of replication, not each masked cell as an independent scientific sample. Seeds within a dataset are repeated measures.
- Predeclare a minimum number and diversity of datasets, a power or precision rationale, a smallest effect size of interest, and a decision rule for ties/failed runs.
- Use paired contrasts within the same dataset/mask/split and a hierarchical or dataset-level uncertainty analysis; choose a confidence interval, multiplicity strategy and prespecified sensitivity analyses.
- Reserve at least one independent, sealed holdout dataset/split or an independent reproduction for confirmation.
- Publish negative results, inconclusive results and any exploratory changes as such. Do not use the 47 passing unit tests or two repeated baseline runs as evidence of a statistical effect.

## 4. Evidence and provenance contract

Before an authorised execution, freeze and hash a machine-readable run manifest covering:

1. **Code:** exact Git commit, clean/dirty status, installed wheel name and SHA-256, RMTI distribution version, and executable entry point.
2. **Data:** original source, licence, acquisition timestamp, original-byte SHA-256, data preparation transform specification and prepared-data hash.
3. **Design:** split indices and their hashes, eligibility and mask definitions, complete seed schedule, global and per-feature mask counts, RMTI API contract version.
4. **Methods:** baseline package versions, train-only fitting and transformations, hyperparameters, per-method failure policy, downstream estimator configuration.
5. **Environment:** OS, Python, NumPy, pandas, scikit-learn if used, hardware where material, installed dependency lock or freeze.
6. **Results:** row-level measurement table, schema version, aggregate statistics, complete run logs and SHA-256 of output bundles.
7. **Review:** protocol identifier/hash, reviewer/owner decisions, date of approval, deviations, independent replication notes.

Write append-only or revision-tracked records. Do not put secrets or private raw data in Git. PostgreSQL may store indexed metadata and report links, but the **complete immutable manifest and digest trail** must remain retrievable without access to an individual's database.

## 5. Gates, stop conditions and authorisation

| Gate | Entry requirement | Exit evidence | State on drafting |
|---|---|---|---|
| P0 software | Existing 4-function API and regression suite | Python 3.10–3.12 CI; documented release provenance | Software checks passing; not experimental authorisation |
| P1 novelty & protocol | Written question, literature matrix, dataset eligibility, training/test leakage audit | Independently reviewed frozen preregistration, defined effect thresholds and statistical plan | **NOT SUBMITTED / DRAFT** |
| P2 mechanism & dataset | Exact real-data bytes/provenance; verified intervention mechanism | R002/R003 and any separate applicable gate dispositions with evidence | **BLOCKED for MAR and unresolved Adult data** |
| P3 execution | Explicit recorded authorisation specifying allowed MCAR experiment scope, datasets and code | Verifiable complete manifests; fixed seeds/splits; zero unauthorised deviation | **NOT AUTHORISED** |
| P4 claim review | Completed prespecified analysis and holdout replication | Independent evidence review; supported limits; transparent negative cases | **NOT AUTHORISED** |

**Hard stops:** Any missing source-byte provenance; unresolved leakage; deviations from frozen seed/split schedules; observed/masked-cell counting ambiguity; unexpectedly unfilled values; unsupported dtypes; inconclusive statistical evidence; attempted MAR/MNAR inference without mechanism approval; or use of an unapproved target/benchmark. Record failures without claiming discoveries.

**Release and commercial separation:** New research work does not imply permission for v0.2, MAR/MNAR public APIs, commercial deployment or a new PyPI release. The recorded hold through **2026-12-17 23:59 UTC** still requires a separate affirmative decision after expiry.

## 6. Protocol review checklist (no experiment execution)

- [ ] Check the current research decision ledger and obtain an explicit owner research-scope disposition.
- [ ] Complete a dated literature/novelty comparison with primary paper references and an explicit *not novel* fallback.
- [ ] Specify eligible datasets, licences, exact source-byte hashes and holdout boundaries; do not substitute unverified Adult data.
- [ ] Freeze the set of baseline methods and train-only fit/predict rules.
- [ ] Choose one primary endpoint, meaningful effect threshold, sample-size/precision justification and full analysis decision tree.
- [ ] Verify the proposed validation implementation against independent numerical fixtures (including masking counts and scale handling).
- [ ] Obtain independent protocol review; document who reviewed what and whether a signed identity is available.
- [ ] Record a separate **GO** decision and permitted execution scope before any new scientific run.

**Current declaration:** 0 validated scientific discoveries from this protocol. The only executed RMTI synthetic demonstration remains a software regression example (100 rows × 3 numeric columns; seed 42; 60 globally MCAR-masked cells; mean baseline MAE ~3.775269, RMSE ~5.803243), not primary study evidence.

## 7. Related repository evidence

- [Software API and current research restrictions](../README.md)
- [Post-release roadmap and hold](../docs/POST_RELEASE_ROADMAP.md)
- [Optional local PostgreSQL demo](../docs/POSTGRESQL_EXPERIMENT_EXAMPLE.md)
- [Synthetic-regression test](../tests/test_synthetic_experiment.py)
- [Published v0.1.0 provenance issue #7](https://github.com/lonewolf15116/reliable-masked-tabular-imputation/issues/7) — historical exact-byte rule was not met, even though subsequent read-only archive forensics found matching extracted contents and timestamp differences.

This protocol must be revised and frozen only after review. It is **not** itself preregistration, approval, evidence of imputation superiority, or permission to run a benchmark.
