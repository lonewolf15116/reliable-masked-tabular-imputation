# G1A Review Candidate 005 — R001 amendment first; R002 completed

## Commit-order integrity

A001 R001 descriptive-only amendment was recorded as the FIRST local commit, before any new R002 execution (commit `765c24d0b77684c9a3bb8940969880e5a918d51e`). No GitHub remote was configured; this is a local Git evidence record only.

## R002 full MAR distribution test

Previously frozen specification: `evidence/R002_FULL_MAR/R002_MAR_SPEC_LOCK.json`; its SHA256 is `9dbfaceedf21217a243ef9ac25c4cb50d678a45d061d9a495924a2a821741b84`. Ten rows, anchor shared by f1/f2/f3, eligible rows 0–5, exactly 2 masked rows per feature, 60,000 trial masks per feature, 15 categories per feature. The production `generate_mask` function was called for every trial and feature. Reference probabilities were derived from the unordered Plackett–Luce top-2 formula independently of production Gumbel implementation; exact reference SHA256 `fe2605cffa19d44d4513bd7efe95daad180d4cda590c958db1369695b52412ca`.

Original unoptimized runner timed out. The successful runner caches identical deterministic logistic-weight vectors only (1 cached vector), preserving the production generator and RNG sequences. A 20-seed direct comparison of cached vs uncached outputs matched exactly over 3 features; six automated masking tests passed. Performance optimization and its scope are disclosed.

Per-feature Pearson chi-square (df=14) results: f1 9.3882 / p=0.8054, f2 8.7225 / p=0.8484, f3 24.0802 / p=0.04481. Every minimum expected category count was 805.66 (>5). Per the frozen alpha=0.01 rule, 3/3 PASS. This means no detected defect for this anchor-and-eligibility configuration, not proof of the whole masking pipeline. Other MAR driver mappings and independent-person audit remain outside the tested scope.

## R003 source identity

Source URL: https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data . Retrieval failed (DNS NameResolutionError), therefore no file bytes, SHA256, retrieval timestamp for successful download, publisher-checksum comparison, or actual Adult audit. No OpenML or mirror substitution. R003 BLOCKED.

## Decision

R001 CLOSED BY SCOPE REDUCTION (not inferential approval); R002 passed its frozen full-MAR distribution test on tested configuration, but not all independent review goals; R003 BLOCKED. G1A IN PROGRESS; G1B BLOCKED; 0 confirmed scientific discoveries; no model fitting, baseline fitting or test evaluation.
