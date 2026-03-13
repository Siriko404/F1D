"""
Investigate SurpDec coverage using the exact Dzielinski et al. recipe:

  SurpPct = (ACTUAL - MEANEST) / Price_5days_before * 100
  SurpDec = binned into -5..0..+5

Ingredients:
  1. IBES Detail -> consensus MEANEST + ACTUAL per (gvkey, fpedats)
  2. CRSP -> share price 5 trading days before the call
  3. Manifest -> call dates
"""
import pandas as pd
import numpy as np
from pathlib import Path

root = Path(__file__).resolve().parents[2]

# =====================================================================
# 1. MANIFEST (Main panel, 2002-2018)
# =====================================================================
manifest = pd.read_parquet(
    root / "outputs" / "1.4_AssembleManifest" / "2026-02-19_175609" / "master_sample_manifest.parquet",
    columns=["file_name", "gvkey", "start_date", "ff12_code"],
)
manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
manifest["start_date"] = pd.to_datetime(manifest["start_date"])
manifest = manifest[~manifest["ff12_code"].isin([8, 11])].copy()
manifest["year"] = manifest["start_date"].dt.year
manifest = manifest[(manifest["year"] >= 2002) & (manifest["year"] <= 2018)].copy()
print(f"Manifest (Main, 2002-2018): {len(manifest):,}")
print(f"Unique gvkeys: {manifest['gvkey'].nunique():,}")

# =====================================================================
# 2. CCM LINKING (CUSIP8 -> gvkey)
# =====================================================================
ccm = pd.read_parquet(
    root / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
    columns=["cusip", "gvkey", "LINKPRIM"],
)
ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
ccm_primary = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
c2g = ccm_primary.drop_duplicates(subset=["cusip8"], keep="first").copy()
c2g["gvkey"] = c2g["gvkey"].astype(str).str.zfill(6)
c2g = c2g.set_index("cusip8")["gvkey"]

# =====================================================================
# 3. IBES DETAIL -> CONSENSUS per (gvkey, fpedats)
# =====================================================================
print("\n--- Loading IBES Detail ---")
ibes_dir = root / "inputs" / "tr_ibes"
chunks = []
for yr in range(2000, 2026):
    f = ibes_dir / f"tr_ibes_{yr}.parquet"
    if not f.exists():
        continue
    df = pd.read_parquet(f)
    eps_q = df[(df["MEASURE"] == "EPS") & (df["FPI"].isin(["6", "7"]))].copy()
    eps_q = eps_q.dropna(subset=["CUSIP", "ACTDATS", "ANALYS", "VALUE", "FPEDATS"])
    eps_q["cusip8"] = eps_q["CUSIP"].astype(str).str[:8]
    eps_q = eps_q[~eps_q["cusip8"].isin(["00000000", "nan", "NaN", "None", ""])]
    eps_q["gvkey"] = eps_q["cusip8"].map(c2g)
    eps_q = eps_q.dropna(subset=["gvkey"])
    eps_q["actdats"] = pd.to_datetime(eps_q["ACTDATS"], errors="coerce")
    eps_q["fpedats"] = pd.to_datetime(eps_q["FPEDATS"], errors="coerce")
    eps_q = eps_q.dropna(subset=["actdats", "fpedats"])
    eps_q["ANALYS"] = pd.to_numeric(eps_q["ANALYS"], errors="coerce")
    eps_q["VALUE"] = pd.to_numeric(eps_q["VALUE"], errors="coerce")
    eps_q["actual"] = pd.to_numeric(eps_q["ACTUAL"], errors="coerce")
    # Also grab announcement date of actual
    if "ANNDATS_ACT" in eps_q.columns:
        eps_q["anndats_act"] = pd.to_datetime(eps_q["ANNDATS_ACT"], errors="coerce")
    else:
        eps_q["anndats_act"] = pd.NaT
    out_cols = ["gvkey", "actdats", "fpedats", "ANALYS", "VALUE", "actual", "anndats_act"]
    chunks.append(eps_q[out_cols])

raw = pd.concat(chunks, ignore_index=True)
print(f"Raw IBES estimates (linked): {len(raw):,}")
print(f"Unique gvkeys: {raw['gvkey'].nunique():,}")

