# NYC 311 Resolution Time Analysis

This project is a Python and SQL analysis of NYC 311 service request resolution times. The main question is:

**Do NYC 311 service requests get resolved at different speeds across boroughs after controlling for complaint type, agency, seasonality, and workload?**

The project uses public NYC Open Data 311 Service Request data, extracts records through the Socrata API, cleans and transforms the data in Python, loads the processed data into SQLite, creates workload features with SQL, and fits statistical models to compare adjusted resolution speed across boroughs.

## Project Overview

A simple comparison of average resolution times can be misleading because different boroughs may have different complaint types, agencies, request volumes, or seasonal patterns. To address this, the analysis controls for:

- complaint type
- responding agency
- month created
- hour created
- weekend status
- daily agency-borough workload

The main outcome is the number of hours between when a request was created and when it was closed. Requests not closed within 90 days are treated as censored observations in the survival analysis.

## Data Source

Data comes from the NYC 311 Service Requests dataset:

- Dataset: 311 Service Requests from 2020 to Present
- Source: NYC Open Data
- API resource ID: `erm2-nwe9`
- Endpoint used: `https://data.cityofnewyork.us/resource/erm2-nwe9.json`

This project uses 2024 records for the ten most common complaint types.

## Methods

The project includes two main models:

1. Log response-time regression
   - Outcome: `log(duration_hours + 1)`
   - Purpose: estimate adjusted differences in expected resolution time.

2. Cox proportional hazards model
   - Outcome: time until request closure
   - Event: request closed within 90 days
   - Purpose: estimate adjusted differences in closure speed.

For the Cox model, hazard ratios above 1 indicate faster closure, while hazard ratios below 1 indicate slower closure.

## Project Structure

```text
nyc-311-resolution-time-analysis/
│
├── src/
│   ├── config.py
│   ├── extract_311.py
│   ├── transform_311.py
│   ├── load_sqlite.py
│   └── analyze_311.py
│
├── sql/
│   └── create_model_table.sql
│
├── data/
│   ├── raw/
│   └── processed/
│
├── outputs/
│   ├── figures/
│   └── tables/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Pipeline

### 1. Extract

`extract_311.py` queries the NYC Open Data API using pagination. It identifies the top ten complaint types in 2024 and downloads matching service request records.

### 2. Transform

`transform_311.py` cleans the raw API output by standardizing date fields, borough names, ZIP codes, complaint types, and agency fields. It also creates the main modeling variables:

- `duration_hours`
- `event_closed_90d`
- `created_month`
- `created_hour`
- `is_weekend`
- `neighborhood_proxy`

### 3. Load

`load_sqlite.py` loads the cleaned data into a local SQLite database.

### 4. SQL Feature Engineering

`create_model_table.sql` creates the final modeling table and adds a workload control:

- `daily_agency_borough_volume`

This measures how many requests an agency received in a borough on a given day.

### 5. Analyze

`analyze_311.py` fits the regression and survival models and saves output tables and figures.

## Outputs

The project produces:

- `outputs/tables/log_duration_model_summary.txt`
- `outputs/tables/cox_model_summary.csv`
- `outputs/figures/adjusted_borough_hazard_ratios.png`

These files are generated locally and are not tracked in Git.

## How to Run

Create a virtual environment and install dependencies:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Create a `.env` file using `.env.example` as a guide:

SOCRATA_APP_TOKEN=your_app_token_here

Then run the full pipeline:

```text
python src/extract_311.py
python src/transform_311.py
python src/load_sqlite.py
python src/analyze_311.py
```

## Notes

The `.env`, raw data, processed data, SQLite database, and generated outputs are excluded from GitHub to avoid uploading credentials or large generated files.

## Limitations

This project is observational and should not be interpreted causally. Adjusted differences in resolution time may reflect unobserved factors not included in the model, such as request severity, staffing differences, local enforcement priorities, or reporting behavior. The neighborhood-level proxy is based on available 311 geographic fields and may not perfectly match lived neighborhood boundaries.
