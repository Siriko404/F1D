"""P4b — attrition waterfall by treatment group, step7 merge order."""
import sys, numpy as np, pandas as pd, pyarrow.parquet as pq
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

POST_Q = [20163, 20164]
WINSOR = 0.01
COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")


def _prev_q(yq):
    yr, q = yq // 10, yq % 10
    return (yr - 1) * 10 + 4 if q == 1 else yr * 10 + (q - 1)


def _latest(sub):
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def _calendar_lag1(df, col):
    src = df[["gvkey", "cal_yr_qtr", col]].rename(
        columns={"cal_yr_qtr": "_pq", col: col + "_L"})
    tgt = df[["gvkey", "cal_yr_qtr"]].copy()
    tgt["_pq"] = tgt["cal_yr_qtr"].map(_prev_q).astype("int64")
    return (tgt.merge(src, on=["gvkey", "_pq"], how="left")
            .drop(columns="_pq")
            .rename(columns={col + "_L": col}))


def _cash_dv_t8():
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol",
                       "indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD") & (df["loc"]=="USA") & (df["consol"]=="C")
            & (df["indfmt"]=="INDL") & (df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10
                        + df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(
        columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & df["cheq_l1"].notna() & (df["denom"] > 0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH"]]


def _counts(df):
    """Return (treated, control) firm counts."""
    tg = df.groupby("gvkey")["HIGH_UK_EXPOSURE"].first()
    return int((tg == 1).sum()), int((tg == 0).sum())


# -- load step1 + step3 --
s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                     columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                      columns=["gvkey","group","in_step1"])
trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
tc = trt[trt["in_step1"] & trt["group"].isin(["treated","control"])].copy()
tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)

t0, c0 = int((tc.HIGH_UK_EXPOSURE == 1).sum()), int((tc.HIGH_UK_EXPOSURE == 0).sum())

print("=== P4b -- Attrition Waterfall by Treatment Group ===")
print(f"{'Step':<35s} {'Treated':>8s} {'Control':>8s} {'dT':>6s} {'dC':>6s}")
print(f"{'---'*11} {'------'*1} {'------'*1} {'---'*2} {'---'*2}")
pt, pc = t0, c0
print(f"{'Assigned (step3 tercile)':<35s} {pt:>8d} {pc:>8d}")

# A. S1 × tercile merge
panel = s1.merge(tc[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
nt, nc = _counts(panel)
print(f"{'S1 x tercile merge':<35s} {nt:>8d} {nc:>8d} {nt-pt:>+6d} {nc-pc:>+6d}")
pt, pc = nt, nc

# B. CASH DV (T8)
cash = _cash_dv_t8()
df = panel.merge(cash, on=["gvkey","cal_yr_qtr"], how="inner")
nt, nc = _counts(df)
print(f"{'CASH (T8 net-of-cash)':<35s} {nt:>8d} {nc:>8d} {nt-pt:>+6d} {nc-pc:>+6d}")
pt, pc = nt, nc

df = df[df["atq"] > 0].copy()
df["log_assets"] = np.log(df["atq"])

# C. 5 firm controls (lagged 1Q) -- capture actual column names
BUILDERS = [
    ("BrexitStockReturnBuilder","brexit_stock_return"),
    ("BrexitTobinsQBuilder","brexit_tobins_q"),
    ("BrexitCashFlowBuilder","brexit_cash_flow"),
    ("BrexitSalesGrowthBuilder","brexit_sales_growth"),
]
firm_cols = []
for cls_name, mod_name in BUILDERS:
    m = importlib.import_module(f"f1d.shared.variables.{mod_name}")
    b = getattr(m, cls_name)().build(range(2009, 2017), root_path=ROOT).data.copy()
    if "gvkey" in b.columns:
        b["gvkey"] = b["gvkey"].astype(str).str.zfill(6)
    b["cal_yr_qtr"] = b["cal_yr_qtr"].astype("int64")
    col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
    firm_cols.append(col)
    df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")

nt, nc = _counts(df)
print(f"{'5 firm controls (all lagged)':<35s} {nt:>8d} {nc:>8d} {nt-pt:>+6d} {nc-pc:>+6d}")
pt, pc = nt, nc

df = df.merge(_calendar_lag1(df[["gvkey","cal_yr_qtr","log_assets"]],
                              "log_assets").rename(
    columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
firm_cols.append("log_assets_l1")
nt, nc = _counts(df)
print(f"{'log_assets lagged':<35s} {nt:>8d} {nc:>8d} {nt-pt:>+6d} {nc-pc:>+6d}")
pt, pc = nt, nc

# D. CONSENSUS_EPS (LAGGED -- Fix 2)
m2 = importlib.import_module("f1d.shared.variables.brexit_consensus_eps")
cons = getattr(m2, "BrexitConsensusEPSBuilder")().build(range(2009, 2017), root_path=ROOT).data.copy()
if "gvkey" in cons.columns:
    cons["gvkey"] = cons["gvkey"].astype(str).str.zfill(6)
cons["cal_yr_qtr"] = cons["cal_yr_qtr"].astype("int64")
cons = cons.sort_values(["gvkey","cal_yr_qtr"], kind="stable")
cons = cons.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
ccol = [c for c in cons.columns if c not in ("gvkey","cal_yr_qtr")][0]
con_lagged = _calendar_lag1(cons, ccol).rename(columns={ccol: "cons_fwd"})
df = df.merge(con_lagged, on=["gvkey","cal_yr_qtr"], how="left")
nt, nc = _counts(df)
print(f"{'CONSENSUS_EPS (LAGGED Fix-2)':<35s} {nt:>8d} {nc:>8d} {nt-pt:>+6d} {nc-pc:>+6d}")
pt, pc = nt, nc

# E. Complete-case (estimation)
df["CASH_w"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
    lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                      + "_" + df["cal_yr_qtr"].astype(str))
                     .astype("category").cat.codes)
rcols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
print(f"  (dropna cols: {rcols})")
sub = df.dropna(subset=["CASH_w","indqtr_code"] + rcols).copy()
nt, nc = _counts(sub)
print(f"{'Complete-case (estimation)':<35s} {nt:>8d} {nc:>8d} {nt-pt:>+6d} {nc-pc:>+6d}")
print()

# -- Coverage check --
print("=== CONSENSUS_EPS coverage (assigned firms, LAGGED) ===")
for label, mask in [("treated", tc["HIGH_UK_EXPOSURE"]==1),
                     ("control", tc["HIGH_UK_EXPOSURE"]==0)]:
    gvlist = tc.loc[mask, "gvkey"].unique()
    m = con_lagged[con_lagged["gvkey"].isin(gvlist)]
    firms_with = m["gvkey"].nunique()
    print(f"  {label}: {firms_with}/{len(gvlist)} have >=1 lagged consensus "
          f"({firms_with/len(gvlist):.1%})")

# -- Lagged vs contemporaneous --
print()
print("=== CONSENSUS_EPS: contemporaneous (old) vs lagged (new) ===")

# rebuild from after-controls with contemporaneous consensus
df_old = panel.merge(cash, on=["gvkey","cal_yr_qtr"], how="inner")
df_old = df_old[df_old["atq"] > 0].copy()
df_old["log_assets"] = np.log(df_old["atq"])
old_firm_cols = []
for cls_name, mod_name in BUILDERS:
    m = importlib.import_module(f"f1d.shared.variables.{mod_name}")
    b = getattr(m, cls_name)().build(range(2009, 2017), root_path=ROOT).data.copy()
    if "gvkey" in b.columns:
        b["gvkey"] = b["gvkey"].astype(str).str.zfill(6)
    b["cal_yr_qtr"] = b["cal_yr_qtr"].astype("int64")
    col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
    old_firm_cols.append(col)
    df_old = df_old.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")
df_old = df_old.merge(_calendar_lag1(
    df_old[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(
    columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
old_firm_cols.append("log_assets_l1")

# contemporaneous consensus
df_old = df_old.merge(cons.rename(columns={ccol: "cons_fwd"}),
                      on=["gvkey","cal_yr_qtr"], how="left")
df_old["CASH_w"] = df_old.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
    lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
df_old["POST_x_HIGH"] = (df_old["POST"] * df_old["HIGH_UK_EXPOSURE"]).astype(float)
df_old["indqtr_code"] = ((df_old["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df_old["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)
rcols_old = ["POST_x_HIGH"] + old_firm_cols + ["cons_fwd"]
sub_old = df_old.dropna(subset=["CASH_w","indqtr_code"] + rcols_old).copy()
t_old, c_old = _counts(sub_old)
t_new, c_new = nt, nc  # from lagged waterfall above

print(f"  Contemporaneous (old): T={t_old}, C={c_old}")
print(f"  Lagged (new):          T={t_new}, C={c_new}")
print(f"  d from lagging:        T {t_old - t_new:+d}, C {c_old - c_new:+d}")
print(f"  -> Lagging consensus drops {t_old - t_new} treated, "
      f"{c_old - c_new} control firms from estimation")
