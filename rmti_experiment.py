import getpass

import numpy as np
import pandas as pd
import psycopg

from reliable_masked_tabular_imputation import (
    make_mcar_mask,
    apply_mask,
    masked_mae,
    masked_rmse,
)

# Reproducible synthetic data
rng = np.random.default_rng(42)

original = pd.DataFrame({
    "feature_a": rng.normal(10, 2, 100),
    "feature_b": rng.normal(20, 5, 100),
    "feature_c": rng.normal(30, 8, 100),
})

mask = make_mcar_mask(
    original,
    rate=0.20,
    random_state=42,
)

masked = apply_mask(original, mask)

# Baseline: replace missing values with observed column means
imputed = masked.fillna(masked.mean())

mae = masked_mae(original, imputed, mask)
rmse = masked_rmse(original, imputed, mask)
masked_cells = int(mask.to_numpy().sum())

print("Dataset: synthetic, 100 rows, 3 columns")
print("Masked cells:", masked_cells)
print("MAE:", mae)
print("RMSE:", rmse)

# Save measured results into PostgreSQL
password = getpass.getpass("PostgreSQL password: ")

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="rmti_research",
    user="postgres",
    password=password,
) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO experiments (
                experiment_name,
                dataset_name,
                method_name,
                masking_mechanism,
                masking_rate,
                random_seed,
                code_commit
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING experiment_id
            """,
            (
                "RMTI Synthetic MCAR Baseline",
                "synthetic_normal_100x3",
                "observed_column_mean",
                "MCAR",
                0.20,
                42,
                None,
            ),
        )

        experiment_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO evaluation_results (
                experiment_id,
                masked_cells,
                mae,
                rmse
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                experiment_id,
                masked_cells,
                mae,
                rmse,
            ),
        )

    conn.commit()

print("Saved experiment ID:", experiment_id)
