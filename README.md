# Reliable Masked Tabular Imputation (RMTI)

## Current status
**REVISE — G1A IN PROGRESS; G1B BLOCKED.** R001 closed by inferential scope reduction; R002 full MAR verification is partial and provenance clearance pending; R003 original Adult bytes not verified. No model fitting, baseline fitting or test-set evaluation authorized. Scientific discoveries: 0 confirmed.

Downstream comparisons are descriptive; no binary non-inferiority claim is made, because the prespecified NI procedures failed validation under skewness (see decision ledger).

## G1A documentation authority
A001 and A002 are governing amendments. A002 confirms **clipped-logistic, fixed-count weighted MAR**; any exponential-weight wording in older drafts is stale. MAR driver allowlists, original Adult source integrity, and archival fixture provenance remain to be frozen or verified.

Run `pip install -e ".[test]"` and `pytest` for available masking tests. No test pass authorizes G1B.
