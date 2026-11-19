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


---

## 8. IR001 independent review disposition and v1.1 revision candidates (2026-11-20)

**External review supplied:** `RMTI-SPV1-IR001`, decision **REVISE**. The report says it inspected PR #10 and the README, but **did not** execute a benchmark, verify the research decision ledger/R002/R003, or independently validate the cited literature beyond search snippets. This is a methodological review of the draft, not approval to execute.

The eight corrections below are **proposed design choices for reviewer scrutiny**, not a frozen preregistration or proof that the concerns are closed. No datasets have been acquired or analysed for this study.

| Finding | Proposed v1.1 response | Closure state |
|---|---|---|
| M-01 dataset set missing | Freeze an eligible, licensed, traceable dataset inventory with original SHA-256, original download/source, version, target and feature schema, missingness audit, and independent holdout allocation | **OPEN**: no verified source-byte hashes or frozen list yet |
| M-02 per-feature support missing | Candidate threshold: at least **10 artificially masked finite numeric cells per included feature, per evaluation cell**; otherwise flag unsupported and exclude that feature from scale-normalised *per-feature* aggregation, with counts/coverage and full exclusion table | Proposed only; check how exclusions influence comparisons |
| M-03 baseline fitting ambiguous | Candidate train-fitted mean/median and training-reference KNN baselines with predeclared numeric-only features, deterministic preprocessing, 5 KNN neighbours, uniform weights, and no use of test statistics or test data as KNN reference points | Proposed; exact library/version/API implementation requires external check |
| M-04 downstream endpoint optional | **Restrict primary comparison to two reconstruction-based rankings**: pooled masked-cell MAE vs equal-feature-weighted training-scale-normalised MAE. Downstream prediction becomes a distinct **exploratory**, separately approved extension | Proposed clarification |
| M-05 categorical columns ambiguous | Primary analysis uses **numeric-only features**; exclude categorical features from primary estimands, disclose exclusion counts and no claims about mixed-type imputation | Proposed clarification |
| Statistical plan absent | Set candidate paired contrast, effect threshold, tie margin, multiplicity family and precision target below | **OPEN** until dataset count/precision and independent statistician review |
| Split/protection ambiguous | Precommit split IDs, train-only preprocessing, validation selection rules, signed/sealed test hashes and independent release authority | **OPEN** until real split manifests and reviewer specified |
| Manifest/literature incomplete | Define candidate canonical manifest rules; compile dated 5–10-paper novelty matrix from primary sources; require independent check | **OPEN**: primary literature and verified manifest not yet supplied |

### 8.1 Candidate estimand and metric definitions

- **Unit:** dataset; multiple mask seeds and rates within each dataset are repeated measures. Count no masked cell as an independent external replicate.
- **Compared methods:** candidate train-fitted mean, median, and KNN; method identity and deterministic settings must be frozen before dataset outcomes are inspected.
- **Primary endpoint A:** the existing RMTI `masked_mae` pooled over newly masked eligible numeric cells in the evaluation subset. All methods must be scored on the **same mask**.
- **Primary endpoint B:** compute per-feature absolute error on newly masked cells, divide by **training-only robust scale** defined as IQR; average with **equal weight across supported features**. Features with training IQR = 0 or fewer than 10 selected masked cells are **unsupported** and excluded from endpoint B; disclose the unsupported count. If no features remain, mark the dataset/rate/seed cell **UNEVALUABLE**, not a zero result.
- **Critical comparability rule:** for a pair of methods, compare endpoint A and B **on the same common supported feature subset**, rather than comparing an all-feature pooled score to an exclusion-based equal-weight score. Also report the full eligible-feature pooled error as supplementary information. This avoids attributing a reversal solely to changing the feature set.
- **Rank inversion:** for a prespecified method pair, method X beats Y on A but Y beats X on B, or vice versa; both improvements must exceed their endpoint-specific **5% relative margin**, measured relative to the larger absolute pairwise score or a predeclared nonzero numerical floor. The 5% threshold is **a candidate smallest practically relevant contrast**, not an empirically justified SESOI; reviewer must approve a numerical-floor policy and justify this threshold before freeze. Ties inside the margin are **TIE**, not reversals.
- **Missing/failing methods:** retain failure rows and their reason; exclude failed pairwise comparisons from the conditional inversion calculation but report numerator and denominator, failure rate and an explicit worst-case sensitivity bound. No imputer may silently receive test labels or true masked test entries.

### 8.2 Proposed split, fitting and data controls

