# -*- coding: utf-8 -*-
"""Emit the FULL FE-LPM coefficient set (key + controls + N + firms + within-R2) for both
binary tests -> fe_results.json. One authoritative source for the table column AND the props."""
import sys, json, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd, os
ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
sys.path.insert(0, str(ROOT / "scripts")); os.chdir(ROOT)
import gen_empire_did_table as G
from linearmodels.panel import PanelOLS
CTRL = G.CTRL; RHS = ["UncResCEO"] + CTRL
OUT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\tmp\fe_results.json")

p, s, m = G.base_panel(), G.sdc(), G.manifest()
d = s[s["known"]].copy()
d["dq"] = d["da"].dt.year * 4 + (d["da"].dt.quarter - 1)
d = d.merge(m, on="c6", how="inner")
d["arm"] = np.where(d["pc"] >= 50, "cash", np.where(d["ps"] >= 50, "stock", "other"))
# TEST B
alld = d[d["arm"].isin(["cash", "stock"])][["gvkey", "dq", "arm"]]
b = p.merge(alld, on="gvkey", how="inner"); b = b[b["cq"] == b["dq"] - 1].copy()
b = b[~(b.groupby(["gvkey", "cq"])["arm"].transform("nunique") > 1)].copy()
b["cash"] = (b["arm"] == "cash").astype(float)
bB = b.replace([np.inf, -np.inf], np.nan).dropna(subset=["cash"] + RHS).copy()
# TEST A
AFT = 3; dqs = d.groupby("gvkey")["dq"].apply(lambda x: sorted(set(x))).to_dict()
def lab(g, cq):
    ds = dqs.get(g)
    if not ds: return "base"
    if (cq + 1) in ds: return "pre"
    if any(0 <= cq - dd <= AFT for dd in ds): return "drop"
    return "base"
a = p.copy(); a["clsA"] = [lab(g, cq) for g, cq in zip(a["gvkey"], a["cq"])]
a = a[a["clsA"] != "drop"].copy(); a["deal_next"] = (a["clsA"] == "pre").astype(float)
aA = a.replace([np.inf, -np.inf], np.nan).dropna(subset=["deal_next"] + RHS).copy()

def fe_full(df, dv):
    dd = df.drop_duplicates(["gvkey", "cq"]).set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(RHS) + " + EntityEffects + TimeEffects"
    r = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    def c(k): return {"beta": float(r.params[k]), "se": float(r.std_errors[k]), "p2": float(r.pvalues[k])}
    return {"key": c("UncResCEO"), "ctrls": {x: c(x) for x in CTRL if x in r.params.index},
            "n": int(r.nobs), "n_firms": int(dd.index.get_level_values(0).nunique()),
            "r2_within": float(r.rsquared_within), "fe": "Firm + Year-Qtr"}

out = {"note": "LPM + Firm & Year-Qtr FE (PanelOLS EntityEffects+TimeEffects), firm-clustered SE. Logit-FE infeasible (perfect separation).",
       "controls": CTRL,
       "TEST_A": fe_full(aA, "deal_next"), "TEST_B": fe_full(bB, "cash")}
OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
def st(p): return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))
for t in ("TEST_A", "TEST_B"):
    k = out[t]["key"]; print(f"{t} FE-LPM UncResCEO {k['beta']:+.5f} (se {k['se']:.5f}, p {k['p2']:.4f}{st(k['p2'])}) N={out[t]['n']:,} firms={out[t]['n_firms']}")
print("wrote", OUT)
