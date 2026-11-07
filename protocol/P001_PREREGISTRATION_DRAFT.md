# P001 — preregistration preparation (curve-first, Adult-only)

**Status: DRAFT — NOT FROZEN; P001 EXECUTION NOT AUTHORIZED.** Prepared after bounded G1A sign-off `c7875fa`. A frozen preregistration requires committed validation-half files and their verified SHA-256, final risk-score implementation checks, a frozen mask/cell-set manifest, and an explicit owner approval of any new metric details below. Its eventual freeze commit SHALL NOT also authorize training. Only a separate subsequent explicit authorization may start P001.

## 1. Data partition and isolation

- Adult `adult.data` only, SHA256 `5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d`. S001 training indices 22,792; S001 validation 4,884; S001 test 4,885 untouched.
- The validation IDs are read from the **sorted ascending** S001 validation index file, SHA256 `48add8759a60eeaf7b12cdbed787dfb5ff3a78ec9161ab1b92c49cabb5b02e03`.
- New distinct seed `pilot_validation_partition=20261114` (not S001 split 20261107, mask 20261108, model 20261109, calibration 20261110 or bootstrap 20261111). Python 3.12.10, NumPy 2.1.3, sklearn 1.5.2. Use `numpy.random.default_rng(20261114).permutation` on sorted 1-based validation row IDs. First 2,442 go to **selection**; last 2,442 to **reporting**. Both emitted sorted, ASCII with LF, separate files.
- `scripts/p001_validation_halves.py --mode generate` creates these once; `--mode verify` byte-recomputes and checks manifest and SHA against S001. **Actual output file hashes are pending until the owner runs and commits the generator.** Do not represent those as frozen now.
- Selection half ONLY for early stopping, fixed member selection (if any), calibration and other prospectively permitted development decisions. Reporting half accessed ONCE for preregistered evaluation; never for tuning, score direction, architecture, loss, feature weights, or GO thresholds. No use of S001 test rows.

## 2. Mask / model boundaries

- One Adult single-anchor simulated MAR at 20% exactly per eligible feature, conditioned on TRAIN-standardized `age` (train mean `38.54646367146367`, population SD `13.602926529574551`, train-standardized SHA256 `2a803bf89e6b555b490eb139b4e44963e55b35044626faa65972b13336ddd908`). `age` is never MAR-masked and `income` is never an input, masked predictor, or outcome in P001.
- Only training/validation masks; frozen seed stream and actual mask cell IDs must be hashed and shared by all methods **before** any model prediction; the S001 test set remains untouched. Original literal `?` values remain observed category levels. No raw-row deletion.
- Three methods only: mixed-type MICE (20 stochastic imputations), MissForest (100 trees in each relevant feature-specific forest), and masked-training three-hidden-layer width-64 MLP, five independently initialized ensemble members. A random-abstention control is a diagnostic, not a fourth trained imputer. No architecture search or transformers. Freeze package versions, MICE categorical conditionals, seed streams and runtime limits before execution. No unapproved fallback model or score.

## 3. Risk scores — higher always means greater predicted error

Scores rank each method's own masked cells in ascending order; **only ranks, not absolute risk-score values, are compared across methods**. They are not assumed calibrated or commensurate between model families.

| Method | Numeric risk, for each masked cell | Categorical risk, for each masked cell |
|---|---|---|
| MICE, m=20 stochastic conditional imputations | Population variance (ddof=0) of 20 imputed numeric values, divided by squared positive *training* IQR when used in the pooled numeric ranking | Shannon entropy (natural logarithm, 0log0=0) of the empirical category distribution over 20 categorical draws |
| MissForest, 100 trees | Population variance (ddof=0) of tree-level numeric predictions from the feature's final fitted forest, divided by squared positive training IQR for pooled numeric ranking | Shannon entropy of the proportions of the 100 tree votes for that feature |
| Masked MLP, five independent members | Population variance (ddof=0) of five member predictions, divided by squared positive training IQR for pooled numeric ranking | Shannon entropy of the five members' **averaged predicted categorical probability vector** |

For numeric point reconstruction use mean of draws/members/tree predictions as appropriate; for categorical point reconstruction use highest-probability category (lexicographic tie-break by the frozen train-only vocabulary order). To implement MICE categorical draws, a stochastic mixed-type chained-conditional procedure must be explicitly selected and tested **before preregistration freeze**; sklearn `IterativeImputer` alone does not implement categorical posterior draws. Likewise the chosen MissForest implementation must truly expose final per-feature tree predictions/votes, rather than assigning a fabricated risk proxy. If either is unavailable, **block pilot freeze**, report the limitation, and do not compare against a strawman. Freeze all categorical vocabularies from S002 train-only statistics; unseen category handling needs a prespecified rule.

