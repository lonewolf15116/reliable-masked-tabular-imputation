# RMTI competitor differentiation decision — locked protocol (2026-11-19 UTC)

Decision scope: **v0.2 differentiation only**. No changes to scientific G1A/G1B gates or v0.1.0 software review.

This protocol MUST be committed remotely **before** the matched trial code is added or executed. The GitHub commit is the timestamped pre-experiment record; report its exact hash. Private-repository timestamps are visible to authorised readers, not independently public evidence. Do not describe this as public preregistration.

## Decision task
UCI Horse Colic, original `horse-colic.data` (300 rows; not its test/reflected version), source https://archive.ics.uci.edu/ml/machine-learning-databases/horse-colic/horse-colic.data . Download bytes in CI; record SHA-256, UTC time, URL, raw row count. Fail closed on download errors. Evaluate numeric continuous columns only, explicitly select original one-indexed columns 4 (rectal temperature), 5 (pulse), 6 (respiratory rate), 16 (nasogastric reflux pH), 19 (packed cell volume), 20 (total protein), 22 (abdominocentesis total protein). Exclude identifier, outcome, and categorical codes. The real dataset contains natural missing values. These 7 features need not have identical numbers of observations.

Seed values: 11, 23, 37, 53, 71. Independent random 80/20 train/test split per seed; training-only fit. Artificially mask 20% of *observed test values*, exact floor count, identical for all approaches per seed. Score per-column MAE/RMSE on these artificially hidden cells only; do not pool units. Retain per-seed masks and split fingerprint.

Use **one** custom median imputer with fit/transform; for qolmat test native Comparator separately, and explicitly report if that native protocol cannot implement train-only fit and fixed held-out cells. The custom fitted external evaluation is the reference for correctness, not proof that native comparator enforces the contract. For MissMecha test native generator separately; its generated mask may differ and is not automatically "matched" to the fixed mask. Report all unmatched pieces as such.

## Thresholds (defined before execution)
* Setup: human-observed clean-venv + installation + docs reading + first correct comparison <= 45 min = adequate; >=90 min (>=2x) is potential RMTI opportunity. Automated CI install seconds **cannot substitute** for human stopwatch time.
* Custom imputer: <=10 extra adapter LOC and no monkey patch = adequate.
* Leakage: for deployment-style evaluation, train-only fit and split-first masks required. Native APIs that fit evaluation rows without prominently labelled transductive semantics must be reported, but a documented <=10-line external orchestration is adequate, not an automatic differentiator.
* Provenance: dataset raw-byte SHA256, source URL/download UTC, seed, mask parameters, realised per-column mask rates, split fingerprint, dependency versions. <=15 lines of user-side logging adequate; missing fields alone do not demonstrate value.
* Metric correctness: per-column MAE/RMSE on planted small fixture must agree with direct NumPy reference.
* Hard-stop: 2026-12-17 23:59 UTC. Incomplete validation by then -> **FREEZE v0.2**, not extend.

## Explicit competitor-win / freeze rule
**If qolmat OR MissMecha can be brought to the split-first, fit-train-only contract within the setup-time threshold, and the provenance gap is closable with <=15 lines of user-side logging, then RMTI has NO demonstrated v0.2 differentiation: FREEZE v0.2 feature development; maintain only the v0.1.0 scoped teaching/portfolio utility.**

If human setup time or provenance-LOC checks are not measured, the freeze rule has not been empirically evaluated; do not infer a GO. Competing implementations need not be identical, but deviations must be labelled. If a truly material gap emerges, document it first; v0.2 does not automatically become GO without external demand evidence. No v0.2 implementation is authorised by this benchmark.

## Evidence separation
Synthetic persona replies are not verified user demand (0 verified interviews, 0 independently confirmed unmet problems). GitHub CI artifacts are independent execution evidence but do not constitute independent source review. Source is private unless a separately approved public snapshot is created. No public mirror or publication is authorised by this protocol.
