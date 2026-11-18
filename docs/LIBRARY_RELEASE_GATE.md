# RMTI v0.1.0 release gate

Status: **candidate only; no PyPI publication or GitHub release authorised by this file.**

## Software gate (all required)
- [x] Minimal public API for MCAR masks, non-mutating masking, and masked-cell metrics.
- [x] Input validation and unit tests committed.
- [x] Python 3.10, 3.11, 3.12 test/build workflow initially passed (run 44407583954).
- [x] Clean-wheel smoke-test workflow passed on Python 3.10–3.12 (run 44408165317).
- [ ] Latest workflow including legacy-namespace compatibility checks passes (run 44408514947; pending at review time).
- [x] Inspected original `rmti.masking` and `rmti.schema`; the new public package is a separate import namespace and both are included in the wheel.
- [ ] Final CI compatibility tests pass and an independent reviewer checks the two API contracts.
- [x] CI wheel log lists new public modules and both original `rmti` modules, and both wheel and sdist pass `twine check` (run 44408165317).
- [ ] Explicit audit of the source distribution contents beyond metadata validation.
- [ ] Adopt and verify an explicit software licence (owner decision required).
- [x] Project metadata passes `twine check` and new API is documented.
- [ ] Final review of dependency upper-bound policy, external documentation, clean-venv consistency and release provenance.
- [ ] Tag a reviewed, immutable release commit.

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
