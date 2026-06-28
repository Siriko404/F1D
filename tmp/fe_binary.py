# -*- coding: utf-8 -*-
"""FE version of the 2 binary tests. Rebuilds TEST A/B panels verbatim from
logit_fullcontrols_rerun.py, then fits LPM with Firm + Year-Qtr FE (PanelOLS, same as the
main tables) + diagnoses why a firm-FE LOGIT separates. Run from anywhere (ROOT hardcoded)."""
import sys, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
sys.path.insert(0, str(ROOT / "scripts"))
import os; os.chdir(ROOT)
import gen_empire_did_table as G
from linearmodels.panel import PanelOLS
CTRL = G.CTRL; RHS = ["UncResCEO"] + CTRL

p, s, m = G.base_panel(), G.sdc(), G.manifest()
d = s[s["known"]].copy()
d["dq"] = d["da"].dt.year * 4 + (d["da"].dt.quarter - 1)
d = d.merge(m, on="c6", how="inner")
d["arm"] = np.where(d["pc"] >= 50, "cash", np.where(d["ps"] >= 50, "stock", "other"))

# TEST B: cash vs stock | deal, e=-1
alld = d[d["arm"].isin(["cash", "stock"])][["gvkey", "dq", "arm"]]
b = p.merge(alld, on="gvkey", how="inner")
b = b[b["cq"] == b["dq"] - 1].copy()
b = b[~(b.groupby(["gvkey", "cq"])["arm"].transform("nunique") > 1)].copy()
b["cash"] = (b["arm"] == "cash").astype(float)
bB = b.replace([np.inf, -np.inf], np.nan).dropna(subset=["cash"] + RHS).copy()

# TEST A: predict a deal next quarter (all-deals)
AFT = 3
dqs = d.groupby("gvkey")["dq"].apply(lambda x: sorted(set(x))).to_dict()
def labelA(g, cq):
    ds = dqs.get(g)
    if not ds: return "base"
    if (cq + 1) in ds: return "pre"
    if any(0 <= cq - dd <= AFT for dd in ds): return "drop"
    return "base"
a = p.copy(); a["clsA"] = [labelA(g, cq) for g, cq in zip(a["gvkey"], a["cq"])]
a = a[a["clsA"] != "drop"].copy(); a["deal_next"] = (a["clsA"] == "pre").astype(float)
aA = a.replace([np.inf, -np.inf], np.nan).dropna(subset=["deal_next"] + RHS).copy()

def stars(p): return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))
def fe_lpm(df, dv):
    dd = df.drop_duplicates(["gvkey", "cq"]).set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(RHS) + " + EntityEffects + TimeEffects"
    r = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    k = "UncResCEO"
    return r.params[k], r.std_errors[k], r.pvalues[k], int(r.nobs), dd.index.get_level_values(0).nunique()
def sep(df, dv):
    nun = df.groupby("gvkey")[dv].transform("nunique")
    nt = df["gvkey"].nunique(); nc = df[nun == 1]["gvkey"].nunique(); oc = int((nun == 1).sum())
    return nt, nc, oc, len(df)

print("================ FE BINARY TESTS ================")
print("(pooled baseline: TEST A LPM 0.0086*** | TEST B LPM 0.0613**)\n")
for tag, df, dv in (("TEST A  deal-next-q (all types)", aA, "deal_next"),
                    ("TEST B  cash vs stock | deal",   bB, "cash")):
    nt, nc, oc, N = sep(df, dv)
    print(f"--- {tag} ---")
    print(f"  firm-FE LOGIT separation: {nc}/{nt} firms ({nc/nt:.0%}) have NO within-firm variation in {dv}")
    print(f"    -> they cover {oc}/{N} obs ({oc/N:.0%}); a firm-FE logit drops them = infeasible/uninformative")
    try:
        be, se, pv, no, nf = fe_lpm(df, dv)
        print(f"  LPM + Firm&Year-Qtr FE:  UncResCEO {be:+.5f}  (se {se:.5f}, p {pv:.4f}{stars(pv)})  N={no:,}  firms={nf}\n")
    except Exception as e:
        print(f"  LPM-FE FAILED: {str(e)[:140]}\n")
