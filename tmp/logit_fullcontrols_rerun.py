"""Cash-gate logits — FULL thesis control set, ALL coefs, NO ClarityCEO (bug, removed).
Only CEO-speech var = UncResCEO. Sample/design IDENTICAL to advisor-locked logit_cash_gate.py;
ONLY changes: (1) add the 7 thesis controls to RHS, (2) emit every coef (key + controls) for
BOTH LPM and logit, (3) drop the ClarityCEO leg. RAW regressors (thesis tables are raw).

TEST A: 1[deal next q] ~ UncResCEO + CTRL          (all-deals stacked; aftermath dropped)
TEST B: 1[cash] ~ UncResCEO + CTRL                  (among deals at e=-1; cash=1 vs stock=0)

Run from F1D (data home):  python <path>/logit_fullcontrols_rerun.py
Writes: F1D-phase3/tmp/logit_fullcontrols_results.json
"""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import statsmodels.formula.api as smf
ROOT = Path(".").resolve(); sys.path.insert(0, str(ROOT / "scripts"))
import gen_empire_did_table as G

CTRL = G.CTRL  # ["Leverage","lnAssets","TobinsQ","ROA","Capex","DivDummy","sCFO"]
RHS = ["UncResCEO"] + CTRL
OUT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\tmp\logit_fullcontrols_results.json")


def _coefs(params, bse, pvals, terms):
    return {t: {"beta": float(params[t]), "se": float(bse[t]), "p2": float(pvals[t])}
            for t in terms if t in params.index}


def fit_lpm(df, dv, cl="gvkey"):
    f = f"{dv} ~ " + " + ".join(RHS)
    m = smf.ols(f, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[cl]})
    return {"key": _coefs(m.params, m.bse, m.pvalues, ["UncResCEO"])["UncResCEO"],
            "ctrls": _coefs(m.params, m.bse, m.pvalues, CTRL),
            "n": int(m.nobs), "n_firms": int(df[cl].nunique()), "r2": float(m.rsquared)}


def fit_logit(df, dv, cl="gvkey"):
    f = f"{dv} ~ " + " + ".join(RHS)
    try:
        m = smf.logit(f, data=df).fit(disp=0, cov_type="cluster", cov_kwds={"groups": df[cl]})
        return {"key": _coefs(m.params, m.bse, m.pvalues, ["UncResCEO"])["UncResCEO"],
                "ctrls": _coefs(m.params, m.bse, m.pvalues, CTRL),
                "n": int(m.nobs), "n_firms": int(df[cl].nunique()), "converged": True,
                "pseudo_r2": float(m.prsquared)}
    except Exception as e:
        return {"converged": False, "error": str(e)[:160]}


# ---------- data (verbatim from logit_cash_gate.py; clarity merge REMOVED) ----------
p, s, m = G.base_panel(), G.sdc(), G.manifest()
d = s[s["known"]].copy()
d["dq"] = d["da"].dt.year * 4 + (d["da"].dt.quarter - 1)
d = d.merge(m, on="c6", how="inner")
d["arm"] = np.where(d["pc"] >= 50, "cash", np.where(d["ps"] >= 50, "stock", "other"))

out = {"note": "FULL thesis controls; NO ClarityCEO; RAW regressors; sample = advisor-locked logit_cash_gate design.",
       "controls": CTRL}

# ================= TEST B: cash vs stock | deal, e=-1 =================
alld = d[d["arm"].isin(["cash", "stock"])][["gvkey", "dq", "arm"]]
b = p.merge(alld, on="gvkey", how="inner")
b = b[b["cq"] == b["dq"] - 1].copy()
straddle = b.groupby(["gvkey", "cq"])["arm"].transform("nunique") > 1
b = b[~straddle].copy()
b["cash"] = (b["arm"] == "cash").astype(float)
bB = b.replace([np.inf, -np.inf], np.nan).dropna(subset=["cash"] + RHS).copy()
out["TEST_B"] = {
    "question": "Among deals at e=-1, does CEO Q&A uncertainty predict CASH(1) vs STOCK(0)?",
    "n_cash": int(bB["cash"].sum()), "n_stock": int((bB["cash"] == 0).sum()),
    "cash_base_rate": float(bB["cash"].mean()),
    "lpm": fit_lpm(bB, "cash"), "logit": fit_logit(bB, "cash"),
}

# ================= TEST A: predict a deal next quarter (all-deals) =================
AFT = 3
dqs = d.groupby("gvkey")["dq"].apply(lambda x: sorted(set(x))).to_dict()
def labelA(g, cq):
    ds = dqs.get(g)
    if not ds: return "base"
    if (cq + 1) in ds: return "pre"
    if any(0 <= cq - dd <= AFT for dd in ds): return "drop"
    return "base"
a = p.copy()
a["clsA"] = [labelA(g, cq) for g, cq in zip(a["gvkey"], a["cq"])]
a = a[a["clsA"] != "drop"].copy()
a["deal_next"] = (a["clsA"] == "pre").astype(float)
aA = a.replace([np.inf, -np.inf], np.nan).dropna(subset=["deal_next"] + RHS).copy()
out["TEST_A"] = {
    "question": "Does CEO Q&A uncertainty at e=-1 predict a deal announcement next quarter (any payment type)?",
    "n": int(len(aA)), "n_events": int(aA["deal_next"].sum()), "event_rate": float(aA["deal_next"].mean()),
    "lpm": fit_lpm(aA, "deal_next"), "logit": fit_logit(aA, "deal_next"),
}

OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

# ---------- console ----------
def show(tag, blk):
    print(f"\n===== {tag}: {blk['question']} =====")
    for mdl in ("lpm", "logit"):
        r = blk[mdl]
        if not r.get("converged", True): print(f"  {mdl}: FAILED {r.get('error')}"); continue
        k = r["key"]; st = G.stars(k["p2"])
        print(f"  {mdl:5} UncResCEO beta={k['beta']:+.5f} se={k['se']:.5f} p2={k['p2']:.4f} {st}  N={r['n']:,} firms={r['n_firms']}")
print("TEST_B counts: cash", out["TEST_B"]["n_cash"], "stock", out["TEST_B"]["n_stock"])
print("TEST_A events:", out["TEST_A"]["n_events"], "of", out["TEST_A"]["n"], f"({out['TEST_A']['event_rate']:.2%})")
show("TEST_A (deal next q, all types)", out["TEST_A"])
show("TEST_B (cash vs stock | deal)", out["TEST_B"])
print("\nwrote", OUT)
