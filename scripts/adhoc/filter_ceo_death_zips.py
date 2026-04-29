"""One-pass filter: stream zipped WRDS CSVs (no extraction) → write filtered parquet.

Architecture:
  zip → zipfile.open() (file-like stream)
      → pyarrow.csv.open_csv() (multi-threaded streaming CSV parser)
      → iterate RecordBatch → polars DataFrame → filter → buffer
      → write parquet at end

Outputs to data/raw/ceo_death_events/:
  q1_capiq_filtered.parquet              (CapIQ KD death-related events)
  q2_audit_filtered.parquet              (Audit Analytics CEO death events)
  q3a_boardex_individual_filtered.parquet (BoardEx deceased directors)
  q3b_boardex_employment_ceo.parquet     (BoardEx CEO role records)
  recon_summary.json                     (counts + samples)

Filters:
  Q1: keydeveventtypeid IN (16,101,102) AND announcedate ∈ 2002-2018 AND headline regex(death|died|passed away|deceased)
  Q2: is_ceo == 1 AND eff_date ∈ 2002-2018 AND reasons regex(same)
  Q3a: dod is real (not 9999/null) — keep all real deaths regardless of year (we'll filter window after join)
  Q3b: rolename regex(ceo|chief executive)
"""
from __future__ import annotations
import json
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.csv as pa_csv
import polars as pl
import zipfile

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ROOT / "inputs"
OUT = ROOT / "data" / "raw" / "ceo_death_events"
OUT.mkdir(parents=True, exist_ok=True)

DEATH_RE = r"(?i)\bdeath\b|\bdied\b|\bpassed away\b|\bdeceased\b"

WIN_START = "2002-01-01"
WIN_END = "2018-12-31"

BLOCK_SIZE = 64 * 1024 * 1024  # 64 MB CSV-block read buffer


def stream_filter(
    zip_path: Path,
    cols: list[str],
    filter_fn,
    out_parquet: Path,
    label: str,
    string_columns: list[str] | None = None,
) -> dict:
    t0 = time.time()
    print(f"\n[{label}] streaming {zip_path.name} ...", flush=True)
    total_rows = 0
    matched_rows = 0
    buffered: list[pl.DataFrame] = []

    with zipfile.ZipFile(zip_path) as z:
        inner = z.namelist()[0]
        with z.open(inner) as fh:
            read_opts = pa_csv.ReadOptions(use_threads=True, block_size=BLOCK_SIZE)
            column_types = {c: pa.string() for c in (string_columns or [])}
            convert_opts = pa_csv.ConvertOptions(
                include_columns=cols,
                strings_can_be_null=True,
                column_types=column_types,
            )
            parse_opts = pa_csv.ParseOptions(invalid_row_handler=lambda row: "skip")
            reader = pa_csv.open_csv(fh, read_options=read_opts, parse_options=parse_opts, convert_options=convert_opts)
            for batch in reader:
                if batch.num_rows == 0:
                    continue
                total_rows += batch.num_rows
                df = pl.from_arrow(pa.Table.from_batches([batch]))
                m = filter_fn(df)
                if m.height > 0:
                    matched_rows += m.height
                    buffered.append(m)

    if buffered:
        out_df = pl.concat(buffered, how="vertical_relaxed")
        out_df.write_parquet(out_parquet, compression="zstd")
    else:
        out_df = pl.DataFrame(schema={c: pl.Utf8 for c in cols})
        out_df.write_parquet(out_parquet, compression="zstd")

    elapsed = round(time.time() - t0, 1)
    summary = {
        "label": label,
        "input_zip": str(zip_path),
        "output_parquet": str(out_parquet),
        "total_rows_scanned": total_rows,
        "matched_rows": matched_rows,
        "match_rate_pct": round(100.0 * matched_rows / max(total_rows, 1), 4),
        "elapsed_sec": elapsed,
        "throughput_mrows_per_sec": round(total_rows / max(elapsed, 0.01) / 1e6, 3),
    }
    print(f"[{label}] done: {total_rows:,} scanned -> {matched_rows:,} matched in {elapsed}s", flush=True)
    return summary


# ---- Filter functions per source ----

def filter_q1_capiq(df: pl.DataFrame) -> pl.DataFrame:
    # date is string in CSV; cast to date
    return (
        df.with_columns(pl.col("announcedate").str.to_date(strict=False).alias("_d"))
        .filter(
            (pl.col("_d") >= pl.lit(WIN_START).str.to_date())
            & (pl.col("_d") <= pl.lit(WIN_END).str.to_date())
            & pl.col("keydeveventtypeid").is_in([16, 101, 102])
            & pl.col("headline").str.contains(DEATH_RE)
        )
        .drop("_d")
    )


