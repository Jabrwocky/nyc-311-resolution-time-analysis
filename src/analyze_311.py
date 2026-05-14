import sqlite3
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from lifelines import CoxPHFitter
import matplotlib.pyplot as plt

from config import DB_PATH, OUTPUT_DIR


def load_model_data():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM service_requests_model",
            conn,
        )

    return df


def prep_model_data(df):
    df = df.copy()

    needed = [
        "duration_hours",
        "event_closed_90d",
        "borough",
        "complaint_type",
        "agency",
        "created_month",
        "created_hour",
        "is_weekend",
        "daily_agency_borough_volume",
    ]

    df = df.dropna(subset=needed)

    df["duration_hours"] = pd.to_numeric(df["duration_hours"], errors="coerce")
    df["event_closed_90d"] = pd.to_numeric(df["event_closed_90d"], errors="coerce")
    df["created_month"] = pd.to_numeric(df["created_month"], errors="coerce")
    df["created_hour"] = pd.to_numeric(df["created_hour"], errors="coerce")
    df["is_weekend"] = pd.to_numeric(df["is_weekend"], errors="coerce")
    df["daily_agency_borough_volume"] = pd.to_numeric(
        df["daily_agency_borough_volume"],
        errors="coerce",
    )

    df = df.dropna(subset=needed)

    df["log_duration_hours"] = np.log1p(df["duration_hours"])
    df["log_workload"] = np.log1p(df["daily_agency_borough_volume"])

    complaint_counts = df["complaint_type"].value_counts()
    agency_counts = df["agency"].value_counts()

    df = df[df["complaint_type"].isin(complaint_counts[complaint_counts >= 500].index)]
    df = df[df["agency"].isin(agency_counts[agency_counts >= 500].index)]

    return df


def run_log_regression(df):
    formula = """
    log_duration_hours ~
        C(borough)
        + C(complaint_type)
        + C(agency)
        + C(created_month)
        + created_hour
        + is_weekend
        + log_workload
    """

    model = smf.ols(formula, data=df).fit(cov_type="HC3")

    output_path = OUTPUT_DIR / "tables" / "log_duration_model_summary.txt"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(model.summary().as_text())

    print(model.summary())
    print(f"Saved OLS model summary to {output_path}")

    return model


def run_cox_model(df):
    cox_cols = [
        "duration_hours",
        "event_closed_90d",
        "borough",
        "complaint_type",
        "agency",
        "created_month",
        "created_hour",
        "is_weekend",
        "log_workload",
    ]

    cox_df = df[cox_cols].copy()

    cox_df = pd.get_dummies(
        cox_df,
        columns=[
            "borough",
            "complaint_type",
            "agency",
            "created_month",
        ],
        drop_first=True,
    )

    cph = CoxPHFitter(penalizer=0.05)

    cph.fit(
        cox_df,
        duration_col="duration_hours",
        event_col="event_closed_90d",
    )

    summary = cph.summary.reset_index()
    summary_path = OUTPUT_DIR / "tables" / "cox_model_summary.csv"
    summary.to_csv(summary_path, index=False)

    print(cph.summary)
    print(f"Saved Cox model summary to {summary_path}")

    return cph, summary


def plot_borough_hazard_ratios(cox_summary):
    borough_effects = cox_summary[
        cox_summary["covariate"].str.startswith("borough_")
    ].copy()

    if borough_effects.empty:
        print("No borough terms found in Cox model.")
        return

    borough_effects["borough"] = (
        borough_effects["covariate"]
        .str.replace("borough_", "", regex=False)
    )

    borough_effects = borough_effects.sort_values("exp(coef)")

    plt.figure(figsize=(8, 5))
    plt.scatter(
        borough_effects["exp(coef)"],
        borough_effects["borough"],
    )
    plt.axvline(1, linestyle="--")
    plt.xlabel("Hazard Ratio for Closure")
    plt.ylabel("Borough")
    plt.title("Adjusted 311 Closure Speed by Borough")
    plt.tight_layout()

    fig_path = OUTPUT_DIR / "figures" / "adjusted_borough_hazard_ratios.png"
    plt.savefig(fig_path, dpi=300)
    plt.close()

    print(f"Saved plot to {fig_path}")


def main():
    df = load_model_data()
    df = prep_model_data(df)

    print(f"Modeling rows: {len(df):,}")

    run_log_regression(df)
    cph, cox_summary = run_cox_model(df)
    plot_borough_hazard_ratios(cox_summary)


if __name__ == "__main__":
    main()