"""Quick diagnostic: does our SP500 vol() construction have bugs?
Check: sprtrn dedup, daily counts, vol series correlation with known values."""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path(".")
MIN_DAYS = 15

# SP500 vol from CRSP sprtrn (our current method)
frames = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["PERMNO", "date", "sprtrn"])
            frames.append(df)
cr = pd.concat(frames, ignore_index=True)
cr["date"] = pd.to_datetime(cr["date"])
cr["sprtrn"] = pd.to_numeric(cr["sprtrn"], errors="coerce")
cr["ym"] = cr["date"].dt.to_period("M")

# Method A: current code - drop_duplicates on all 3 cols
sp = cr[["date", "sprtrn", "ym"]].drop_duplicates()
spg_a = sp.groupby("ym")
sp500_a = spg_a["sprtrn"].std()
sp500_a = sp500_a[spg_a["sprtrn"].count() >= MIN_DAYS]

# Method B: drop_duplicates on date+ym only, keep first sprtrn
sp_b = cr[["date", "sprtrn", "ym"]].drop_duplicates(subset=["date", "ym"])
spg_b = sp_b.groupby("ym")
sp500_b = spg_b["sprtrn"].std()
sp500_b = sp500_b[spg_b["sprtrn"].count() >= MIN_DAYS]

# Check: are there duplicate dates with different sprtrn values?
dup_check = cr.groupby(["date", "ym"])["sprtrn"].nunique()
multi_sprtrn = dup_check[dup_check > 1]
print(f"Dates with multiple distinct sprtrn values: {len(multi_sprtrn)}")
if len(multi_sprtrn) > 0:
    print(f"  Examples: {multi_sprtrn.head(10).to_dict()}")

# Check daily counts per month
daily_counts_a = spg_a["sprtrn"].count()
daily_counts_b = spg_b["sprtrn"].count()
print(f"\nMethod A (drop_duplicates all cols):")
print(f"  Months: {len(sp500_a)}, mean daily obs/month: {daily_counts_a.mean():.1f}")
print(f"  Vol series (first 3): {sp500_a.head(3).values}")
print(f"\nMethod B (drop_duplicates date+ym):")
print(f"  Months: {len(sp500_b)}, mean daily obs/month: {daily_counts_b.mean():.1f}")
print(f"  Vol series (first 3): {sp500_b.head(3).values}")

# Compare: do A and B produce same results?
common = sp500_a.index.intersection(sp500_b.index)
diff = (sp500_a.loc[common] - sp500_b.loc[common]).abs()
print(f"\nMax |A-B|: {diff.max():.6f}, Mean |A-B|: {diff.mean():.6f}")

# Check if any months have inflated daily counts
print(f"\nMethod A months with >23 trading days: {(daily_counts_a > 23).sum()}")
print(f"Method A months with >30 trading days: {(daily_counts_a > 30).sum()}")
if (daily_counts_a > 23).sum() > 0:
    print(f"  Suspicious months: {daily_counts_a[daily_counts_a > 23].to_dict()}")
