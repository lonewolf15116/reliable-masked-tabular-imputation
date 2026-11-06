# Protocol amendment A001 — Downstream NI scope reduction

Decision date: 2026-11-07 (UTC). This amendment supersedes the downstream non-inferiority test and binary NI success criterion in `protocol/G1A_DRAFT.md`; other protocol items remain draft and unfrozen.

## Binding decision

Downstream comparisons are descriptive; no binary non-inferiority claim is made, because the prespecified NI procedures failed validation under skewness (see decision ledger).

For every comparison report the full 15 paired differences, mean difference, 90% and 95% **two-sided descriptive** Student-t intervals, bias-corrected sample skewness and n, Shapiro-Wilk W and p, effective N, and the 1% relative margin **as a reference line only**. No inferential classification or automatic downstream pass/fail from the margin. Do not describe any comparison as "non-inferior", "equivalent", or "not significantly worse" in manuscript, README, tables, plots, or generated summary text. Only explicit discussion of the retired procedure in the decision ledger may use those terms historically. No bootstrap/gated/path-2 replacement is authorized.

## Reasons and preserved failures

1. Adaptive 5→15 seed stopping: formal NI boundary false rejection 6.73% in an intermediate-SD regime (100,000 simulations); data-dependent expansion invalidated assumed single-stage control.
2. Fixed-15 t inference: false NI rejection 11.88% under centered exponential and 30.18% under centered lognormal (100,000 simulations per regime); skewness violates small-sample pivotal assumptions.
3. Five-seed skewness gate: conditional false NI rejection 12.58% exponential, 37.03% lognormal.
4. Same-sample Shapiro-Wilk gate: conditional false NI rejection 15.86% exponential; 77.4% lognormal with insufficient effective passing replicates (<5,000).

These are design-validation observations, not evidence of improved imputation and not a theorem of impossibility for all procedures. Original evidence artifacts must remain intact.

## Documentation and guardrails

`templates/DOWNSTREAM_DESCRIPTIVE_REPORT.md` is the fixed output format and wording contract. The eventual manuscript's methods section must include the exact one-sentence scope statement above. Keep methods-validation findings in a separate section from imputation results. G1B remains blocked until R002 and R003 complete and a new review approves it. Changes require a new, dated ledger entry and hashed amendment; no silent edits to this amendment.
