import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

from config import (
    API_URL,
    RAW_DIR,
    START_DATE,
    END_DATE,
    PAGE_LIMIT,
    TOP_N_COMPLAINT_TYPES,
    FIELDS,
)


load_dotenv()


def get_headers():
    app_token = os.getenv("SOCRATA_APP_TOKEN")

    if app_token:
        return {"X-App-Token": app_token}

    return {}


def run_api_query(params):
    response = requests.get(
        API_URL,
        params=params,
        headers=get_headers(),
        timeout=60,
    )

    response.raise_for_status()
    return response.json()


def get_top_complaint_types():
    params = {
        "$select": "complaint_type, count(*) as request_count",
        "$where": (
            f"created_date >= '{START_DATE}' "
            f"AND created_date < '{END_DATE}' "
            "AND complaint_type IS NOT NULL"
        ),
        "$group": "complaint_type",
        "$order": "request_count DESC",
        "$limit": TOP_N_COMPLAINT_TYPES,
    }

    data = run_api_query(params)
    top_types = [row["complaint_type"] for row in data]

    print("Top complaint types:")
    for item in top_types:
        print(f"- {item}")

    return top_types


def escape_soql_string(value):
    return value.replace("'", "''")


def fetch_complaint_type(complaint_type):
    all_rows = []
    offset = 0

    safe_complaint = escape_soql_string(complaint_type)
    field_string = ", ".join(FIELDS)

    while True:
        params = {
            "$select": field_string,
            "$where": (
                f"created_date >= '{START_DATE}' "
                f"AND created_date < '{END_DATE}' "
                f"AND complaint_type = '{safe_complaint}'"
            ),
            "$order": "created_date, unique_key",
            "$limit": PAGE_LIMIT,
            "$offset": offset,
        }

        rows = run_api_query(params)

        if not rows:
            break

        all_rows.extend(rows)

        print(
            f"{complaint_type}: fetched {len(rows):,} rows "
            f"at offset {offset:,}"
        )

        if len(rows) < PAGE_LIMIT:
            break

        offset += PAGE_LIMIT
        time.sleep(0.2)

    return all_rows


def main():
    top_types = get_top_complaint_types()

    all_rows = []

    for complaint_type in top_types:
        rows = fetch_complaint_type(complaint_type)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)

    output_path = RAW_DIR / "nyc_311_2024_top10_raw.csv"
    df.to_csv(output_path, index=False)

    print(f"\nSaved {len(df):,} rows to {output_path}")


if __name__ == "__main__":
    main()