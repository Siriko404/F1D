"""Phase B template builder — emit CSV with 109 candidates + empty classification columns.

User opens the CSV (Excel/etc), searches obituaries for each row, fills in:
  - is_sudden: 1 if heart attack/accident/stroke/suicide/violence WITHOUT prior decline; 0 if illness
  - age_at_death: integer (for Bennedsen retirement-eligibility cut at 65+)
  - cause_quote: verbatim <=15 words from obituary
  - source_url: obituary URL (primary source)
  - confidence: H/M/L (high/medium/low)
  - notes: optional free-text

Recommended order: tier 3+4 first (19 events). Power gate is borderline:
  109 candidates x 25-40% sudden rate x 80% retention = 22-35 surviving sudden.
  Plan: >=40 GO, 20-39 marginal, <20 DROP. Tier 1 inclusion is the lever.

Output: data/raw/ceo_death_events/sudden_classification_template.csv
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "raw" / "ceo_death_events" / "cross_source_candidates.parquet"
OUT = ROOT / "data" / "raw" / "ceo_death_events" / "sudden_classification_template.csv"


def main():
    df = pd.read_parquet(SRC)

    # User-facing columns for classification
    df["is_sudden"] = ""
    df["age_at_death"] = ""
    df["cause_quote"] = ""
    df["source_url"] = ""
    df["confidence"] = ""
    df["notes"] = ""

    # Order by tier desc then date asc — tier 4 first
    df_sorted = df.sort_values(["tier", "death_date_canonical"], ascending=[False, True])

    cols_priority = [
        "tier", "sources_matched", "q2b_corroborates",
        "gvkey", "exec_name_canonical", "death_date_canonical", "death_date_source",
        "is_sudden", "age_at_death", "cause_quote", "source_url", "confidence", "notes",
        "Q1_detail", "Q2A_detail", "Q3_detail", "Q4_detail",
        "Q1_date", "Q2A_date", "Q3_date", "Q4_date",
        "Q1_event_id", "Q2A_event_id", "Q3_event_id", "Q4_event_id",
        "q2b_evidence",
    ]
    cols_actual = [c for c in cols_priority if c in df_sorted.columns]
    df_sorted[cols_actual].to_csv(OUT, index=False)
    print(f"Wrote {len(df_sorted)} rows to: {OUT}")
    print(f"Tier counts: {df_sorted['tier'].value_counts().sort_index().to_dict()}")


if __name__ == "__main__":
    main()
