from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

DB_PATH = BASE_DIR / "nyc_311.db"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "tables").mkdir(parents=True, exist_ok=True)

API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

START_DATE = "2024-01-01T00:00:00"
END_DATE = "2025-01-01T00:00:00"

PAGE_LIMIT = 50000
TOP_N_COMPLAINT_TYPES = 10

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