# Keep most recent estimate per (gvkey, fpedats, analyst)
raw = raw.sort_values(["gvkey", "fpedats", "ANALYS", "actdats"])
raw = raw.drop_duplicates(subset=["gvkey", "fpedats", "ANALYS"], keep="last")
print(f"After dedup per analyst: {len(raw):,}")

# Stale filter: drop estimates >180 days from latest in group
latest = raw.groupby(["gvkey", "fpedats"])["actdats"].transform("max")
stale = (latest - raw["actdats"]).dt.days <= 180
raw = raw[stale].copy()
print(f"After stale filter: {len(raw):,}")

# Aggregate consensus per (gvkey, fpedats)
grouped = raw.groupby(["gvkey", "fpedats"]).agg(
    numest=("VALUE", "count"),
    meanest=("VALUE", "mean"),
    actual=("actual", "first"),
    anndats_act=("anndats_act", "first"),
).reset_index()
print(f"Consensus rows (gvkey x fpedats): {len(grouped):,}")

# Filters
f_numest = grouped["numest"] >= 2
f_actual = grouped["actual"].notna()
# NOTE: Dzielinski recipe does NOT require |meanest| >= 0.05 -- the denominator is PRICE not meanest
# But we still need actual to compute surprise
consensus = grouped[f_numest & f_actual].copy()
print(f"After numest>=2 and actual notna: {len(consensus):,}")
print(f"Unique gvkeys in consensus: {consensus['gvkey'].nunique():,}")

# =====================================================================
# 4. MATCH CALLS TO CONSENSUS
# =====================================================================
# Strategy: for each call (gvkey, start_date), find the fpedats that is
# the fiscal period the call is reporting on.
# Earnings calls happen AFTER the fiscal period ends, so we want the
# most recent fpedats that is BEFORE the call date.
print("\n--- Matching calls to IBES consensus ---")

manifest_sorted = manifest.sort_values("start_date")
consensus_sorted = consensus.sort_values("fpedats")

# merge_asof: for each call, find the most recent fpedats <= start_date
merged = pd.merge_asof(
    manifest_sorted[["file_name", "gvkey", "start_date"]],
    consensus_sorted[["gvkey", "fpedats", "meanest", "actual", "anndats_act"]],
    left_on="start_date",
    right_on="fpedats",
    by="gvkey",
    direction="backward",
    tolerance=pd.Timedelta(days=120),  # fiscal period should be within ~1 quarter of call
)

n_matched = merged["actual"].notna().sum()
print(f"Matched (fpedats within 120d before call): {n_matched:,} ({100*n_matched/len(manifest):.1f}%)")

# Check the fpedats-to-call gap distribution
matched_rows = merged[merged["actual"].notna()].copy()
matched_rows["gap_days"] = (matched_rows["start_date"] - matched_rows["fpedats"]).dt.days
print(f"\nGap (call_date - fpedats) distribution:")
print(matched_rows["gap_days"].describe())
for p in [5, 10, 25, 50, 75, 90, 95, 99]:
    print(f"  P{p}: {matched_rows['gap_days'].quantile(p/100):.0f} days")

# Tighter filter: gap should be 0-90 days (call is 0-3 months after fiscal period end)
merged["gap_days"] = (merged["start_date"] - merged["fpedats"]).dt.days
merged.loc[(merged["gap_days"] < 0) | (merged["gap_days"] > 90), "actual"] = np.nan
n_tight = merged["actual"].notna().sum()
print(f"\nAfter 0-90 day gap filter: {n_tight:,} ({100*n_tight/len(manifest):.1f}%)")

# Compute raw surprise (before price scaling)
merged["surprise_raw"] = merged["actual"] - merged["meanest"]

# =====================================================================
# 5. CRSP PRICE AVAILABILITY
# =====================================================================
# Check if we have CRSP daily data to get price 5 days before call
print("\n--- Checking CRSP price availability ---")
crsp_dir = root / "inputs" / "CRSP_DSF"
crsp_files = sorted(crsp_dir.glob("*.parquet")) if crsp_dir.exists() else []
print(f"CRSP DSF files: {len(crsp_files)}")
if crsp_files:
    print(f"First: {crsp_files[0].name}, Last: {crsp_files[-1].name}")
    # Load a sample to see schema
    sample_crsp = pd.read_parquet(crsp_files[0], columns=None)
    print(f"CRSP columns: {list(sample_crsp.columns)}")
    # Check for price columns
    price_cols = [c for c in sample_crsp.columns if "prc" in c.lower() or "price" in c.lower()]
    print(f"Price-related columns: {price_cols}")

