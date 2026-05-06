"""Geocode F1D firm HQ addresses via Census Batch Geocoder.

For each F1D-panel gvkey, builds modal (add1, city, state, zip5) per period:
  - PRE  = datadate in 2006-2010 (5-yr Hasan pre-window)
  - POST = datadate in 2012-2016 (5-yr Hasan post-redistricting)

Submits to Census Batch Geocoder API
(https://geocoding.geo.census.gov/geocoder/locations/addressbatch),
benchmark Public_AR_Current. Returns lat/lon for each firm-period; saved to
inputs/firm_geocodes/firm_lat_lon.parquet.

Used by H1.6 redistricting DiD TEST 3 — replaces lossy ZCTA-CD crosswalk
path with point-in-polygon spatial join against Lewis 2013 CD shapefiles.

Run once:
    python scripts/adhoc/geocode_firm_hq_addresses.py

Output schema:
    gvkey         str (6-digit)
    period        str ('pre' or 'post')
    add1          str (modal street)
    city          str (modal)
    state         str (modal)
    zip5          str (5-digit modal)
    latitude      float (NaN if no match)
    longitude     float (NaN if no match)
    match_status  str ('Match' / 'Tie' / 'No_Match')
    match_type    str ('Exact' / 'Non_Exact' / blank)
    matched_addr  str
    tiger_line_id str
"""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(".")
PATH_COMP = ROOT / "inputs/comp_na_daily_all/comp_na_daily_all.parquet"
PATH_MANIFEST = ROOT / "outputs/1.4_AssembleManifest/2026-02-19_175609/master_sample_manifest.parquet"
OUT_DIR = ROOT / "inputs/firm_geocodes"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PARQUET = OUT_DIR / "firm_lat_lon.parquet"
INPUT_CSV = OUT_DIR / "geocoder_batch_input.csv"
RESPONSE_CSV = OUT_DIR / "geocoder_batch_response.csv"

PRE_YEARS = range(2006, 2011)   # 2006-2010 inclusive
POST_YEARS = range(2012, 2017)  # 2012-2016 inclusive

CENSUS_BATCH_URL = (
    "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
)
BENCHMARK = "Public_AR_Current"
BATCH_SIZE = 9_500  # Census limit is 10K rows; leave headroom


def load_f1d_gvkeys() -> set[str]:
    """Return set of 6-digit gvkeys present in the F1D earnings-call manifest."""
    m = pd.read_parquet(PATH_MANIFEST, columns=["gvkey"])
    return set(m["gvkey"].astype(str).str.zfill(6).unique())


def load_compustat_addresses(gvkeys: set[str]) -> pd.DataFrame:
    """Load Compustat address rows restricted to F1D gvkeys."""
    cols = ["gvkey", "datadate", "add1", "city", "state", "addzip"]
    df = pd.read_parquet(PATH_COMP, columns=cols)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df = df[df["gvkey"].isin(gvkeys)].copy()
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["year"] = df["datadate"].dt.year
    return df


def modal_per_firm_period(comp: pd.DataFrame, years: range, period_label: str) -> pd.DataFrame:
    """Per gvkey, return modal (add1, city, state, zip5) across the period."""
    sub = comp[comp["year"].isin(list(years))].copy()
    # Strip ZIP+4 suffix
    sub["zip5"] = (
        sub["addzip"].astype(str).str.split("-").str[0].str.zfill(5).str[:5]
    )
    # Drop rows missing key fields
    sub = sub.dropna(subset=["add1", "city", "state"])
    sub = sub[sub["zip5"].str.match(r"^\d{5}$", na=False)].copy()
    if len(sub) == 0:
        return pd.DataFrame(columns=["gvkey", "period", "add1", "city", "state", "zip5"])

    # Modal address per firm: most frequent (add1, city, state, zip5) tuple
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


def build_batch_csv(addresses: pd.DataFrame) -> Path:
    """Write Census-format CSV: unique_id,street,city,state,zip (no header)."""
    out = pd.DataFrame({
        "unique_id": addresses["gvkey"] + "_" + addresses["period"],
        "street": addresses["add1"].astype(str).str.replace(",", " ", regex=False),
        "city": addresses["city"].astype(str).str.replace(",", " ", regex=False),
        "state": addresses["state"].astype(str),
        "zip": addresses["zip5"].astype(str),
    })
    out.to_csv(INPUT_CSV, index=False, header=False)
    print(f"[geocode] batch input written: {INPUT_CSV} ({len(out):,} rows)")
    return INPUT_CSV


