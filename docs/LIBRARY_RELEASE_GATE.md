# RMTI v0.1.0 release gate

Status: **candidate only; no PyPI publication or GitHub release authorised by this file.**

## Software gate (all required)
- [x] Minimal public API for MCAR masks, non-mutating masking, and masked-cell metrics.
- [x] Input validation and unit tests committed.
- [x] Python 3.10, 3.11, 3.12 test/build workflow initially passed (run 44407583954).
- [ ] Latest workflow after clean-wheel smoke-test change passes.
- [ ] Independent reviewer confirms prior code/API compatibility and confirms no accidental duplicate/conflicting package names.
- [ ] Confirm all expected files are present in wheel and source distribution.
- [ ] Adopt and verify an explicit software licence (owner decision required).
- [ ] Validate release naming, metadata, dependency ranges, documentation and reproducibility.
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