## 4. Curve-first primary outcome and loss

- **Proposed primary numeric population (requires explicit owner approval as new choice):** MAR-masked held-out cells in the three positive-IQR, MAR-eligible numeric Adult columns: `fnlwgt`, `education-num`, `hours-per-week`. `age` is the never-masked anchor; zero-IQR `capital-gain` and `capital-loss` are masked if eligible but never divided by IQR and are reported separately in raw units. All eight MAR-maskable categoricals are reported using a separate 0/1 categorical error selective-risk curve. **Do not pool numeric and categorical units into a new primary endpoint.**
- Primary loss per numeric cell is `abs(true-imputed)/train_IQR(feature)`. Pool these three feature-cell populations **equally per masked cell**, not by hand-tuned feature weights. At 20% fixed count and equal held-out row eligibility, each numeric feature contributes the same number of masked cells.
- For each method, rank only those primary numeric masked cells by ascending numeric risk; break exact ties by `(row_id,feature_name)` ascending. For k=1..N compute accepted-cell mean loss among the lowest-risk k; empirical coverage k/N. Store full integer-k cumulative summaries and hash.
- Report exactly 100 grid-point curve values at target fractions `0.01,0.02,...,1.00`, by linear interpolation between the bracketing integer-k empirical coverage/risk points. At c=0.80 read each method's accepted-cell loss from the **same** grid. Never select a numeric abstention threshold on selection data for the primary result. This is a retrospective ranking evaluation, not a deployable acceptance-threshold policy.
- **Best baseline** = whichever of MICE/MissForest has **lower held-out primary accepted-cell error at c=0.80**, with a deterministic tie preference for MissForest. Report the nonselected baseline as well. This selection is built into the frozen comparison rule; never change baselines post hoc.

## 5. Calibration and simulated review queue

- Proposed calibration: per-feature numeric nominal-90% split-conformal intervals, using only **selection** observed masked evaluation cells to fit the absolute-residual conformal quantile, with finite-sample rank `ceil((n+1)*0.90)` order statistic; if rank exceeds n, return an unbounded interval and label it not informative. Apply frozen interval radii to held-out predictions, reporting empirical held-out coverage separately for each primary numeric feature. Other feature calibration (categorical sets and zero-IQR numerics) remains secondary and must be explicitly specified or marked not applicable **before freeze**. Target band for primary numeric featurewise 90%-nominal coverage is [0.85,0.95] inclusive; this is a pilot heuristic, not guaranteed.
- Queue comparison uses the **best baseline's held-out accepted-cell error at 80% coverage** as fixed error target `T`. Baseline queue fraction is 20%. For the MLP curve determine the **largest** accepted fraction c with interpolated primary loss ≤T (if several c, select largest); MLP queue fraction =1-c. For the GO queue criterion require MLP queue strictly <0.20. This is an **oracle retrospective diagnostic** calculated using held-out outcomes, *not* a deployable review budget or labour-hours estimate. Report if no nonempty accepted subset achieves T. Report every curve even if its accepted-cell error is nonmonotonic.

## 6. Prespecified pilot decision

Assess once on reporting half only, using the above point definitions:

- **GO** iff all three: MLP numeric accepted-cell loss at 0.80 is at least 5% lower than the best baseline (relative ratio `(L_best-L_MLP)/L_best >= 0.05` with `L_best>0`); each of the three primary numeric held-out nominal-90% coverage rates falls in [0.85,0.95]; MLP oracle queue fraction to reach baseline-80% loss is strictly <0.20.
- **PIVOT** if GO fails and MLP primary loss is not below baseline (`L_MLP>=L_best`), but wins **either** on calibration or queue. Calibration win means MLP macro-average absolute deviation `mean_feature |coverage_90-0.90|` is strictly lower than the best baseline's corresponding deviation using the same three features; queue win means MLP fraction <0.20.
- **STOP for this MLP pilot** if GO fails, MLP primary loss is not below baseline, calibration is not better, and queue is not better; applies to this pilot scope only.
- **INCONCLUSIVE** for all other configurations, including missing risk scores, uncomputable baseline/calibration, zero baseline loss, any unapproved categorical policy, or 0%-to-5% numeric improvements not meeting all GO requirements. Negative and null results must be recorded; do not retune after inspecting held-out reporting metrics.

The validation-half partition must be committed and hashes verified; the actual pilot mask population, method implementations, loss-scope choice above, runtime ceiling and model/seed settings must be frozen in a **subsequent** preregistration finalization commit. An **additional later owner authorization**, separately recorded after that freeze, is required before any MICE/MissForest fit, MLP training, or reporting-set evaluation.

**Current: draft preregistration; no split artifacts committed yet, no models fit, G1B blocked, P001 execution blocked, scientific discoveries 0 confirmed.**