# Also check if we already have CRSP data loaded via existing builders
# The manifest might have price data from StockPriceBuilder
print("\n--- Checking StockPrice from existing panel ---")
h03_panel_dir = root / "outputs" / "variables" / "ceo_clarity_extended" / "2026-03-02_223802"
h03_panel_path = h03_panel_dir / "ceo_clarity_extended_panel.parquet"
if h03_panel_path.exists():
    h03_cols = pd.read_parquet(h03_panel_path, columns=None).columns.tolist()
    price_cols_h03 = [c for c in h03_cols if "price" in c.lower() or "stock" in c.lower() or "prc" in c.lower()]
    print(f"H0.3 panel price columns: {price_cols_h03}")

# Check H14 panel which has StockPrice
h14_dirs = sorted((root / "outputs" / "variables" / "h14_bidask_spread").glob("*"))
h14_latest = [d for d in h14_dirs if d.is_dir()]
if h14_latest:
    h14_path = h14_latest[-1] / "h14_bidask_spread_panel.parquet"
    if h14_path.exists():
        h14_panel = pd.read_parquet(h14_path, columns=["file_name", "StockPrice"])
        n_price = h14_panel["StockPrice"].notna().sum()
        print(f"H14 panel StockPrice: {n_price:,}/{len(h14_panel):,} ({100*n_price/len(h14_panel):.1f}%)")

        # Merge price onto our matched calls
        merged_price = merged.merge(h14_panel[["file_name", "StockPrice"]], on="file_name", how="left")
        n_both = (merged_price["actual"].notna() & merged_price["StockPrice"].notna()).sum()
        print(f"\nCalls with BOTH IBES consensus+actual AND StockPrice: {n_both:,} ({100*n_both/len(manifest):.1f}%)")

# =====================================================================
# 6. CRSP PRICE DIRECTLY (for proper 5-day-before price)
# =====================================================================
print("\n--- Loading CRSP for 5-day-before price ---")
# We need PERMNO to link. Check CCM for PERMNO mapping
ccm_full = pd.read_parquet(
    root / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
    columns=["gvkey", "LPERMNO", "LINKPRIM"],
)
ccm_full = ccm_full[ccm_full["LINKPRIM"].isin(["P", "C"])]
ccm_full["gvkey"] = ccm_full["gvkey"].astype(str).str.zfill(6)
g2p = ccm_full.drop_duplicates(subset=["gvkey"], keep="first").set_index("gvkey")["LPERMNO"]
print(f"gvkey->PERMNO mappings: {len(g2p):,}")

# How many manifest gvkeys have PERMNO?
manifest_gvkeys = set(manifest["gvkey"].unique())
has_permno = sum(1 for g in manifest_gvkeys if g in g2p.index)
print(f"Manifest gvkeys with PERMNO: {has_permno:,}/{len(manifest_gvkeys):,}")

# Load CRSP daily for the calls that matched IBES
# We need price at t-5 (5 trading days before call)
# Load just enough CRSP data
calls_need_price = merged[merged["actual"].notna()][["file_name", "gvkey", "start_date"]].copy()
calls_need_price["permno"] = calls_need_price["gvkey"].map(g2p)
calls_need_price = calls_need_price.dropna(subset=["permno"])
calls_need_price["permno"] = calls_need_price["permno"].astype(int)
print(f"Calls needing CRSP price (with PERMNO): {len(calls_need_price):,}")

