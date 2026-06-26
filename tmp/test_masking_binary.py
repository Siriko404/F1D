"""Masking test (BINARY, logit + LPM) — does the STOCK arm suppress uncertain language?

DV = 1[var > full-sample median], for var in {UncResCEO (residual), UncPreCEO (scripted presentation)}.
Design = empire_building_did arms (cash / stock), regress DV on PreAnnounceQtr + 7 controls.
Estimators per cell:
  * LPM_FE     : PanelOLS firm + cal-qtr FE, firm-clustered  (within-firm; the paper's design)  -> G.run
  * LPM_pool   : pooled OLS + controls, firm-clustered (no FE)          (matches the cash-gate tests)
  * logit_pool : pooled logit + controls, firm-clustered (no FE)        (matches the cash-gate tests)

Prediction (masking framing): STOCK PreAnnounceQtr coefficient NEGATIVE + significant
(stock pre-deal calls are below-median = suppressed). Cash for contrast.

Run from F1D:  python <path>/test_masking_binary.py
"""
import glob, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import statsmodels.formula.api as smf
import pyarrow.parquet as pq

ROOT = Path(".").resolve(); sys.path.insert(0, str(ROOT / "scripts"))
import gen_empire_did_table as G
CTRL = G.CTRL


def latest(pat):
    h = sorted(glob.glob(str(ROOT / pat)))
    return h[-1] if h else None


def find_uncpre():
    """UncPreCEO = raw CEO presentation uncertainty; lives in the ceo_clarity_extended variables panel."""
    f = latest("outputs/variables/ceo_clarity_extended/*/ceo_clarity_extended_panel.parquet")
    if f:
        names = pq.ParquetFile(f).schema.names
        if "file_name" in names and "UncPreCEO" in names:
            return f, "UncPreCEO"
    return None, None


def pooled(q, dv, logit):
    need = [dv, "PreAnnounceQtr"] + CTRL
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need + ["gvkey"]).copy()
    f = f"{dv} ~ PreAnnounceQtr + " + " + ".join(CTRL)
    fit = (smf.logit if logit else smf.ols)(f, data=d)
    m = fit.fit(disp=0, cov_type="cluster", cov_kwds={"groups": d["gvkey"]}) if logit \
        else fit.fit(cov_type="cluster", cov_kwds={"groups": d["gvkey"]})
    k = "PreAnnounceQtr"
    return {"beta": float(m.params[k]), "se": float(m.bse[k]), "p2": float(m.pvalues[k]),
            "n": int(m.nobs), "nf": int(d["gvkey"].nunique())}


def st(p): return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))


# ---------- data ----------
p, s, m = G.base_panel(), G.sdc(), G.manifest()
upf, upcol = find_uncpre()
if upf is None:
    raise SystemExit("UncPreCEO column not found in ceo_clarity_extended parquets")
up = (pd.read_parquet(upf, columns=["file_name", upcol])
        .rename(columns={upcol: "UncPreCEO"}).drop_duplicates("file_name"))
p = p.merge(up, on="file_name", how="left")
print(f"UncPreCEO from {Path(upf).relative_to(ROOT)}  col='{upcol}'")

med_res = p["UncResCEO"].median()
med_pre = p["UncPreCEO"].median()
p["hi_res"] = np.where(p["UncResCEO"].notna(), (p["UncResCEO"] > med_res).astype(float), np.nan)
p["hi_pre"] = np.where(p["UncPreCEO"].notna(), (p["UncPreCEO"] > med_pre).astype(float), np.nan)
print(f"medians: UncResCEO={med_res:.4f}  UncPreCEO={med_pre:.4f}")
print(f"coverage: UncResCEO {p['UncResCEO'].notna().mean():.1%}  UncPreCEO {p['UncPreCEO'].notna().mean():.1%}")

arms = {"cash": s["pc"] >= 50, "stock": s["ps"] >= 50}
DVS = [("hi_res", "1[UncRes>med]"), ("hi_pre", "1[UncPre>med]")]

print("\n" + "=" * 96)
print(f"{'arm':5} {'DV':16} {'LPM_FE':>22} {'LPM_pool':>22} {'logit_pool':>22}")
print("-" * 96)
rows = {}
for arm, mask in arms.items():
    q, n = G.build(p, s, m, mask)
    for dvc, lbl in DVS:
        fe = G.run(q, dvc)                      # within-firm LPM (firm+time FE)
        lp = pooled(q, dvc, logit=False)        # pooled LPM
        lg = pooled(q, dvc, logit=True)         # pooled logit
        rows[(arm, dvc)] = (fe, lp, lg)
        def cc(r): return f"{r['beta']:+.4f}{st(r['p2']):<3}({r['se']:.4f})"
        print(f"{arm:5} {lbl:16} {cc(fe):>22} {cc(lp):>22} {cc(lg):>22}")
    print(f"      (arm N pre-deal firms={n}, panel N={int(q['PreAnnounceQtr'].sum())} pre-qtrs)")

print("=" * 96)
print("WIN = STOCK row NEGATIVE + significant (stock pre-deal calls below median = suppressed).")
print("Cash row expected positive (residual run-up).  Stars: * .10  ** .05  *** .01 (two-tailed).")
