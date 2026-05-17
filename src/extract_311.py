"""Extract NYC 311 service request data from the Socrata API.

This script identifies the ten most common 2024 complaint types and downloads
matching service request records in paginated API calls.
"""

import os
import time

import pandas as pd
import requests
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
    """Return API headers with the Socrata app token when one is available."""
    app_token = os.getenv("SOCRATA_APP_TOKEN")

    if app_token:
        return {"X-App-Token": app_token}

    return {}


def run_api_query(params):
    """Submit one API request and return the JSON response."""
    response = requests.get(
        API_URL,
        params=params,
        headers=get_headers(),
        timeout=60,
    )

    # Fail immediately if the API returns an error so bad data is not saved.
    response.raise_for_status()

    return response.json()


def get_top_complaint_types():
    """Find the highest-volume complaint types in the selected date range."""
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
    """Escape apostrophes so complaint names can be safely used in SoQL."""
    return value.replace("'", "''")


def fetch_complaint_type(complaint_type):
    """Download all records for one complaint type using limit/offset paging."""
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

        # An empty page means there are no more records to retrieve.
        if not rows:
            break

        all_rows.extend(rows)

        print(
            f"{complaint_type}: fetched {len(rows):,} rows "
            f"at offset {offset:,}"
        )

        # A short final page means the query has reached the end of the result set.
        if len(rows) < PAGE_LIMIT:
            break

        offset += PAGE_LIMIT

        # Pause briefly to avoid hammering the public API during pagination.
        time.sleep(0.2)

    return all_rows


def main():
    """Run extraction and save the raw API data as a CSV file."""
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
