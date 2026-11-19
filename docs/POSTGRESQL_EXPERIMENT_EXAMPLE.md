# Optional PostgreSQL experiment-tracking example

**Scope:** a local, optional demonstration that records a deterministic, synthetic MCAR masking experiment with an observed-column-mean baseline. This is **not** a validated imputation estimator, an endorsement of mean imputation, a MAR/MNAR experiment, or a scientific comparative claim. It does **not** alter the published four-function RMTI public API.

## Requirements

- Python 3.10+ with this repository installed (e.g. `python -m pip install -e ".[test]"`).
- For **database logging only**, install `python -m pip install "psycopg[binary]>=3"`. PostgreSQL and psycopg are intentionally **not** core package dependencies.
- A running PostgreSQL server and a dedicated local database, e.g. `rmti_research`. A least-privileged database user is preferred to the PostgreSQL superuser outside an initial local smoke test.

## Local schema

Run the following SQL in an already-created `rmti_research` database (e.g. with `psql -d rmti_research -U postgres`). These statements are intended for a **new empty development schema**; do not rerun unchanged if the tables already exist.

```sql
CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    method_name TEXT NOT NULL,
    masking_mechanism TEXT NOT NULL CHECK (masking_mechanism = 'MCAR'),
    masking_rate DOUBLE PRECISION NOT NULL CHECK (masking_rate BETWEEN 0 AND 1),
    random_seed BIGINT NOT NULL,
    code_commit TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE evaluation_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL REFERENCES experiments(experiment_id),
    masked_cells BIGINT NOT NULL CHECK (masked_cells > 0),
    mae DOUBLE PRECISION NOT NULL CHECK (mae >= 0 AND mae < 'Infinity'::float8),
    rmse DOUBLE PRECISION NOT NULL CHECK (rmse >= 0 AND rmse < 'Infinity'::float8),
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Run the existing local demonstration

From the repository root:

```powershell
python -m pip install -e .
python -m pip install "psycopg[binary]>=3"
python rmti_experiment.py
```

The current `rmti_experiment.py` is an **interactive local-only example**. It requests the PostgreSQL password using `getpass` and connects to `localhost:5432` with database `rmti_research` and user `postgres`. It makes two database inserts and commits them in one connection transaction. It does not store credentials in the repository, but the local `postgres` superuser is not recommended for production. Avoid running this script unattended or importing it as a library: it executes immediately and prompts for a password.

Each run **creates a new experiment row**, even with the same seed; duplicate IDs are expected. The `code_commit` value is currently `NULL` and is **not** commit-level provenance.

The demonstration creates a synthetic 100-row, three-feature Gaussian dataset with NumPy seed 42, applies a global exact-budget 20% MCAR mask using mask seed 42, imputes using observed-column means, and scores only artificially masked cells.

In the recorded local environment the two executions produced:
- Masked cells: **60** of 300 observed cells.
- Masked-cell MAE: **3.77526901862113**.
- Masked-cell RMSE: **5.803242712249292**.
- PostgreSQL experiment IDs: **2** and **3**.

The repeatability check applies to this **specific deterministic synthetic configuration**, not other machines, NumPy generators, statistical properties, production data or research results.

## Test the calculation without PostgreSQL

```powershell
python -m pip install -e ".[test]"
python -m pytest -q tests/test_synthetic_experiment.py
```

The regression test does not import psycopg, open a database connection, or use a real dataset. The ordinary Python-library CI should continue to pass with no database configured.

## Security and recordkeeping boundaries

- Never commit passwords, `.env`, PGPASSFILE, dumps, production data, or local artifacts.
- Prefer a dedicated PostgreSQL user with INSERT/SELECT access only to the relevant tables and a credential mechanism suited to your environment.
- The example's experiment metadata is **incomplete** for scientific dataset provenance: it does not hash datasets/masks, fingerprint Python/NumPy/pandas versions, capture the Git commit automatically, or record an external validation protocol.
- Preserve the repository's research gates. This local illustration does not authorise MAR/MNAR work, v0.2 development, or comparative scientific conclusions.
- Separate outstanding publication provenance discrepancy: [issue #7](https://github.com/lonewolf15116/reliable-masked-tabular-imputation/issues/7).
