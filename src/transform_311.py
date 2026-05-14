import numpy as np
import pandas as pd

from config import RAW_DIR, PROCESSED_DIR


VALID_BOROUGHS = {
    "BRONX",
    "BROOKLYN",
    "MANHATTAN",
    "QUEENS",
    "STATEN ISLAND",
}

MAX_FOLLOWUP_DAYS = 90


def clean_zip(value):
    """Standardize ZIP codes as 5-character strings."""
    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if len(value) >= 5:
        return value[:5]

    return np.nan


def main():
    raw_path = RAW_DIR / "nyc_311_2024_top10_raw.csv"
    df = pd.read_csv(raw_path, dtype=str)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    df["created_datetime"] = pd.to_datetime(
        df["created_date"],
        errors="coerce",
    )

    df["closed_datetime"] = pd.to_datetime(
        df["closed_date"],
        errors="coerce",
    )

    df["borough"] = df["borough"].str.upper().str.strip()
    df["agency"] = df["agency"].str.upper().str.strip()
    df["complaint_type"] = df["complaint_type"].str.strip()
    df["descriptor"] = df["descriptor"].str.strip()
    df["status"] = df["status"].str.upper().str.strip()
    df["incident_zip"] = df["incident_zip"].apply(clean_zip)

    df = df[df["created_datetime"].notna()]
    df = df[df["borough"].isin(VALID_BOROUGHS)]

    df["followup_end"] = (
        df["created_datetime"] + pd.Timedelta(days=MAX_FOLLOWUP_DAYS)
    )

    df["event_closed_90d"] = np.where(
        df["closed_datetime"].notna()
        & (df["closed_datetime"] <= df["followup_end"]),
        1,
        0,
    )

    df["observed_end"] = np.where(
        df["event_closed_90d"] == 1,
        df["closed_datetime"],
        df["followup_end"],
    )

    df["observed_end"] = pd.to_datetime(df["observed_end"])

    df["duration_hours"] = (
        df["observed_end"] - df["created_datetime"]
    ).dt.total_seconds() / 3600

    df = df[df["duration_hours"].notna()]
    df = df[df["duration_hours"] >= 0]

    df["created_date_only"] = df["created_datetime"].dt.date.astype(str)
    df["created_month"] = df["created_datetime"].dt.month
    df["created_hour"] = df["created_datetime"].dt.hour
    df["created_day_of_week"] = df["created_datetime"].dt.day_name()
    df["is_weekend"] = (
        df["created_datetime"].dt.dayofweek.isin([5, 6]).astype(int)
    )

    df["community_board_clean"] = (
        df["community_board"]
        .astype(str)
        .str.upper()
        .str.strip()
        .replace({"NAN": np.nan, "UNSPECIFIED": np.nan})
    )

    df["neighborhood_proxy"] = df["community_board_clean"].fillna(
        df["incident_zip"]
    )

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    keep_cols = [
        "unique_key",
        "created_datetime",
        "closed_datetime",
        "observed_end",
        "duration_hours",
        "event_closed_90d",
        "agency",
        "agency_name",
        "complaint_type",
        "descriptor",
        "status",
        "borough",
        "incident_zip",
        "community_board_clean",
        "neighborhood_proxy",
        "created_date_only",
        "created_month",
        "created_hour",
        "created_day_of_week",
        "is_weekend",
        "open_data_channel_type",
        "latitude",
        "longitude",
    ]

    df = df[keep_cols]

    output_path = PROCESSED_DIR / "nyc_311_2024_top10_clean.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved cleaned data: {output_path}")
    print(f"Rows: {len(df):,}")
    print(df[["duration_hours", "event_closed_90d"]].describe())


if __name__ == "__main__":
    main()