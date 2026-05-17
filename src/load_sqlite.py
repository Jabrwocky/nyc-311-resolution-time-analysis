"""Load cleaned NYC 311 data into SQLite and build the model table.

This script is the bridge between the Python cleaning step and the SQL feature
engineering step. It loads the cleaned CSV into SQLite, then runs the SQL script
that adds workload controls for modeling.
"""

import sqlite3

import pandas as pd

from config import BASE_DIR, DB_PATH, PROCESSED_DIR


def main():
    """Create the SQLite database and run SQL feature engineering."""
    clean_path = PROCESSED_DIR / "nyc_311_2024_top10_clean.csv"
    df = pd.read_csv(clean_path)

    with sqlite3.connect(DB_PATH) as conn:
        # Replace the cleaned table each run so the database matches the current
        # processed CSV instead of holding stale results from an earlier pipeline run.
        df.to_sql(
            "service_requests_clean",
            conn,
            if_exists="replace",
            index=False,
        )

        sql_path = BASE_DIR / "sql" / "create_model_table.sql"

        with open(sql_path, "r", encoding="utf-8") as file:
            sql_script = file.read()

        # Run the SQL script that creates the final model-ready table and adds
        # the daily agency-borough workload feature.
        conn.executescript(sql_script)

    print(f"Loaded SQLite database: {DB_PATH}")


if __name__ == "__main__":
    main()
