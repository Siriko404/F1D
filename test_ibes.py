import pandas as pd
import numpy as np
from pathlib import Path
from f1d.shared.path_utils import get_latest_output_dir

root_path = Path(".")
ibes_path = root_path / "inputs" / "tr_ibes" / "tr_ibes.parquet"
ccm_path = root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"

manifest_dir = get_latest_output_dir(
    root_path / "outputs" / "1.4_AssembleManifest",
    required_file="master_sample_manifest.parquet",
)
manifest_path = manifest_dir / "master_sample_manifest.parquet"

print("Loading manifest...")
manifest = pd.read_parquet(manifest_path, columns=["file_name", "gvkey", "start_date"])
manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
manifest["start_date"] = pd.to_datetime(manifest["start_date"])

print("Loading IBES...")
ibes = pd.read_parquet(
    ibes_path,
    columns=[
        "MEASURE",
        "FISCALP",
        "TICKER",
        "CUSIP",
        "FPEDATS",
        "STATPERS",
        "MEANEST",
        "ACTUAL",
    ],
)
ibes = ibes.loc[(ibes["MEASURE"] == "EPS") & (ibes["FISCALP"] == "QTR")].copy()
ibes = ibes[["CUSIP", "FPEDATS", "STATPERS", "MEANEST", "ACTUAL"]].copy()
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"], errors="coerce")
ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"], errors="coerce")
ibes["surprise_raw"] = ibes["ACTUAL"] - ibes["MEANEST"]
ibes["cusip8"] = ibes["CUSIP"].astype(str).str[:8]

print("Loading CCM...")
ccm = pd.read_parquet(ccm_path, columns=["cusip", "LPERMNO", "gvkey"])
ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm_cusip = ccm[["cusip8", "gvkey"]].drop_duplicates().dropna()

ibes_linked = ibes.merge(ccm_cusip, on="cusip8", how="inner")

ibes_cols = ibes_linked[["gvkey", "STATPERS", "FPEDATS", "surprise_raw"]].dropna(
    subset=["STATPERS", "FPEDATS", "surprise_raw"]
)

# Vectorized approach testing
print("Testing vectorized approach...")

# merge on gvkey
merged = pd.merge(
    manifest[["file_name", "gvkey", "start_date"]], ibes_cols, on="gvkey", how="inner"
)

# filter by FPEDATS within 45 days
window = pd.Timedelta(days=45)
fpedats_valid = (merged["FPEDATS"] >= merged["start_date"] - window) & (
    merged["FPEDATS"] <= merged["start_date"] + window
)
merged_fpedats = merged[fpedats_valid].copy()

# filter by STATPERS <= start_date
statpers_valid = merged_fpedats["STATPERS"] <= merged_fpedats["start_date"]
merged_valid = merged_fpedats[statpers_valid].copy()

# get max STATPERS per call
merged_valid = merged_valid.sort_values(["file_name", "STATPERS"])
final_matches = merged_valid.drop_duplicates(subset=["file_name"], keep="last")

matched = len(final_matches)
print(f"Matched {matched} calls out of {len(manifest)}")
