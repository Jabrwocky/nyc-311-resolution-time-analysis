import sqlite3
import pandas as pd

from config import PROCESSED_DIR, DB_PATH, BASE_DIR


def main():
    clean_path = PROCESSED_DIR / "nyc_311_2024_top10_clean.csv"
    df = pd.read_csv(clean_path)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(
            "service_requests_clean",
            conn,
            if_exists="replace",
            index=False,
        )

        sql_path = BASE_DIR / "sql" / "create_model_table.sql"

        with open(sql_path, "r", encoding="utf-8") as file:
            sql_script = file.read()

        conn.executescript(sql_script)

    print(f"Loaded SQLite database: {DB_PATH}")


if __name__ == "__main__":
    main()