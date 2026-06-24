"""Cash-gate logits (supervisor Ask 3), advisor-locked spec. SUPPLEMENTARY (underpowered: stock~129).
Reuses gen_empire_did_table (base_panel/sdc/manifest/arms). Regressor sampled at e=-1.

Test B (existential, but power-limited): among DEAL firm-quarters at e=-1, does CEO uncertainty
  predict CASH(1) vs STOCK(0)?   1[cash] ~ z(UncResCEO)  [+ z(lnAssets)+z(Leverage)]
  + PERSISTENT-CHANNEL fallback:  1[cash] ~ z(ClarityCEO)   (ClarityCEO = -CEO_FE, the chronic style)
Test A: does CEO uncertainty at e=-1 predict a deal announcement next quarter?
  1[deal next q] ~ z(UncResCEO),  risk set = base panel, post-first-deal quarters dropped.

Lean controls (UncResCEO already nets out CEO-FE, year-FE, returns, linguistic factors -> no year FE,
no era buckets). Primary = LPM (clean AME + 95% CI, cluster-robust by firm); logit secondary (AME).
SESOI pre-committed: 'weak' = 95% CI on AME(per 1-SD) excludes a >=5pp shift in P(cash).
Output: tmp/logit_cash_gate_results.json + printed table.
"""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import statsmodels.formula.api as smf
ROOT = Path(".").resolve(); sys.path.insert(0, str(ROOT / "scripts"))
import gen_empire_did_table as G

SESOI = 0.05  # 5pp shift in P(cash) per 1-SD UncResCEO

def z(s):  # standardize on estimation sample
    s = pd.to_numeric(s, errors="coerce"); return (s - s.mean()) / s.std()

def clarity_ceo() -> pd.DataFrame:
    """file_name -> ClarityCEO (= -CEO fixed effect, DWZ Eq.5: the persistent guardedness)."""
    res_path = Path(G._latest("outputs/econometric/ceo_clarity_extended/*/ceo_clarity_residual.parquet"))
    fe = pd.read_parquet(res_path.parent / "ceo_clarity_fe.parquet", columns=["ceo_id", "ClarityCEO"])
    rk = pd.read_parquet(res_path, columns=["file_name", "ceo_id"])
    return rk.merge(fe, on="ceo_id", how="left")[["file_name", "ClarityCEO"]]

def lpm(df, dv, rhs, cl="gvkey"):
    f = f"{dv} ~ " + " + ".join(rhs)
    m = smf.ols(f, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[cl]})
    key = rhs[0]
    b, se = float(m.params[key]), float(m.bse[key])
    return {"spec": f, "ame": b, "se": se, "ci": [b - 1.96*se, b + 1.96*se],
            "p": float(m.pvalues[key]), "n": int(m.nobs), "n_firms": int(df[cl].nunique())}

def logit_ame(df, dv, rhs, cl="gvkey"):
    f = f"{dv} ~ " + " + ".join(rhs)
    try:
        m = smf.logit(f, data=df).fit(disp=0, cov_type="cluster", cov_kwds={"groups": df[cl]})
        mg = m.get_margeff(at="overall")
        i = list(m.params.index).index(rhs[0]) - 1  # margeff drops intercept
        return {"ame": float(mg.margeff[i]), "se": float(mg.margeff_se[i]),
                "ci": [float(mg.conf_int()[i][0]), float(mg.conf_int()[i][1])], "converged": True}
    except Exception as e:
        return {"converged": False, "error": str(e)[:120]}

def verdict(ci):
    lo, hi = ci
    if lo > 0 or hi < 0:        return "SIGNIFICANT (excludes 0)"
    if abs(lo) < SESOI and abs(hi) < SESOI: return "PRECISE NULL (rules out >=5pp -> could drop)"
    return "UNDERPOWERED null (CI admits >=5pp -> cannot drop)"

def supports(ame, ci, expect):
    # expect = +1 (UncResCEO: more uncertainty -> cash) | -1 (ClarityCEO: LOW clarity=guarded -> cash)
    if not (ci[0] > 0 or ci[1] < 0): return "n.s."
    return "SUPPORTS cash" if ((ame > 0) == (expect > 0)) else "CONTRADICTS cash"

# ---------- data ----------
p, s, m = G.base_panel(), G.sdc(), G.manifest()
p = p.merge(clarity_ceo(), on="file_name", how="left")
d = s[s["known"]].copy()
d["dq"] = d["da"].dt.year * 4 + (d["da"].dt.quarter - 1)
d = d.merge(m, on="c6", how="inner")
d["arm"] = np.where(d["pc"] >= 50, "cash", np.where(d["ps"] >= 50, "stock", "other"))

out = {"SESOI_pp": SESOI*100, "note": "SUPPLEMENTARY (stock arm underpowered); confirmatory only, cannot drop on a null."}

# ================= TEST B: all-deals, e=-1, cash vs stock =================
alld = d[d["arm"].isin(["cash", "stock"])][["gvkey", "dq", "arm"]]
b = p.merge(alld, on="gvkey", how="inner")
b = b[b["cq"] == b["dq"] - 1].copy()
# drop straddle firm-quarters that map to BOTH arms (same quarter cash+stock deal)
straddle = b.groupby(["gvkey", "cq"])["arm"].transform("nunique") > 1
b = b[~straddle].copy()
b["cash"] = (b["arm"] == "cash").astype(float)
b["zUnc"], b["zSize"], b["zLev"], b["zClar"] = z(b["UncResCEO"]), z(b["lnAssets"]), z(b["Leverage"]), z(b["ClarityCEO"])

