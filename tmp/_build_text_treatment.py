"""Build text-based UK treatment per paper page 14:
Count of 'Brexit', 'Great Britain', 'Uncertainty' in 2015 10-Ks.
Treated = >5 entries; Control = 0 entries."""
import warnings; warnings.filterwarnings("ignore")
import re
import zipfile
from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
ZIP = ROOT / "inputs" / "10-X_C_2015_10Konly.zip"

# Per paper page 14 verbatim:
# "we look for the number of entries of keywords related to uncertainty about
#  Brexit ('Brexit,' 'Great Britain,' and 'Uncertainty') in firms' disclosures"
KEYWORDS = ["Brexit", "Great Britain", "Uncertainty"]

# Parse filename pattern: YYYYMMDD_10-K_edgar_data_CIK_*.txt
fn_pat = re.compile(r"edgar_data_(\d+)_")

results = []
with zipfile.ZipFile(str(ZIP)) as zf:
    names = [n for n in zf.namelist() if n.endswith(".txt")]
    print(f"Total 10-K files: {len(names)}")

    for i, name in enumerate(names):
        m = fn_pat.search(name)
        if not m:
            continue
        cik = int(m.group(1))
        try:
            with zf.open(name) as f:
                text = f.read().decode("utf-8", errors="replace")
        except Exception:
            continue
        # Count keyword occurrences (case-insensitive)
        n_brexit = len(re.findall(r"\bBrexit\b", text, re.IGNORECASE))
        n_gb = len(re.findall(r"\bGreat Britain\b", text, re.IGNORECASE))
        n_unc = len(re.findall(r"\bUncertainty\b", text, re.IGNORECASE))
        total = n_brexit + n_gb + n_unc

        # Get filing date from filename prefix
        date_str = name.split("/")[-1][:8]
        results.append({
            "cik": cik, "filing_date": date_str, "filename": name,
            "n_Brexit": n_brexit, "n_GreatBritain": n_gb, "n_Uncertainty": n_unc,
            "n_total": total
        })

        if (i+1) % 1000 == 0:
            print(f"  Processed {i+1}/{len(names)} ({i*100/len(names):.0f}%)")

df = pd.DataFrame(results)
print(f"\nProcessed {len(df):,} 10-Ks (CIK extracted)")
print(f"Unique CIKs: {df['cik'].nunique():,}")
print(f"\nDistribution of Brexit+GB+Uncertainty counts:")
print(df["n_total"].describe())
print(f"\n% with >5 entries: {(df['n_total']>5).mean()*100:.1f}%")
print(f"% with 0 entries: {(df['n_total']==0).mean()*100:.1f}%")

# Paper benchmark: 807 firms >5 entries, 433 with 0 entries
# Per CIK, take SUM of all 2015 filings (firms may file 10-K + 10-K/A)
firm_counts = df.groupby("cik")["n_total"].sum().reset_index()
firm_counts["TEXT_HIGH_UK"] = (firm_counts["n_total"] > 5).astype(int)
firm_counts["TEXT_LOW_UK"] = (firm_counts["n_total"] == 0).astype(int)
print(f"\nFirm-level (CIK aggregated): {len(firm_counts):,}")
print(f"Paper benchmark: 807 high, 433 low")
print(f"Mine: {firm_counts['TEXT_HIGH_UK'].sum():,} high, {firm_counts['TEXT_LOW_UK'].sum():,} low")

# Save
out_path = ROOT / "outputs" / "campello_v2" / f"text_treatment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
out_path.mkdir(parents=True, exist_ok=True)
firm_counts.to_parquet(out_path / "text_treatment.parquet", index=False)
print(f"\nSaved to {out_path / 'text_treatment.parquet'}")
