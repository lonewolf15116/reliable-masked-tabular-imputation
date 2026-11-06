# A002 fixture-provenance enumeration — 2026-11-07

Scope examined: container-mounted original evidence ZIPs Review Candidates 001, 002, 003, 004, 005, and GitHub Upload Ready 005, including the surviving R002 tests, source files, result JSON, sealed references, and SHA-256 manifests. This record is an actual enumeration of **available archived materials**, not a statement about unknown external files.

## Findings by artifact class

1. `tests/golden_mask_mcar_seed17.csv` and `evidence/R002_REFERENCE_MASK.csv`: same MCAR mask bytes in archived bundle. SHA-256 `dc6c1d70ec9687fb21fbcc8a94a0fa91eae91ef3994b102a0988fee69edd92b0`. MCAR uses constant selection weights, so its top-k selection law is uniform regardless of how a **MAR** probability function is parameterized. No MAR exponential/logistic supersession is needed for this MCAR fixture. Its derivation's independence from the implementation is a separate unresolved review issue.
2. `evidence/R002_ENUM_RESULTS.json`: independent toy weighted-top-k enumeration, six categories, not an exponential-MAR fixture; SHA-256 `92dde3ff87371db8d169b632f7347865831d963c3e33d273304a7636a413fce4`.
3. `evidence/R002_FULL_MAR/R002_MAR_REFERENCE_SEALED.json`: MAR anchor vector and **explicit calibrated logistic weights** recorded; SHA-256 `fe2605cffa19d44d4513bd7efe95daad180d4cda590c958db1369695b52412ca`.
4. `evidence/R002_FULL_MAR/R002_MAR_RESULTS.json`: **five MAR-derived seeded fixtures** for f1/f2/f3 (seeds 200000–200004), paired with the clipped-logistic MAR experiment. SHA-256 `78a2e3cfe36a493919fef3245754b5cff41c5c3e4c6b7fdbd86d0a987c3a5a94`.
5. `evidence/R002_FULL_MAR/R002_MAR_SPEC_LOCK.json`: single-anchor, three-feature MAR scenario explicitly locked with slope=1, clip bounds and 60,000 samples/feature. SHA-256 `9dbfaceedf21217a243ef9ac25c4cb50d678a45d061d9a495924a2a821741b84`.
6. `evidence/R002_FULL_MAR/R002_EXECUTION.py`, `R002_CACHED_RUNNER.py` and `src/rmti/masking.py`: archived scripts use the clipped-logistic probability calculation, not exponential MAR weights. Source-file SHA-256 values appear in the archived Review Candidate 005 manifest. No alternate exponential-MAR generator code or fixture was found in this enumerated material.
7. Review Candidate 004 is a separate simulation-evidence ZIP whose R002 reference concerns the same logistic test; no prior exponential-derived mask fixture identified.

## Decision

**No MAR-derived fixture generated from exponential MAR weighting was found in the enumerated available archives.** The archived MAR-derived fixtures that do exist are under clipped-logistic weights, and their original SHA-256 values are preserved above. Thus no fixture was silently regenerated or superseded by this review. This closes **A002 weighting-provenance within the enumerated archive set**, while not certifying unexamined external materials or independent reviewer authorship. Note that some of these fixtures predate the *documentation* amendment A002, but not the previously agreed clipped-logistic design.

MAR driver-allowlist finalization is **not** closed. The single anchor `anchor` for synthetic f1/f2/f3 is a test case, not an approved per-dataset allowlist. No claim about Adult or Bank feature-specific allowlists may be inferred.
