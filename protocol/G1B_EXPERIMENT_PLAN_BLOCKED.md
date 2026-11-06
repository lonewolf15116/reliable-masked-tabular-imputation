# G1B experiment plan — PLANNING ONLY, BLOCKED

G1B may begin **only** after a documented G1A PASS with validated Adult source bytes, SHA256, audit, split manifest, finalized feature/anchor masking definitions, training-only preprocessors, masking tests, and decision-ledger approval.

First authorized experimental task after sign-off: compare mean/mode, KNN, MICE and MissForest imputation under frozen MCAR/MAR 10/20/30% masks on Adult development split. Never include income as predictor or mask income. Fit all preprocessors on train only, tune exclusively against validation, and keep original Adult test isolated until explicit test authorization. Log seeds, runtime, per-feature results and uncertainty risk scores. Report no binary downstream NI result; use descriptive A001 template. G1C neural model and G1D test evaluation have their own authorization gates.

Current phase is preparation and audit; this file gives NO authorization to fit any models.