def filter_q2_audit(df: pl.DataFrame) -> pl.DataFrame:
    # is_ceo is Int64 (0/1).
    # `reasons` categorical has only 1 'Deceased' row in entire 357K file (Audit Analytics
    # does NOT systematically code deaths there). Real death info is in do_change_text body.
    # Filter: CEO + window + (death keyword in do_change_text OR reasons in plausible-death
    # categories). High false-positive rate; manual screen required downstream.
    plausible_reasons = ["Deceased", "Personal / Health Reasons", "Personal Reasons", "Other"]
    return (
        df.with_columns(pl.col("eff_date").str.to_date(strict=False).alias("_d"))
        .filter(
            (pl.col("_d") >= pl.lit(WIN_START).str.to_date())
            & (pl.col("_d") <= pl.lit(WIN_END).str.to_date())
            & (pl.col("is_ceo") == 1)
            & (
                pl.col("do_change_text").str.contains(DEATH_RE)
                | pl.col("reasons").is_in(plausible_reasons)
            )
        )
        .drop("_d")
    )


def filter_q3a_boardex_ind(df: pl.DataFrame) -> pl.DataFrame:
    # dod is char. Keep real death dates (not 9999 sentinel, not null), no window filter here.
    return df.filter(
        pl.col("dod").is_not_null()
        & ~pl.col("dod").str.starts_with("9999")
        & ~pl.col("dod").str.starts_with("0001")
    )


def filter_q3b_boardex_emp(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(
        pl.col("rolename").str.contains(r"(?i)ceo|chief executive")
        | pl.col("brdposition").str.contains(r"(?i)ceo|chief executive")
    )


def main():
    summaries = []

    # Q3a smallest first (sanity check the pipeline)
    summaries.append(
        stream_filter(
            zip_path=INPUTS / "BoardEx Individual" / "fwakz2kpthiqwo7k.csv.zip",
            cols=["directorid", "directorname", "forename1", "surname", "dob", "dod", "dodflag", "gender", "nationality"],
            filter_fn=filter_q3a_boardex_ind,
            out_parquet=OUT / "q3a_boardex_individual_filtered.parquet",
            label="Q3a BoardEx Individual",
            string_columns=["dod", "dob"],
        )
    )

    summaries.append(
        stream_filter(
            zip_path=INPUTS / "Directors and Officer Changes" / "u4s63x3i773cgalg.csv.zip",
            cols=["company_fkey", "name", "is_in_sp500", "best_edgar_ticker", "isin", "cusip_number",
                  "title_standard", "is_ceo", "is_cfo", "title_report", "interim", "action", "reasons",
                  "eff_date", "first_name", "middle_name", "last_name", "do_change_text"],
            filter_fn=filter_q2_audit,
            out_parquet=OUT / "q2_audit_filtered.parquet",
            label="Q2 Audit Analytics",
            string_columns=["eff_date"],
        )
    )

    summaries.append(
        stream_filter(
            zip_path=INPUTS / "BoardEx employment" / "f9cpt7kmzuhc8p7l.csv.zip",
            cols=["primarykeyid", "directorid", "directorname", "companyid", "companyname",
                  "rolename", "brdposition", "ned", "leadershipteam", "datestartrole", "dateendrole",
                  "hocountryname", "isin"],
            filter_fn=filter_q3b_boardex_emp,
            out_parquet=OUT / "q3b_boardex_employment_ceo.parquet",
            label="Q3b BoardEx Employment",
            string_columns=["datestartrole", "dateendrole"],
        )
    )

    summaries.append(
        stream_filter(
            zip_path=INPUTS / "KeyDevelopements" / "n9rbimggotfxzglk.csv.zip",
            cols=["gvkey", "announcedate", "companyid", "companyname", "objectroletype",
                  "keydevid", "headline", "keydeveventtypeid", "eventtype", "mostimportantdateutc"],
            filter_fn=filter_q1_capiq,
            out_parquet=OUT / "q1_capiq_filtered.parquet",
            label="Q1 Capital IQ Key Developments",
            string_columns=["announcedate", "mostimportantdateutc"],
        )
    )

    summary_path = OUT / "filter_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2))
    print(f"\nSUMMARY written to {summary_path}")

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    for s in summaries:
        print(f"\n{s['label']}")
        print(f"  scanned: {s['total_rows_scanned']:,}")
        print(f"  matched: {s['matched_rows']:,} ({s['match_rate_pct']}%)")
        print(f"  elapsed: {s['elapsed_sec']}s ({s['throughput_mrows_per_sec']} M rows/sec)")
        print(f"  output:  {s['output_parquet']}")


if __name__ == "__main__":
    main()
