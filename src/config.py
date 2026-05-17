"""Project-wide settings for the NYC 311 resolution-time analysis.

This file keeps paths, API settings, and extraction parameters in one place so
the rest of the pipeline can reuse the same values consistently.
"""

from pathlib import Path


# Resolve the main project folder from the location of this config file.
# This avoids hard-coding a local Windows path that would not work on GitHub.
BASE_DIR = Path(__file__).resolve().parents[1]

# Standard project folders for raw data, cleaned data, and generated outputs.
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

# Local SQLite database created by the load step.
DB_PATH = BASE_DIR / "nyc_311.db"

# Create expected folders if they do not already exist.
# This lets the pipeline run on a fresh clone without manual folder setup.
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "tables").mkdir(parents=True, exist_ok=True)

# NYC Open Data Socrata API endpoint for 311 Service Requests from 2020-present.
API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

# Date range used for this code sample. The project focuses on 2024 requests.
START_DATE = "2024-01-01T00:00:00"
END_DATE = "2025-01-01T00:00:00"

# Pull records in large pages to reduce API calls while still using pagination.
PAGE_LIMIT = 50000

# Limit the analysis to the most common complaint types to keep the project
# reproducible and small enough for a code sample.
TOP_N_COMPLAINT_TYPES = 10

# API fields needed for ETL, SQLite feature engineering, and statistical models.
# Keeping this list explicit avoids downloading unnecessary columns.
FIELDS = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "status",
    "location_type",
    "incident_zip",
    "city",
    "borough",
    "community_board",
    "open_data_channel_type",
    "latitude",
    "longitude",
]
