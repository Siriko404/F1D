"""C6 robustness: re-estimate the formal cash-specificity test with TWO-WAY clustering
(firm x calendar-quarter) and compare to the locked firm-clustered table.

Read-only. Does NOT touch the frozen production script or any output table. Reuses the
production module's loaders + build_pooled so inputs are byte-identical; only the .fit()
clustering changes. Point estimates are identical across clusterings (clustering changes
ONLY the covariance -> SE -> p), so the question is purely whether the EFFECT diff
(locked 0.0983**, p=.039 firm-clustered) stays significant at 5% under two-way SEs.
"""
import importlib.util
from pathlib import Path
import numpy as np
from linearmodels.panel import PanelOLS
from scipy.stats import norm

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
spec = importlib.util.spec_from_file_location("_cs", ROOT / "src" / "f1d" / "econometric" / "empire_cashspec_interaction.py")
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)          # executes module top-level (NOT main); gives cs.emp, cs.CTRL, cs.build_pooled
emp, CTRL = cs.emp, cs.CTRL


def run_eff(q, dv, restrict_uncres, add_cash_lag, two_way):
    extra = ["CashRatio_lag"] if add_cash_lag else []
    need = [dv, "PreAnn_cash", "PreAnn_stock"] + CTRL + extra
    if restrict_uncres and "UncResCEO" not in need:
        need = ["UncResCEO"] + need
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy().set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + PreAnn_cash + PreAnn_stock + " + " + ".join(CTRL + extra) + " + EntityEffects + TimeEffects"
    kw = dict(cov_type="clustered", cluster_entity=True)
    if two_way:
        kw["cluster_time"] = True
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(**kw)
    par, V = mod.params, mod.cov
    i, j = "PreAnn_cash", "PreAnn_stock"
    diff = float(par[i] - par[j])
    var = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j])
    se = var ** 0.5
    t = diff / se
    p2 = 2 * norm.sf(abs(t))
    return dict(diff=diff, se=se, t=t, p2=p2, cash=float(par[i]), cash_se=float(mod.std_errors[i]),
                stock=float(par[j]), stock_se=float(mod.std_errors[j]), n=int(mod.nobs))


def stars(p):
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else "n.s."))


# replicate production main()'s panel prep exactly
p, s, m = emp.base_panel(), emp.sdc(), emp.manifest()
p = p.sort_values(["gvkey", "cq"]).copy()
p["CashRatio_lag"] = p.groupby("gvkey")["CashRatio"].shift(1)
prev_cq = p.groupby("gvkey")["cq"].shift(1)
p.loc[prev_cq != p["cq"] - 1, "CashRatio_lag"] = np.nan
q, n_cash, n_stock = cs.build_pooled(p, s, m)
print(f"pooled: PreAnn_cash={n_cash:,}  PreAnn_stock={n_stock:,}\n")

cols = [("UncResCEO  (EFFECT, matched)", "UncResCEO", True, False),
        ("CashRatio  (CAUSE, matched)", "CashRatio", True, True),
        ("CashRatio  (CAUSE, full)", "CashRatio", False, True)]

print(f"{'column':32} {'cluster':9} {'diff':>9} {'se':>8} {'t':>6} {'p2':>7} sig")
print("-" * 80)
for label, dv, ru, lag in cols:
    base = run_eff(q, dv, ru, lag, two_way=False)
    twoway = run_eff(q, dv, ru, lag, two_way=True)
    assert abs(base["diff"] - twoway["diff"]) < 1e-9, "point estimate must be identical across clusterings"
    print(f"{label:32} {'firm':9} {base['diff']:>9.4f} {base['se']:>8.4f} {base['t']:>6.2f} {base['p2']:>7.3f} {stars(base['p2'])}")
    print(f"{'':32} {'firm+qtr':9} {twoway['diff']:>9.4f} {twoway['se']:>8.4f} {twoway['t']:>6.2f} {twoway['p2']:>7.3f} {stars(twoway['p2'])}")
    print()

# headline verdict on the EFFECT diff
base = run_eff(q, "UncResCEO", True, False, two_way=False)
tw = run_eff(q, "UncResCEO", True, False, two_way=True)
print("=" * 80)
print(f"C6 EFFECT diff (locked = 0.0983**, p=.039 firm-clustered):")
print(f"  firm-clustered  : {base['diff']:.4f}  se {base['se']:.4f}  p2 {base['p2']:.4f}  {stars(base['p2'])}")
print(f"  two-way (f x q) : {tw['diff']:.4f}  se {tw['se']:.4f}  p2 {tw['p2']:.4f}  {stars(tw['p2'])}")
verdict = "STRENGTHENS (or holds) -> two-way keeps C6 sig at 5%" if tw["p2"] < 0.05 else "DAMAGES -> two-way pushes C6 above 5%; IGNORE per user, keep firm-clustered"
print(f"  VERDICT: {verdict}")