bB = b.dropna(subset=["cash", "zUnc"]).copy()
res_b = {
    "n_cash": int(bB["cash"].sum()), "n_stock": int((bB["cash"] == 0).sum()),
    "cash_base_rate": float(bB["cash"].mean()),
    "transient_uncres": {
        "lpm": lpm(bB, "cash", ["zUnc"]),
        "lpm_controlled": lpm(bB.dropna(subset=["zSize", "zLev"]), "cash", ["zUnc", "zSize", "zLev"]),
        "logit_ame": logit_ame(bB, "cash", ["zUnc"]),
    },
    "persistent_clarityceo": {"lpm": lpm(bB.dropna(subset=["zClar"]), "cash", ["zClar"])},
}
tb = res_b["transient_uncres"]["lpm"]; pc = res_b["persistent_clarityceo"]["lpm"]
res_b["transient_uncres"]["verdict"] = verdict(tb["ci"]); res_b["transient_uncres"]["support"] = supports(tb["ame"], tb["ci"], +1)
res_b["persistent_clarityceo"]["verdict"] = verdict(pc["ci"]); res_b["persistent_clarityceo"]["support"] = supports(pc["ame"], pc["ci"], -1)
out["TEST_B"] = res_b

# ================= TEST A: predict a deal next quarter (ALL DEALS — locked rule, not first-deal) =================
AFT = 3   # aftermath window: deal quarter + 3 post-quarters are contaminated -> dropped
dqs = d.groupby("gvkey")["dq"].apply(lambda x: sorted(set(x))).to_dict()
def labelA(g, cq):
    ds = dqs.get(g)
    if not ds: return "base"                                # never-acquirer quarter -> clean DV=0
    if (cq + 1) in ds: return "pre"                         # e=-1 for SOME deal -> DV=1
    if any(0 <= cq - dd <= AFT for dd in ds): return "drop" # deal quarter or aftermath -> contaminated
    return "base"
a = p.copy()
a["clsA"] = [labelA(g, cq) for g, cq in zip(a["gvkey"], a["cq"])]
a = a[a["clsA"] != "drop"].copy()
a["deal_next"] = (a["clsA"] == "pre").astype(float)
a["zUnc"] = z(a["UncResCEO"])
aA = a.dropna(subset=["deal_next", "zUnc"]).copy()
res_a = {"design": "all-deals stacked (locked rule); risk set = all clean firm-quarters, deal+aftermath dropped",
         "n": int(len(aA)), "n_events": int(aA["deal_next"].sum()), "event_rate": float(aA["deal_next"].mean()),
         "lpm": lpm(aA, "deal_next", ["zUnc"]), "logit_ame": logit_ame(aA, "deal_next", ["zUnc"])}
res_a["verdict"] = verdict(res_a["lpm"]["ci"]); res_a["support"] = supports(res_a["lpm"]["ame"], res_a["lpm"]["ci"], +1)
out["TEST_A"] = res_a

Path("tmp/logit_cash_gate_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

# ---------- print ----------
def row(name, r): print(f"  {name:<22} AME={r['ame']*100:+6.2f}pp  CI=[{r['ci'][0]*100:+6.2f},{r['ci'][1]*100:+6.2f}]  p={r['p']:.3f}  N={r['n']} firms={r['n_firms']}")
print("\n================= TEST B (cash vs stock | deal, e=-1) =================")
print(f"  cash={res_b['n_cash']}  stock={res_b['n_stock']}  base_rate={res_b['cash_base_rate']:.1%}  (SESOI={SESOI*100:.0f}pp)")
row("UncResCEO LPM", res_b["transient_uncres"]["lpm"])
row("UncResCEO LPM+ctrl", res_b["transient_uncres"]["lpm_controlled"])
la = res_b["transient_uncres"]["logit_ame"]
print(f"  UncResCEO logit-AME    {('%.2fpp CI[%.2f,%.2f]'%(la['ame']*100,la['ci'][0]*100,la['ci'][1]*100)) if la.get('converged') else 'did not converge: '+la.get('error','')}")
row("ClarityCEO LPM (persist)", res_b["persistent_clarityceo"]["lpm"])
print(f"  -> transient (UncResCEO) : {res_b['transient_uncres']['verdict']}  | {res_b['transient_uncres']['support']}")
print(f"  -> persistent (ClarityCEO, expect NEG): {res_b['persistent_clarityceo']['verdict']}  | {res_b['persistent_clarityceo']['support']}")
print("\n================= TEST A (predict deal next quarter) =================")
print(f"  N={res_a['n']:,}  events(e=-1)={res_a['n_events']}  rate={res_a['event_rate']:.2%}")
row("UncResCEO LPM", res_a["lpm"])
print(f"  -> verdict: {res_a['verdict']}  | {res_a['support']}")
print("\nwrote tmp/logit_cash_gate_results.json")
