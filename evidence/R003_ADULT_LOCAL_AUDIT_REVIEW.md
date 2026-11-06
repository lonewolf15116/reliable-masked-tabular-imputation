# R003 Adult source acquisition — owner-provided local audit review

Date recorded: 2026-11-07. Source retrieval timestamp reported by the local script: **2026-11-06T23:46:05.024210+00:00**.

## Owner-provided script output

- Download source: https://raw.githubusercontent.com/batuhansahincanel/UCIsAdultDataset/main/adult.data
- Raw byte length: **3,974,305**.
- Local SHA-256 of unmodified source bytes: `5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d`.
- Matches candidate hash independently published in two third-party records: **yes**, according to executed script output.
- UCI-issued checksum comparison: **not performed / not available**.
- Nonempty rows: **32,561**; fields per row: **15**; observed row widths: [15].
- Expected original Adult 15-column schema: matches.
- Six numeric columns inferred as integer: age, fnlwgt, education-num, capital-gain, capital-loss, hours-per-week.
- '?' counts recorded as **observed categorical values**: workclass 1836, occupation 1843, native-country 583, and zero in other columns.
- UTF-8 decoding error: **none**.
- Script reported status: `CANDIDATE_MATCH_NEEDS_REVIEW`.

## Limits and gate

The assistant reviewed **the user's pasted JSON stdout and report**, not the raw dataset bytes or an independently re-run hash computation. This is evidence consistent with candidate source byte-identity as described by third-party records; it is **not** a UCI publisher-issued identity guarantee. The exact local output `artifacts/source/adult_source_audit.json` should be committed (never the raw `adult.data`) and checked against the summary. A complete Adult G1A audit still requires target balance, immutable split assignments and split hash, schema checks, train-only preprocessing statistics, observed-column/eligibility definitions and relevant deterministic tests.

**R003 state: ACQUISITION EVIDENCE RECEIVED / AUDIT INCOMPLETE. Not G1A PASS.** G1B remains blocked; no baseline, model, or test evaluation is authorized.