# Load CRSP data - check structure
if crsp_files:
    # Try loading just one year to understand structure
    crsp_sample = pd.read_parquet(crsp_files[5])  # pick a middle year
    print(f"\nCRSP sample columns: {list(crsp_sample.columns)}")
    print(f"CRSP sample rows: {len(crsp_sample):,}")
    # Show first few rows
    print(crsp_sample.head(3).to_string())

    # Check what identifier is used
    id_cols = [c for c in crsp_sample.columns if "permno" in c.lower() or "cusip" in c.lower() or "ticker" in c.lower()]
    print(f"\nID columns: {id_cols}")

    # Load all CRSP and compute 5-day-before price
    print("\nLoading all CRSP daily data (this may take a while)...")
    crsp_chunks = []
    price_col = None
    for cf in crsp_files:
        cdf = pd.read_parquet(cf)
        # Identify price column
        if price_col is None:
            for candidate in ["PRC", "prc", "PRICE", "price", "close", "CLOSE"]:
                if candidate in cdf.columns:
                    price_col = candidate
                    break
            if price_col is None:
                # Check all columns
                print(f"  Available columns: {list(cdf.columns)}")
                break
        # Identify date column
        date_col = None
        for candidate in ["date", "DATE", "DlyCalDt", "dlycaldt"]:
            if candidate in cdf.columns:
                date_col = candidate
                break
        # Identify permno column
        permno_col = None
        for candidate in ["PERMNO", "permno", "LPERMNO"]:
            if candidate in cdf.columns:
                permno_col = candidate
                break

        if price_col and date_col and permno_col:
            cdf = cdf[[permno_col, date_col, price_col]].copy()
            cdf.columns = ["permno", "date", "price"]
            cdf["date"] = pd.to_datetime(cdf["date"], errors="coerce")
            cdf["price"] = pd.to_numeric(cdf["price"], errors="coerce").abs()  # CRSP uses negative for bid/ask average
            cdf = cdf.dropna()
            cdf["permno"] = cdf["permno"].astype(int)
            crsp_chunks.append(cdf)

    if crsp_chunks:
        crsp = pd.concat(crsp_chunks, ignore_index=True)
        crsp = crsp.sort_values(["permno", "date"])
        print(f"CRSP daily loaded: {len(crsp):,} rows, {crsp['permno'].nunique():,} PERMNOs")

        # For each call, find price 5 trading days before
        # Strategy: for each (permno, call_date), look up the 5th most recent price
        price_results = []
        unique_permnos = calls_need_price["permno"].unique()
        crsp_by_permno = {p: g for p, g in crsp.groupby("permno")}

        processed = 0
        for _, row in calls_need_price.iterrows():
            permno = row["permno"]
            call_date = row["start_date"]
            file_name = row["file_name"]

            if permno not in crsp_by_permno:
                price_results.append({"file_name": file_name, "price_5d": np.nan})
                continue

            firm_prices = crsp_by_permno[permno]
            # Get trading days before call_date
            before = firm_prices[firm_prices["date"] < call_date].tail(5)
            if len(before) >= 5:
                price_5d = before.iloc[0]["price"]  # 5th trading day before
            elif len(before) > 0:
                price_5d = before.iloc[0]["price"]  # use earliest available
            else:
                price_5d = np.nan

            price_results.append({"file_name": file_name, "price_5d": price_5d})
            processed += 1
            if processed % 10000 == 0:
                print(f"  Processed {processed:,} calls...")

        price_df = pd.DataFrame(price_results)
        n_has_price = price_df["price_5d"].notna().sum()
        print(f"\nCalls with CRSP price 5d before: {n_has_price:,}/{len(calls_need_price):,} ({100*n_has_price/len(calls_need_price):.1f}%)")

        # Final coverage: calls with IBES consensus + actual + CRSP price
        final = merged.merge(price_df, on="file_name", how="left")
        has_all = (final["actual"].notna() & final["price_5d"].notna() & (final["price_5d"] > 0)).sum()
        print(f"\n=== FINAL SURPDEC COVERAGE (Dzielinski recipe) ===")
        print(f"Calls with IBES actual+consensus AND price 5d before: {has_all:,}/{len(manifest):,} ({100*has_all/len(manifest):.1f}%)")
    else:
        print("Could not identify CRSP price column")
else:
    print("No CRSP DSF files found")
    print("\n=== IBES-ONLY COVERAGE (without price requirement) ===")
    print(f"Calls with IBES actual+consensus: {n_tight:,}/{len(manifest):,} ({100*n_tight/len(manifest):.1f}%)")
    print("(Price from CRSP would further reduce this)")
