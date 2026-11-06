# R003 — alternative-source identity investigation (not a source audit)

Recorded 2026-11-07. **SOURCE BYTES UNAVAILABLE; R003 BLOCKED.** We did not replace the Adult dataset or run baseline experiments.

Original UCI file required by locked scope: `https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data` (original 32,561-line Adult training source, not the combined 48,842-row release).

A distinct second access path was attempted: `https://raw.githubusercontent.com/batuhansahincanel/UCIsAdultDataset/main/adult.data`, a publicly displayed GitHub mirror containing a file named `adult.data`. The container could resolve neither this mirror nor the original UCI host; both downloads FAILED with network/DNS connection errors. No bytes acquired, no local SHA-256 computed, no 32,561-row audit performed. This is not confirmation that the mirror bytes match.

**Reference SHA-256 candidate for future verification (not UCI-published):** `5b00264637dbfec36bdeaab5676b0b309ff9eb788d63554ca0a249491c86603d`. Independently displayed by:
- `https://huggingface.co/datasets/wwbrannon/ml-interview-examples-adult/blob/main/meta.json` (metadata source declares this SHA-256 for original UCI adult.data URL);
- `https://pkg.go.dev/github.com/gomlx/gomlx/examples@v0.28.17/adult` (third-party library constant AdultDatasetDataCecksum).

These two third-party references support a check but **do not establish a publisher-issued checksum** and are not sufficient to claim source authenticity without acquiring and hashing actual bytes. If a mirror yields the same SHA-256 and passes format/row-count checks, record its URL, retrieval UTC timestamp, byte length, SHA-256, reference match and reference provenance before any G1A freeze. Until then, the original-source identity requirement is unfulfilled. No raw data committed.
