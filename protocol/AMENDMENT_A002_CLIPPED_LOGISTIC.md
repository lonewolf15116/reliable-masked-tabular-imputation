# A002 — MAR weighting specification reconciliation

Decision recorded: 2026-11-07. Status: AUTHORITATIVE DOCUMENTATION CORRECTION; G1A NOT FROZEN.

## Discrepancy and resolution

G1A Gate Review 006 identified that an older protocol draft described exponential weighting while the previously agreed design and current implementation use **clipped logistic probabilities**. The draft is stale. The implementation must **not** be switched to exponential for document conformity.

For an eligible cell in feature j, take an authorized always-observed anchor z from the frozen feature-specific allowlist, standardized using **training-only** statistics. For preselected slope b_j, define

    p_ij = clip(sigmoid(a_j + b_j * z_i), p_min, p_max),

where a_j is found by monotone bisection to give mean(p_ij) = target mask rate across eligible rows (subject to feasible clipping bounds). Draw independent standard Gumbel variates and select the top k_ j scores log(p_ij) + G_ij, with k_j = floor(rate * n_eligible,j + 0.5). This is **fixed-count weighted without replacement**. p_ij are selection weights; they are **not claimed to be the exact marginal inclusion probabilities** of the resulting top-k design. Keep this distinction explicit in evaluation reports.

Only eligible features may be masked. The downstream target (Adult income) and every designated MAR driver remain observed and never appear in the imputation predictor set where prohibited. Fixed driver allowlists and all parameters are required before freeze; the present implementation has a one-anchor demonstration API and is not a complete feature-specific driver-allowlist implementation.

## Fixture provenance audit: what is and is not established

Present remotely: src/rmti/masking.py uses clipped logistic probabilities; tests/test_g1a_battery.py invokes that implementation for its MAR cases; tests/golden_mask_mcar_seed17.csv is an MCAR fixture and therefore has **no weighting-scheme dependence**. tests/test_masking.py checks MAR generation with an anchor but has no committed MAR-specific expected-mask fixture. The remote R002 Review Candidate 005 summary states a full-MAR reference distribution was generated from the current anchor-based protocol; its raw enumerated distribution and original hash-manifest are **not yet present in this GitHub repository**.

**Thus no committed test or fixture in the currently inspected GitHub source is demonstrably generated from exponential weights, but comprehensive provenance clearance is NOT established for the archival packages and unuploaded files.** Audit archived files before G1A freeze, retain any original SHA-256 and record supersession explicitly if any fixture used exponential weights. No silent regeneration is authorized. This statement is not a claim of independent-person verification.

## Gate

A002 resolves documentation authority only; it does not authorize G1B or establish correctness across all MAR driver configurations. The protocol remains G1A IN PROGRESS, G1B BLOCKED pending Adult source/audit, full fixture provenance, final driver mapping and review.
