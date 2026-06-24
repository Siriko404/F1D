"""GATING count for the cash-gate logit (Test B). Before any regression:
how many first-deal cash vs stock firms survive every filter to a usable e=-1 row?
If the stock arm is tiny (~<90), the 'precise null -> drop cash' branch is unreachable."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(".").resolve(); sys.path.insert(0, str(ROOT / "scripts"))
import gen_empire_did_table as G

p, s, m = G.base_panel(), G.sdc(), G.manifest()

# --- first deal OVERALL per firm, classified by payment arm ---
d = s[s["known"]].copy()
d["dq"] = d["da"].dt.year * 4 + (d["da"].dt.quarter - 1)
d = d.merge(m, on="c6", how="inner")                       # CUSIP -> gvkey
d["arm"] = np.where(d["pc"] >= 50, "cash", np.where(d["ps"] >= 50, "stock", "other"))
first = (d.sort_values("dq").groupby("gvkey", as_index=False).first()[["gvkey", "dq", "arm"]])

def vc(df, where=""):
    g = df.drop_duplicates("gvkey")["arm"].value_counts().to_dict()
    print(f"  {where:<34} cash={g.get('cash',0):>5}  stock={g.get('stock',0):>5}  other={g.get('other',0):>5}")

print("ATTRITION (unique first-deal firms):")
vc(first, "all first-deal firms")

# --- e=-1 panel row (the quarter before the first deal) ---
pre = p.merge(first, on="gvkey", how="inner")
pre = pre[pre["cq"] == pre["dq"] - 1].copy()
vc(pre, "have an e=-1 panel row")

# --- successive non-missing filters (residual inherits Main + >=5 calls) ---
for v in ["UncResCEO", "lnAssets", "Leverage"]:
    pre = pre[pre[v].notna()].copy()
    vc(pre, f"after non-missing {v}")

fin = pre[pre["arm"].isin(["cash", "stock"])].drop_duplicates("gvkey")
nc = int((fin["arm"] == "cash").sum()); ns = int((fin["arm"] == "stock").sum())
print(f"\nFINAL Test B 2x2 (first-deal, clean e=-1, all vars present):")
print(f"  CASH = {nc}    STOCK = {ns}    total = {nc+ns}")
print(f"  cash base rate = {nc/max(1,nc+ns):.1%}")
# crude power read: SE of a proportion ~ sqrt(pq/n); detectable shift scale
import math
se_stock = math.sqrt(0.25/max(1,ns))
print(f"  ~half-CI on stock-arm proportion ~ {se_stock*1.96*100:.1f}pp -> "
      f"{'5pp detectable' if se_stock*1.96 < 0.05 else 'CANNOT resolve 5pp (underpowered)'}")

# --- does ALL-DEALS (stacked) rescue the stock N? (rows; clustering needed) ---
dd = d[["gvkey", "dq", "arm"]].copy()
ad = p.merge(dd, on="gvkey", how="inner")
ad = ad[ad["cq"] == ad["dq"] - 1].copy()
for v in ["UncResCEO", "lnAssets", "Leverage"]:
    ad = ad[ad[v].notna()].copy()
ad = ad[ad["arm"].isin(["cash", "stock"])]
rows = ad["arm"].value_counts().to_dict()
firms = ad.drop_duplicates(["gvkey", "arm"])["arm"].value_counts().to_dict()
print(f"\nALL-DEALS (stacked) e=-1 rows:  cash={rows.get('cash',0)}  stock={rows.get('stock',0)}")
print(f"ALL-DEALS unique firm-arms:     cash={firms.get('cash',0)}  stock={firms.get('stock',0)}")
