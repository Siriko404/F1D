"""Check costat impact on sample N."""
import pandas as pd

p = pd.read_parquet("inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                     columns=["gvkey","datadate","curcdq","loc","consol","indfmt","datafmt","costat","fic","sic","atq","cshoq","prccq"])
p["gvkey"] = p["gvkey"].astype(str).str.zfill(6)
p["datadate"] = pd.to_datetime(p["datadate"])
for col in ["atq","cshoq","prccq","sic"]:
    p[col] = pd.to_numeric(p[col], errors="coerce")

# Apply my current filters
fisc = p["curcdq"].eq("USD") & p["loc"].eq("USA")
fmt = p["consol"].eq("C") & p["indfmt"].eq("INDL") & p["datafmt"].eq("STD")
p = p[fisc & fmt]
p = p[(p["datadate"] >= "2010-01-01") & (p["datadate"] <= "2016-12-31")]
sic = p["sic"]
is_ut = (sic >= 4900) & (sic <= 4999)
is_fin = (sic >= 6000) & (sic <= 6799)
p = p[~(is_ut | is_fin)]
p["mktcap"] = p["cshoq"] * p["prccq"]
too_small = (p["mktcap"] < 10) | (p["atq"] < 10)
p = p[~too_small]

print(f"Without costat filter: {len(p):,}")

# Check costat values
print(f"\ncostat value counts:")
print(p["costat"].value_counts())

# With costat='A'
pA = p[p["costat"] == "A"]
print(f"\nWith costat='A': {len(pA):,}")

# Also check fic
print(f"\nfic value counts (top 10):")
print(p["fic"].value_counts().head(10))

# With fic='USA' AND loc='USA'
p_fic = p[p["fic"] == "USA"]
print(f"\nWith fic='USA' (on top of loc='USA'): {len(p_fic):,}")
print(f"With fic='USA' AND costat='A': {len(p_fic[p_fic['costat']=='A']):,}")
