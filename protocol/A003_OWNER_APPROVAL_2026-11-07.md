# A003 OWNER APPROVAL — single-anchor MAR design

Recorded 2026-11-07. **Owner explicitly approved A003 in conversation.** This approval applies to the documented A003 per-dataset driver allowlists; it does not infer that downstream experiments are ready or that G1A has passed.

- **Adult**: `age` is the sole never-masked MAR anchor and driver for each other eligible feature. The Adult source/schema and S001/S002 have been audited as separately recorded. Operational Adult mask config, fixed seeds and independent R002 checks still must pass.
- **Bank Marketing (bank-full.csv only)**: `age` sole anchor. **DESIGN APPROVED; NOT OPERATIONAL** pending its own source bytes, schema, split and eligibility verification.
- **California Housing**: `HouseAge` sole anchor. **DESIGN APPROVED; NOT OPERATIONAL** pending its own source/schema, split and eligibility verification.

**Condition 1 — reserved anchors**: Adult `age`, Bank `age`, Housing `HouseAge` cannot themselves be MAR-masked. Exclude them from MAR mask populations and MAR aggregate metrics. A separately preregistered **MCAR-only** experiment may mask them, clearly labelled `MCAR only / MAR not applicable: reserved anchor`. Never silently substitute an MCAR age mask within a MAR result.

**Condition 2 — inferential scope**: all MAR experiments here simulate missingness conditioned **exclusively** on the dataset's designated single anchor. Report as *single-anchor simulated MAR* and do not claim general MAR coverage or causality.

**Condition 3 — operational status**: Adult requires a frozen operational configuration, verified train-only standardized anchor and independent Adult-relevant R002 evidence; external datasets require their own schema/source checks before activation. Dataset-level approval does not imply G1A PASS, pilot authorization, model fitting or any evaluation.

`income`/`y`/`MedHouseVal` downstream targets are never missingness anchors, mask targets or imputation predictors.

**G1A IN PROGRESS; G1B BLOCKED; P001 NOT AUTHORIZED.**
