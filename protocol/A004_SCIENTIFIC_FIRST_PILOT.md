# A004 — Scientific-first G1A closeout and bounded feasibility pilot

Recorded 2026-11-07. **Owner-directed research reprioritisation.** This is a proposal to change sequencing and scope, not a claim of experimental completion. Draft PR #1 stays unmerged, G1A IN PROGRESS and G1B BLOCKED until explicit gate closure. No G1C or G1D authority is granted. Zero confirmed scientific discoveries.

## Why scope changes

The objective is no longer to optimise protocol process before first evidence. Existing simulations exposed failures of downstream binary non-inferiority methods, leading to A001 descriptive-only scope. No imputation results have yet been generated. Do not reopen NI gate design, run another methods-gate, or claim novelty from those failures.

Scientific hypothesis: **uncertainty-guided selective imputation might lower accepted-cell error and human review cost at matched coverage versus uncertainty-naive and incumbent baselines**. Full-coverage RMSE is a diagnostic, not the main endpoint.

## One bounded G1A closeout — remaining items only

1. **S003**: construct a feature-level shared eligible-cell definition from frozen S001/S002 (and source); commit a small reproducible manifest rather than unrestricted per-cell expansion. Verify exclusion of `income`, explicit `?` category, zero-IQR `capital-gain` and `capital-loss` excluded from the *primary IQR-normalized aggregate* but separately reported in raw units. Masked-cell identities for any approved run must be frozen before predictions, equal across methods. Preserve every originally observed row.
2. **A003**: owner approval must be an explicit ledger decision, *not inferred from this proposal*. Candidate Adult `age`, Bank `age`, Housing `HouseAge` as sole never-masked anchors; MAR cannot mask those anchors. Each dataset's other eligible features condition missingness on that anchor alone. This is **single-anchor simulated MAR**, not representative of all MAR mechanisms. If a reserved anchor appears in comparisons, mark it MCAR-only or MAR-not-applicable. Schema confirmation is required for used datasets; Adult first, defer unused external dataset execution checks to their own stage rather than pretending checked.
3. **R002**: retain the passed 60,000-draw toy test; perform only the remaining *independent and configuration-relevant* checks necessary for the Adult pilot, without silently extrapolating the toy result to full datasets. Record reference implementation, seeds, scope and failures. Do not run combinatorial full-category enumeration if infeasible. The prospective 120-second and independently seeded 10k fallback can be used only where its fixed defect alternative and power criterion are satisfied; inconclusive stays inconclusive.
4. Single sign-off note with source SHA, split assignment SHA, S002 exact-zero-IQR set, S003 eligibility hash, A003 sign-off, R002 evidence and failures. No new NI validation, extra CI gates, or unrelated project expansion. If any blocking check fails, mark failure and decide explicitly whether to narrow the pilot rather than quietly waiving it.

## Separate feasibility pilot P001 — authorization boundary

P001 may be **authorized only after the minimal G1A closeout is signed**; it is not G1B/G1C or an early G1D test evaluation. Its result is exploratory and cannot serve as confirmatory evidence. Adult 32,561 original rows, immutable S001 training and validation only; no S001 test row may be read or used for pilot evaluation, tuning, uncertainty calibration or final conclusions. One prespecified 20% fixed-count MAR regime using the approved single `age` anchor; `age` never MAR masked. Use identical frozen masks/cells for all methods. Compare (i) MICE, (ii) MissForest, (iii) minimal masked-feature MLP with a small independently initialized ensemble for risk estimation. Fit preprocessing and all imputers on training data only. Use a fixed validation separation for calibrator/threshold selection vs reported pilot curve to avoid evaluating on the same examples used for selection; alternatively use separate cross-fit folds predeclared before running. No use of `income` as input to any imputer. No external datasets.

Outcomes at **matched accepted-cell coverage, especially 80%**: risk/error on the accepted 80%; selective-risk versus coverage curve; ranking/uncertainty diagnostics; featurewise interval or set calibration and empirical coverage if applicable; simulated review fraction and cost at a **declared** unit review cost. Full-coverage numeric RMSE and categorical error are secondary. Report numeric and categorical errors separately rather than mixing incomparable units. Zero-IQR numeric features separately, not divided by zero. Distinguish prediction-set calibration from point-error risk ranking. A naive random-abstention baseline must be included for interpretability; any uncertainty score produced by MICE/MissForest must be specified and validated rather than invented.

Choose computational ceilings before any fit (one development-only condition, finite seeds, brief budget). Negative outcomes and method failures must be fully reported. Avoid claims of non-inferiority, causal effect, general MAR coverage, or scientific novelty. A pilot success is a signal to fund full G1B and G1C; a failure triggers stop/pivot review, not automatic abandonment or protocol repair loops.

## Stop-or-pivot decision

Continue to full research only if selective-risk improvement relative to strongest baseline at matched 80% coverage is practically meaningful under a **declared review-cost model** and not an artifact of feature mix, leakage, or masking. If MLP loses, ask whether baseline uncertainty ranking, calibration and abstention still offer a viable contribution; do not require the MLP to beat MissForest on raw RMSE. Record all null and negative outcomes.

**Current: A004 sequencing documented; S003 incomplete, A003 proposed/unapproved, R002 broader Adult checks incomplete; P001 not yet authorized to execute.**
