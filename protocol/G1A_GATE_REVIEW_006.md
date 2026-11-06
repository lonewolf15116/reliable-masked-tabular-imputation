# G1A Gate Review 006 — NOT FROZEN

Date: 2026-11-07. Status: REVISE / G1A IN PROGRESS / G1B BLOCKED. This is a review record, not authorization to train, fit baselines, tune on validation, or evaluate tests.

## Governing decision precedence

A001 in `protocol/AMENDMENT_R001_DESCRIPTIVE_ONLY.md` supersedes binary non-inferiority claims in the original `protocol/G1A_DRAFT.md`. The old NI test and binary downstream success requirement are RETIRED, not automatically reinstated by the wording in the still-unfrozen draft. The downstream report is descriptive-only and uses the locked template. Do not interpret a 1% reference line as a threshold.

## Verification conducted for Review 006

- Local tests against the existing archived G1A code: 6/6 current masking battery; 2/3 legacy tests before API reconciliation; 9/9 tests after replacing obsolete `drivers=` with `anchor_data=` in the legacy MAR test. This reconciles the tests to the current API and does not expand scientific validation scope. No training or evaluation was run.
- R002 Review Candidate 005 reports 60,000 sampling trials per masked feature for one single-anchor, three-feature toy MAR setup; 3/3 Pearson tests did not reject at alpha=0.01. This remains a limited configuration and does not prove correctness for all MAR drivers/features.
- R003 direct original UCI Adult source acquisition still fails in this environment due to DNS. No original bytes, primary source SHA-256, 32,561-row identity audit, split indices, or train-fitted preprocessing verification can be reported.
- The original draft and implementation disagree on MAR weighting: draft states weights proportional to `exp(clipped((x-median_train)/IQR_train,-5,5))`, whereas implementation uses clipped logistic scores from a supplied standardized anchor. This is a **protocol/implementation mismatch requiring a signed amendment or implementation correction before freeze**.
- The draft also conflicts with prior decisions on exactly-zero-IQR feature exclusions, 15 paired seeds, and downstream descriptive-only status. It is NOT a frozen executable specification.

## Gate decision

**FAIL_BLOCK_G1B** pending (1) verified source bytes and complete Adult audit, (2) explicit resolution of MAR specification mismatch and final masking design/driver choices, (3) committed evidence and independent scope review of R002, (4) reconciled protocol and split/evaluation settings, and (5) explicit gate sign-off. No model or baseline fitting authorized.

## Next authorized work

Source acquisition from original UCI URL with byte provenance, explicit audited protocol corrections, audit-only scripts, missingness structural/determinism tests, and G1B experiment scaffolding that cannot fit models. No substitute Adult variant or mirror may silently replace the original.

## Subsequent review disposition — A002 (2026-11-07)

The owner confirmed that clipped-logistic MAR was the previously agreed specification. The discrepancy is **stale draft documentation**, not an implementation defect. A002 (`protocol/AMENDMENT_A002_CLIPPED_LOGISTIC.md`) is the authoritative correction and supersedes this review's earlier undecided wording. Existing MAR code is NOT changed to exponential. The audited remote MCAR golden fixture is unaffected by MAR weights, and inspected source tests use clipped-logistic; archive-wide fixture clearance is **not yet established**, and the original SHA hashes must be retained for any later supersession. The README, ledger and descriptive-only template are present on this PR head. G1B remains blocked for R003, provenance, final MAR allowlists and sign-off.
