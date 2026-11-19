# RMTI v0.1.0 release gate

Status: **PR #2 merged; owner explicitly waived additional external review on 2026-11-19. Software CI passed. Version tag and distribution publication not confirmed by this record.**

## Software gate (all required)
- [x] Minimal public API for MCAR masks, non-mutating masking, and masked-cell metrics.
- [x] Input validation and unit tests committed.
- [x] Python 3.10, 3.11, 3.12 test/build workflow initially passed (run 44407583954).
- [x] Clean-wheel smoke-test workflow passed on Python 3.10–3.12 (run 44408165317).
- [x] Latest CI including legacy compatibility and clean-wheel checks passed on 3.10–3.12 (run 44413362912, 7 tests per Python version).
- [x] Inspected original `rmti.masking` and `rmti.schema`; the new public package is a separate import namespace and both are included in the wheel.
- [x] Legacy compatibility checks and installed-wheel smoke tests pass in CI.
- [x] **Owner waiver — 2026-11-19:** additional independent reviewer is not required for v0.1.0. This waiver accepts residual review risk; it is **not** independent approval.
- [x] CI wheel log lists new public modules and both original `rmti` modules, and both wheel and sdist pass `twine check` (run 44408165317).
- [x] Source distribution expected files checked by CI (run 44413362912).
- [x] Owner explicitly approved MIT; LICENSE committed and CI checks wheel licence inclusion and SPDX `License-Expression: MIT`.
- [x] Project metadata passes `twine check` and new API is documented.
- [x] Metadata, clean-venv import, wheel contents, distribution checks and documented scope validated in CI.
- [x] **Owner waiver covers the remaining human-review checkpoint.** Automated tests do not verify all possible future dependency versions. Artifact origin and reproducibility require separate provenance evidence; a passed CI run alone is not a cryptographic provenance attestation.
- [x] PR #2 merged on 2026-11-19 02:10 UTC (reported merge commit `a79cebbdd4bfac4afa083c24ee01c554e6d29393`).
- [ ] Verify a real Git tag `v0.1.0` points to the intended immutable release commit; a branch or filename is not an equivalent tag.

## Scientific gate (separate, NOT satisfied)
- [ ] R002 complete MAR verification.
- [ ] R003 original Adult dataset byte provenance.
- [ ] Authorised study execution and scientific claims.

The 0.1.0 utility library is **MCAR-only** and must not be advertised as an empirically validated imputation model or as satisfying G1A/G1B.

## Installation from repository
```bash
python -m pip install "git+https://github.com/lonewolf15116/reliable-masked-tabular-imputation.git@a79cebbdd4bfac4afa083c24ee01c554e6d29393"
```

The above is a pinned-commit installation from a private GitHub repository; access credentials are required. It is not a PyPI release.

## Verification record
- CI run: https://github.com/lonewolf15116/reliable-masked-tabular-imputation/actions/runs/44413362912
- Verified candidate commit: `1d4fe14191f6ccc05efd65915850da618396bbd7`
- Automated software release checks: 3/3 Python jobs succeeded; each job checks unit tests, wheel/sdist builds, metadata, clean wheel installation, legacy imports, licence and source archive contents.
- Owner explicitly waived additional independent review on 2026-11-19. No independent reviewer approval is claimed. Scientific gates and provenance checks are unaffected.
- Recorded merge commit `a79cebbdd4bfac4afa083c24ee01c554e6d29393`; GitHub Actions run https://github.com/lonewolf15116/reliable-masked-tabular-imputation/actions/runs/44433840304 succeeded on that commit.
- No tag creation or registry publication asserted by this record.