def submit_batch(input_csv: Path, response_csv: Path) -> None:
    """Submit Census Batch Geocoder; save response."""
    print(f"[geocode] submitting batch to Census Geocoder ({CENSUS_BATCH_URL})")
    with open(input_csv, "rb") as f:
        files = {"addressFile": (input_csv.name, f, "text/csv")}
        data = {"benchmark": BENCHMARK}
        # Census Batch typically takes 1-5 min for ~5K addresses.
        resp = requests.post(
            CENSUS_BATCH_URL, files=files, data=data, timeout=900
        )
    resp.raise_for_status()
    response_csv.write_bytes(resp.content)
    print(f"[geocode] response saved: {response_csv} ({len(resp.content):,} bytes)")


def parse_response(response_csv: Path) -> pd.DataFrame:
    """Parse Census response CSV.

    Format (no header):
      id, input_address, match_status, match_type, matched_addr, lon_lat,
      tiger_line_id, side
    """
    cols = [
        "unique_id", "input_addr", "match_status", "match_type",
        "matched_addr", "lon_lat", "tiger_line_id", "side",
    ]
    df = pd.read_csv(response_csv, header=None, names=cols, dtype=str, on_bad_lines="warn")
    # split unique_id back into gvkey + period
    parts = df["unique_id"].str.rsplit("_", n=1, expand=True)
    df["gvkey"] = parts[0].str.zfill(6)
    df["period"] = parts[1]
    # split lon,lat
    lonlat = df["lon_lat"].fillna("").str.split(",", expand=True)
    df["longitude"] = pd.to_numeric(lonlat[0], errors="coerce")
    df["latitude"] = pd.to_numeric(lonlat[1] if 1 in lonlat.columns else "", errors="coerce")
    return df


def main() -> None:
    print("[geocode] loading F1D gvkeys + Compustat addresses")
    gvkeys = load_f1d_gvkeys()
    print(f"[geocode] F1D gvkeys: {len(gvkeys):,}")

    comp = load_compustat_addresses(gvkeys)
    print(f"[geocode] Compustat addr rows for F1D firms: {len(comp):,}")

    pre = modal_per_firm_period(comp, PRE_YEARS, "pre")
    post = modal_per_firm_period(comp, POST_YEARS, "post")
    print(f"[geocode] pre-period modal addrs: {len(pre):,}")
    print(f"[geocode] post-period modal addrs: {len(post):,}")

    addr = pd.concat([pre, post], ignore_index=True)
    print(f"[geocode] total firm-period addresses: {len(addr):,}")

    if len(addr) == 0:
        raise SystemExit("[geocode] no addresses to geocode")

    if len(addr) > BATCH_SIZE:
        # Future-proof: chunk into multiple batches if ever > 9500
        raise NotImplementedError(
            f"[geocode] need chunking — got {len(addr):,} > {BATCH_SIZE:,}"
        )

    build_batch_csv(addr)
    submit_batch(INPUT_CSV, RESPONSE_CSV)
    parsed = parse_response(RESPONSE_CSV)

    # Merge geocodes onto modal addrs (latitude/longitude per firm-period)
    keep = parsed[[
        "gvkey", "period", "match_status", "match_type",
        "matched_addr", "tiger_line_id", "longitude", "latitude",
    ]].copy()
    out = addr.merge(keep, on=["gvkey", "period"], how="left")
    out.to_parquet(OUT_PARQUET, index=False)
    print(f"[geocode] saved: {OUT_PARQUET} ({len(out):,} rows)")

    # Diagnostics
    n_match = (out["match_status"] == "Match").sum()
    n_tie = (out["match_status"] == "Tie").sum()
    n_nomatch = (out["match_status"] == "No_Match").sum()
    print(
        f"[geocode] match diagnostics: "
        f"Match={n_match:,} | Tie={n_tie:,} | No_Match={n_nomatch:,}"
    )
    pre_match = ((out["period"] == "pre") & out["latitude"].notna()).sum()
    post_match = ((out["period"] == "post") & out["latitude"].notna()).sum()
    print(
        f"[geocode] non-null lat/lon: pre={pre_match:,}/{len(pre):,} "
        f"post={post_match:,}/{len(post):,}"
    )
    both_periods = (
        out[out["latitude"].notna()]
        .groupby("gvkey")["period"].nunique() == 2
    ).sum()
    print(f"[geocode] firms with BOTH periods geocoded: {both_periods:,}")


if __name__ == "__main__":
    main()
