# Downstream descriptive paired-comparison report — locked template A001

Dataset: `<dataset>`  |  Outcome metric: `<metric>`  |  Direction: `<smaller/larger is better>`  |  Compared methods: `<proposed>` and `<baseline>`

- Split and reference versions: `<IDs>`
- Paired-seed differences, proposed − baseline (all 15, in locked seed order): `<d_01,...,d_15>`
- Mean paired difference: `<value>`
- 90% two-sided Student-t descriptive interval: `[<lower>, <upper>]`
- 95% two-sided Student-t descriptive interval: `[<lower>, <upper>]`
- Bias-corrected sample skewness (Fisher-Pearson G1): `<value>`; n = `<n>`
- Shapiro-Wilk: W = `<value>`; p = `<value>`
- Effective paired N: `<value>`; missing/ineligible pairs and rationale: `<details>`
- 1% relative margin: `<value and baseline denominator>`; visual reference line only, **not a decision threshold**
- Reporting label: **DESCRIPTIVE ONLY — no binary NI claim**

**Permitted interpretation:** Describe direction, magnitude, variability, and uncertainty, without asserting a binary inferential decision. Intervals may be unreliable under skewness; explain the diagnostic findings and avoid overinterpreting their coverage.

**Prohibited result descriptions:** `non-inferior`, `equivalent`, `not significantly worse` (except historical references in the decision ledger). Never compute or display a binary NI PASS/FAIL result. Separate methodological NI validation findings from imputation results.

**Source of authority:** A001 in `protocol/AMENDMENT_R001_DESCRIPTIVE_ONLY.md`; A002 changes MAR weighting documentation only, not this reporting scope. This template is present on the PR #1 head branch for review and is not permission to evaluate Adult test results.
