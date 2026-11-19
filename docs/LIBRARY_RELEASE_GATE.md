# RMTI v0.1.0 release gate

Status: **automated software validation passed; owner waived additional independent reviewer on 2026-11-19. Awaiting merge and release tag. No PyPI publication or GitHub release has occurred.**

## Software gate (all required)
- [x] Minimal public API for MCAR masks, non-mutating masking, and masked-cell metrics.
- [x] Input validation and unit tests committed.
- [x] Python 3.10, 3.11, 3.12 test/build workflow initially passed (run 44407583954).
- [x] Clean-wheel smoke-test workflow passed on Python 3.10–3.12 (run 44408165317).
- [x] Latest CI including legacy compatibility and clean-wheel checks passed on 3.10–3.12 (run 44413362912, 7 tests per Python version).
- [x] Inspected original `rmti.masking` and `rmti.schema`; the new public package is a separate import namespace and both are included in the wheel.
- [x] Legacy compatibility checks and installed-wheel smoke tests pass in CI.
- [x] **Owner waiver (2026-11-19):** additional independent reviewer not required for software v0.1.0. This is a conscious acceptance of residual review risk, **not** an independent approval. Existing technical static review and automated CI remain recorded.
- [x] CI wheel log lists new public modules and both original `rmti` modules, and both wheel and sdist pass `twine check` (run 44408165317).
- [x] Source distribution expected files checked by CI (run 44413362912).
- [x] Owner explicitly approved MIT; LICENSE committed and CI checks wheel licence inclusion and SPDX `License-Expression: MIT`.
- [x] Project metadata passes `twine check` and new API is documented.
- [x] Metadata, clean-venv import, wheel contents, distribution checks and documented scope validated in CI.
- [x] **Owner waiver applies to remaining human-review gate** (2026-11-19). Dependency ranges are unbounded above; automated validation tests the CI-resolved versions only, not every future dependency combination. Provenance is limited to repository commits and GitHub Actions records; no external attestation claimed.
- [ ] Merge reviewed PR #2 and tag its exact release commit as v0.1.0.

## Scientific gate (separate, NOT satisfied)
- [ ] R002 complete MAR verification.
- [ ] R003 original Adult dataset byte provenance.
- [ ] Authorised study execution and scientific claims.

The 0.1.0 utility library is **MCAR-only** and must not be advertised as an empirically validated imputation model or as satisfying G1A/G1B.

## Installation from candidate branch
```bash
python -m pip install "git+https://github.com/lonewolf15116/reliable-masked-tabular-imputation.git@feature/reliable-library-api"
```

The above is a candidate branch installation, not a stable release. Prefer a pinned commit for reproducibility.

## Verification record
- CI run: https://github.com/lonewolf15116/reliable-masked-tabular-imputation/actions/runs/44413362912
- Verified candidate commit: `1d4fe14191f6ccc05efd65915850da618396bbd7`
- Automated software release checks: 3/3 Python jobs succeeded; each job checks unit tests, wheel/sdist builds, metadata, clean wheel installation, legacy imports, licence and source archive contents.
- Owner explicitly waived further independent review on 2026-11-19. No external reviewer approval is claimed. This waiver does not waive functional CI checks, reproducible provenance or scientific gate restrictions.
- Latest passing run at pre-waiver head `cdb791a9a9a5ca33eae58244387471f9affc8867`: https://github.com/lonewolf15116/reliable-masked-tabular-imputation/actions/runs/44413556791
