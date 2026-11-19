# RMTI — post-release adoption and maintenance roadmap

**Planning document only, 2026-11-19.** Not approval to alter scientific research gates, publish v0.2, or commercialise the project.

## Baseline: evidence, not assumptions

- Public PyPI package: `reliable-masked-tabular-imputation`; v0.1.0 published using GitHub Actions Trusted Publishing.
- RMTI public utility API: `make_mcar_mask`, `apply_mask`, `masked_mae`, `masked_rmse`.
- Observed public GitHub issues #3–#5 are release-governance/evidence records, not verified external user reports.
- No external consumer, download count, star/fork total, or unique-user count was verified as of this document. **Unknown is not zero.**
- Adoption stats are not real-time and downloads are not distinct users; automated CI/download traffic can affect counts.
- Public source audit discovered a **release provenance reconciliation**: issue #4 and #5 accept exact SHA-256 hashes for the original wheel/sdist and explicitly forbid rebuilding those accepted artifacts; the later PyPI Trusted Publishing workflow checks out the tagged commit and rebuilds new wheels. The resulting PyPI artifact SHA-256 values must be compared with the approved hashes. Successful publishing alone does not resolve this discrepancy.

## P0 — Release evidence and existing-users safety (2026-11-19 onward)

1. Compare PyPI 0.1.0 wheel/sdist SHA-256 to accepted wheel `1a70b24bac9dd6f0873c7ae690e9edabb792946cc7f0fa8e92e716c6da7c635a` and sdist `bab9c94375dfb47ed4002d9910e01b9aae53940f9b95c53a9690e3836e693c7c` (issues #4, #5). If different, record as a provenance deviation without rewriting the historical approval; investigate before another release. Do not overwrite PyPI 0.1.0 filenames.
2. Confirm published PyPI files, provenance/attestations, release notes and actual Git tag target. Record evidence in a new issue.
3. Keep the prior source commit, artifact identities, release governance and scientific restrictions intact; a new release needs a separately approved procedure.
4. Verify `pip install reliable-masked-tabular-imputation==0.1.0` in a clean Python environment and run its README example.

**Exit gate:** reproducible post-publication evidence report; every discrepancy documented, not silently rationalised.

## P1 — Measure adoption without overclaiming (first 14–30 days)

Track once weekly in a dated table:
- PyPI downloads: yesterday, 7-day, 30-day, excluding known mirrors when possible; note collection lag.
- GitHub stars, forks, watchers (if available), unique visitors and clones (traffic graphs), external issues, external PRs and referring sites.
- Verified use: public downstream `requirements.txt`, `pyproject.toml`, import statements, independent reproducible reports or user feedback.
- Distinguish owners' CI installs, mirror/bot activity, external downloads, and **confirmed real external users**.
- Never publish invented adoption numbers. Use 'unavailable' when metrics cannot be retrieved.

**Exit gate:** first evidence-backed 14-day snapshot and a 30-day trend. Primary adoption outcome is one externally verifiable use case or actionable issue, not a vanity download target.

## P2 — Documentation and bug-fix planning for v0.1.1

Documentation-only work may be proposed while research gates are on hold:
- Make `README` clear about public namespace vs experimental legacy `rmti`.
- Add a self-contained synthetic example, full input/output contracts and API reference.
- Add `CHANGELOG.md`, `CITATION.cff`, issue templates, contributor guide, a concise supported-dtypes matrix.
- Plan release regression tests: empty/one-cell/mixed-type tables, pre-existing missing values, zero/full mask rates, duplicate/unsortable labels, nullable integer precision, boolean masks, nonfinite numerical inputs, sampled rates, pandas and NumPy minimum/latest supported versions.
- Prioritise **F-IR-008**: multi-cell MAE/RMSE aggregation around the `2**53` boundary, per issue #5.
- Add tests that explicitly assert invariants; evaluate whether new tests may expose a need for a backwards-compatible patch.

**Exit gate:** reviewed test plan and documentation; no new scientific or benchmarking claims. Code changes for v0.1.1 require normal software review and verified packaging.

## P3 — Conditional v0.1.1 patch release

Only after P0 evidence and scope review: apply narrowly justified compatibility and safety fixes, run CI on Python 3.10–3.12 and minimum/latest supported dependencies, perform clean-wheel import tests, create a provenance record for the exact artifacts, and release with a small documented change log. Avoid redundant republishing if no supported defect exists.

## P4 — v0.2 experimental utilities, HOLD

GitHub issue #4 explicitly records **no v0.2 or commercial activity**, with a freeze deadline of **2026-12-17 23:59 UTC**. Planning may be documented but this is not authorisation for implementation, experiments, or release. After a separate gate decision:
- Evaluate per-column MCAR rate controls and mask summary/reporting (as proposed API changes).
- MAR/MNAR features remain excluded from the public utility API until their separately documented mechanism verification is complete.
- Benchmarking and imputation-estimator functionality require independent experimental authorisation and validation, not merely passing unit tests.

## Priority order and effort guide

| Priority | Proposed work | Approx. focused effort | Measure of success |
|---|---|---|---|
| P0 | Published artifact hash/provenance reconciliation | 0.5–1 day | Exact PyPI hashes compared and decision recorded |
| P1 | Adoption metric snapshot and tracking | 0.5 day setup + weekly updates | Source-linked measurements; zero assumptions |
| P2 | Docs + synthetic tutorial + F-IR-008 test plan | 1–3 days | First-time reproducible example, test matrix |
| P3 | Optional software patch v0.1.1 | 2–4 days if justified | Verified wheel, unchanged research claims |
| P4 | v0.2 research feature proposals | After hold expires AND separate authorisation | Approved spec before experiments |

*Effort estimates are planning approximations, not promises.*

## Public user feedback

Use [GitHub Issues](https://github.com/lonewolf15116/reliable-masked-tabular-imputation/issues) for reproducible bugs and requests. Do not treat internal release-governance issues as outside-user adoption.
