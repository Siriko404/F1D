"""Geocode FULL Compustat firm-HQ universe via Census Batch Geocoder (TEST 5).

Companion to geocode_firm_hq_addresses.py — that one was restricted to the
F1D earnings-call panel (~2,500 firms; 4,308 firm-period addresses). This
extends the pipeline to ALL Compustat firms with quarterly data in the
2006-2015 window after Hasan SIC exclusions (~12K firms; 24K firm-period
addresses).

Required for TEST 5 (H1.6 redistricting DiD on full-Compustat panel) per
plan @ ~/.claude/plans/tender-popping-origami.md Phase 5 ACTIVE SCOPE.

Output:
    inputs/firm_geocodes/firm_lat_lon_full_compustat.parquet

Run once:
    python scripts/adhoc/geocode_full_compustat_hq.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

ROOT = Path(".")
PATH_COMP = ROOT / "inputs/comp_na_daily_all/comp_na_daily_all.parquet"
OUT_DIR = ROOT / "inputs/firm_geocodes"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PARQUET = OUT_DIR / "firm_lat_lon_full_compustat.parquet"

PRE_YEARS = range(2006, 2011)
POST_YEARS = range(2012, 2017)

CENSUS_BATCH_URL = (
    "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
)
BENCHMARK = "Public_AR_Current"
BATCH_SIZE = 9_500  # Census limit ~10K


def _is_excluded_sic(sic_int: int) -> bool:
    return (6000 <= sic_int <= 6999) or (4900 <= sic_int <= 4999)


def load_full_compustat_addresses() -> pd.DataFrame:
    """Load Compustat addresses; apply Hasan SIC exclusions; restrict to
    firms active in 2006-2015 window."""
    cols = ["gvkey", "datadate", "sic", "add1", "city", "state", "addzip"]
    df = pd.read_parquet(PATH_COMP, columns=cols)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["year"] = df["datadate"].dt.year
    df = df[df["year"].between(2006, 2016)].copy()

    # Apply Hasan SIC exclusions
    df["sic_int"] = pd.to_numeric(df["sic"], errors="coerce")
    df = df[df["sic_int"].notna()].copy()
    df["sic_int"] = df["sic_int"].astype(int)
    df = df[~df["sic_int"].apply(_is_excluded_sic)].copy()
    return df


def modal_per_firm_period(comp: pd.DataFrame, years: range, period_label: str) -> pd.DataFrame:
    """Modal address per (gvkey, period)."""
    sub = comp[comp["year"].isin(list(years))].copy()
    sub["zip5"] = (
        sub["addzip"].astype(str).str.split("-").str[0].str.zfill(5).str[:5]
    )
    sub = sub.dropna(subset=["add1", "city", "state"])
    sub = sub[sub["zip5"].str.match(r"^\d{5}$", na=False)].copy()
    if len(sub) == 0:
        return pd.DataFrame(columns=["gvkey", "period", "add1", "city", "state", "zip5"])
    grouped = (
        sub.groupby(["gvkey", "add1", "city", "state", "zip5"])
        .size()
        .reset_index(name="n")
        .sort_values(["gvkey", "n"], ascending=[True, False])
    )
    modal = grouped.drop_duplicates(subset=["gvkey"], keep="first")[
        ["gvkey", "add1", "city", "state", "zip5"]
    ].copy()
    modal["period"] = period_label
    return modal[["gvkey", "period", "add1", "city", "state", "zip5"]]


def submit_batch(input_csv: Path, response_csv: Path) -> None:
    print(f"[geocode-full] submitting {input_csv.name} (size {input_csv.stat().st_size / 1024:.0f} KB)")
    with open(input_csv, "rb") as f:
        files = {"addressFile": (input_csv.name, f, "text/csv")}
        data = {"benchmark": BENCHMARK}
        resp = requests.post(
            CENSUS_BATCH_URL, files=files, data=data, timeout=900
        )
    resp.raise_for_status()
    response_csv.write_bytes(resp.content)
    print(f"[geocode-full] response saved: {response_csv} ({len(resp.content):,} bytes)")


def parse_response(response_csv: Path) -> pd.DataFrame:
    cols = [
        "unique_id", "input_addr", "match_status", "match_type",
        "matched_addr", "lon_lat", "tiger_line_id", "side",
    ]
    df = pd.read_csv(
        response_csv, header=None, names=cols, dtype=str, on_bad_lines="warn",
    )
    parts = df["unique_id"].str.rsplit("_", n=1, expand=True)
    df["gvkey"] = parts[0].str.zfill(6)
    df["period"] = parts[1]
    lonlat = df["lon_lat"].fillna("").str.split(",", expand=True)
    df["longitude"] = pd.to_numeric(lonlat[0], errors="coerce")
    df["latitude"] = pd.to_numeric(lonlat[1] if 1 in lonlat.columns else "", errors="coerce")
    return df


def main() -> None:
    print("[geocode-full] loading full Compustat addresses (Hasan SIC excl.)")
    comp = load_full_compustat_addresses()
    print(f"[geocode-full] Compustat addr rows after exclusions: {len(comp):,}")
    print(f"[geocode-full] unique gvkeys: {comp['gvkey'].nunique():,}")

    pre = modal_per_firm_period(comp, PRE_YEARS, "pre")
    post = modal_per_firm_period(comp, POST_YEARS, "post")
    print(f"[geocode-full] pre-period modal addrs: {len(pre):,}")
    print(f"[geocode-full] post-period modal addrs: {len(post):,}")

    addr = pd.concat([pre, post], ignore_index=True).reset_index(drop=True)
    print(f"[geocode-full] total firm-period addresses: {len(addr):,}")

    # Build batch input
    out_input_full = pd.DataFrame({
        "unique_id": addr["gvkey"] + "_" + addr["period"],
        "street": addr["add1"].astype(str).str.replace(",", " ", regex=False),
        "city": addr["city"].astype(str).str.replace(",", " ", regex=False),
        "state": addr["state"].astype(str),
        "zip": addr["zip5"].astype(str),
    })

    # Chunk into batches of BATCH_SIZE
    n_batches = (len(out_input_full) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"[geocode-full] submitting in {n_batches} batches of <= {BATCH_SIZE:,}")

    parsed_chunks = []
    for i in range(n_batches):
        start = i * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(out_input_full))
        chunk = out_input_full.iloc[start:end]
        in_path = OUT_DIR / f"geocoder_full_input_batch{i:02d}.csv"
        rsp_path = OUT_DIR / f"geocoder_full_response_batch{i:02d}.csv"
        chunk.to_csv(in_path, index=False, header=False)
        if rsp_path.exists() and rsp_path.stat().st_size > 1000:
            print(f"[geocode-full] batch {i+1}/{n_batches}: response cached ({rsp_path})")
        else:
            submit_batch(in_path, rsp_path)
        parsed_chunks.append(parse_response(rsp_path))

    parsed = pd.concat(parsed_chunks, ignore_index=True)
    print(f"[geocode-full] total parsed responses: {len(parsed):,}")

    # Merge geocodes onto modal addrs
    keep = parsed[[
        "gvkey", "period", "match_status", "match_type",
        "matched_addr", "tiger_line_id", "longitude", "latitude",
    ]].copy()
    out = addr.merge(keep, on=["gvkey", "period"], how="left")
    out.to_parquet(OUT_PARQUET, index=False)
    print(f"[geocode-full] saved: {OUT_PARQUET} ({len(out):,} rows)")

    n_match = (out["match_status"] == "Match").sum()
    n_tie = (out["match_status"] == "Tie").sum()
    n_nomatch = (out["match_status"] == "No_Match").sum()
    print(
        f"[geocode-full] match diagnostics: "
        f"Match={n_match:,} | Tie={n_tie:,} | No_Match={n_nomatch:,}"
    )
    pre_match = ((out["period"] == "pre") & out["latitude"].notna()).sum()
    post_match = ((out["period"] == "post") & out["latitude"].notna()).sum()
    print(
        f"[geocode-full] non-null lat/lon: pre={pre_match:,}/{len(pre):,} "
        f"post={post_match:,}/{len(post):,}"
    )
    both_periods = (
        out[out["latitude"].notna()]
        .groupby("gvkey")["period"].nunique() == 2
    ).sum()
    print(f"[geocode-full] firms with BOTH periods geocoded: {both_periods:,}")


if __name__ == "__main__":
    main()