1. Eligible training/validation/holdout sets must be defined and cryptographically sealed **before** imputation or parameter selection. Candidate split fractions `60/20/20` are a design proposal, not a justification. Use a documented group/time split in place of random splitting whenever independence requires it; record entity leakage checks.
2. Precommit exact split IDs and seed schedules. The true values for artificially masked evaluation cells are kept solely for metric calculation and are not available to imputers or preprocessing.
3. For every method, fit reference statistics and any scaling/encoder on **masked training data only**; choose hyperparameters on validation data only; **freeze** before sealed holdout evaluation. KNN references consist solely of training examples. Explicitly specify how training missingness is introduced and how validation/test missingness intervention is replicated, to avoid inconsistent training/test regimes.
4. Any test-adaptive mean/median fill, KNN test-to-test neighbour search, refit on test data, metric-driven method selection on test, or post hoc removal of failed seeds is forbidden.
5. Report a method-fit matrix covering numerical dtype compatibility, no-observed-value handling, nonfinite input policy, constant features, KNN distance/weights/neighbour count, implementation package/version, and deterministic/randomness controls. **No benchmark implementation is authorised until this table is externally checked.**

### 8.3 Statistical decision-plan candidate

- **Data sufficiency remains UNRESOLVED:** review recommends at least 3–5 datasets; a small set cannot establish a broad generalisation claim. Candidate planning target is **at least 8 independent datasets**, distinct in feature-scale dispersion and correlation structure, plus **at least one separately sealed external confirmation dataset**. This number is a planning target, **not a verified power/precision calculation**. If source provenance, licensing or sample-size precision cannot be met, **STOP** instead of relaxing after looking at results.
- **Primary predeclared comparison family:** 3 method pairs × 4 MCAR rates = **12 primary contrasts** for the binary practically relevant rank-inversion event; seed-level results aggregated within dataset and rate before across-dataset inference. The 5 proposed seeds `{11,23,37,53,71}` are within-dataset repeats and not independent datasets.
- **Candidate inferential rule:** family-wise Holm correction for 12 primary contrast tests, with a predeclared two-sided 5% family-wise error rate. **No statistical test, effect-size estimator, null model or dependence correction is yet frozen**; reviewer/statistician must select appropriate dataset-level uncertainty intervals and decision rules, including a tie/failure rule, *before* any run.
- **Precision planning requirement:** demonstrate an interval-width or simulation-based power argument that accounts for the number of **independent datasets** and high within-dataset correlation. Record a clear minimal relevant inversion-frequency difference, expected dataset heterogeneity and holdout confirmation criterion before freeze; do not reuse the candidate 5% score margin as a power calculation.
- **Negative/inconclusive result:** report if 0/12 corrected tests provide robust evidence or the effect does not replicate, without changing cutoffs or declaring a discovery. A sample too small for acceptable uncertainty is **INCONCLUSIVE**, not evidence of absence.

### 8.4 Proposed pre-execution manifest contract

Before the GO decision, a reviewer must inspect the exact schema and verify a **canonical UTF-8 JSON** encoding using sorted object keys, no insignificant spaces, a declared standard for float/NaN representation (**nonfinite JSON disallowed**), an explicit Unicode normalisation rule and stable array ordering. The SHA-256 covers the exact canonical byte sequence. Store a signed or review-attested **pre-execution** digest for the protocol, dataset inventory, split/mask-seed schedule, baseline plan and analysis plan. Compare these frozen digests immediately before execution; abort on mismatch.

Results and environment fingerprints are *post-execution append-only records* linked to the pre-execution manifest by its digest; do not pretend the resulting output hash could be frozen before the run. Store package artifact SHA-256, Git commit and run environment separately. PostgreSQL may index these references but must never be the sole provenance record.

### 8.5 Literature, dataset and approval blocker ledger

**Novelties not established:** The reviewer characterises the primary metric-ranking phenomenon as incremental and did not perform systematic primary-source verification. Do not cite the review's unverified snippets as if they settle novelty. Create a **dated 5–10-entry primary literature matrix** listing bibliographic identifiers/DOI or stable URL, exact research setting, missingness mechanism, compared metrics, observed findings, methodological overlaps and the **specific** proposed conditional-boundary contribution. If this shows the question already answered, record **NOT NOVEL** and stop or reframe *before* data access.

**Dataset blockers:** No verified list of original dataset URLs, licence terms, source-byte SHA-256, split manifests or independent holdout allocation is supplied. The Adult dataset remains off-limits until R003 is resolved; R002 MAR validation remains excluded. No dataset placeholders may be misrepresented as acquisition evidence.

**Gate decision:** IR001 = **REVISE**. P1 remains **DRAFT / OPEN**, P2 and P3 remain **BLOCKED / NOT AUTHORISED**. Neither this proposed revision nor a passing CI check approves benchmarks, model fitting, real-dataset processing, MAR/MNAR studies, publication, v0.2 work or a scientific discovery. Seek a **second independent review** after completing the real literature, dataset, statistical precision and manifest evidence.

