"""P4c — characterize attrition: coverage, beta-split, group-means vs Table 1 B/C."""
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
            .drop(columns="_pq").rename(columns={col + "_L": col}))


def _cash_dv_t8():
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD") & (df["loc"]=="USA") & (df["consol"]=="C")
            & (df["indfmt"]=="INDL") & (df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10 + df["datadate"].dt.quarter).astype("int64")
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


# -- load step1 + step3 --
s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                     columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                      columns=["gvkey","group","in_step1","beta_uk"])
trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
tc = trt[trt["in_step1"] & trt["group"].isin(["treated","control"])].copy()
tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)

# -- build panel through all merges (same as step7) --
BUILDERS = [
    ("BrexitStockReturnBuilder","brexit_stock_return"),
    ("BrexitTobinsQBuilder","brexit_tobins_q"),
    ("BrexitCashFlowBuilder","brexit_cash_flow"),
    ("BrexitSalesGrowthBuilder","brexit_sales_growth"),
]

panel = s1.merge(tc[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
cash = _cash_dv_t8()
df = panel.merge(cash, on=["gvkey","cal_yr_qtr"], how="inner")
df = df[df["atq"] > 0].copy()
df["log_assets"] = np.log(df["atq"])

firm_cols = []
for cls_name, mod_name in BUILDERS:
    m = importlib.import_module(f"f1d.shared.variables.{mod_name}")
    b = getattr(m, cls_name)().build(range(2009, 2017), root_path=ROOT).data.copy()
    if "gvkey" in b.columns: b["gvkey"] = b["gvkey"].astype(str).str.zfill(6)
    b["cal_yr_qtr"] = b["cal_yr_qtr"].astype("int64")
    col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
    firm_cols.append(col)
    df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")

df = df.merge(_calendar_lag1(df[["gvkey","cal_yr_qtr","log_assets"]], "log_assets")
              .rename(columns={"log_assets":"log_assets_l1"}),
              on=["gvkey","cal_yr_qtr"], how="left")
firm_cols.append("log_assets_l1")

# consensus (lagged, Fix-2)
cons_mod = importlib.import_module("f1d.shared.variables.brexit_consensus_eps")
cons = getattr(cons_mod, "BrexitConsensusEPSBuilder")().build(range(2009, 2017), root_path=ROOT).data.copy()
if "gvkey" in cons.columns: cons["gvkey"] = cons["gvkey"].astype(str).str.zfill(6)
cons["cal_yr_qtr"] = cons["cal_yr_qtr"].astype("int64")
cons = cons.sort_values(["gvkey","cal_yr_qtr"], kind="stable")
cons = cons.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
ccol = [c for c in cons.columns if c not in ("gvkey","cal_yr_qtr")][0]
cons_col_name = ccol  # actual builder column name
con_lagged = _calendar_lag1(cons, ccol).rename(columns={ccol: "cons_fwd"})
df = df.merge(con_lagged, on=["gvkey","cal_yr_qtr"], how="left")

# winsorization
df["CASH_w"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
    lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                      + "_" + df["cal_yr_qtr"].astype(str))
                     .astype("category").cat.codes)

rcols = ["CASH_w", "indqtr_code", "POST_x_HIGH"] + firm_cols + ["cons_fwd"]

# -- dataframe BEFORE dropna (for Check 1 & 2 coverage analysis) --
df["_complete"] = df[rcols].notna().all(axis=1)

# -- estimation sample --
sub = df.dropna(subset=rcols).copy()

# attach beta_uk for Check 2
beta_map = trt[["gvkey","beta_uk"]].drop_duplicates("gvkey")
sub = sub.merge(beta_map, on="gvkey", how="left")
df = df.merge(beta_map, on="gvkey", how="left")

print("=== CHECK 1: Median complete-case quarters per firm ===")
for label, mask in [("Treated", sub["HIGH_UK_EXPOSURE"]==1),
                     ("Control", sub["HIGH_UK_EXPOSURE"]==0)]:
    g = sub[mask]
    cq = g.groupby("gvkey").size()
    print(f"  {label}: median={cq.median():.0f}, mean={cq.mean():.1f}, "
          f"min={cq.min()}, max={cq.max()}, firms={len(cq)}")

# also for comparison: coverage stats from pre-dropna frame
print()
print("  Coverage (pre-dropna, all 956 assigned firms):")
for label, mask in [("Treated", df["HIGH_UK_EXPOSURE"]==1),
                     ("Control", df["HIGH_UK_EXPOSURE"]==0)]:
    g = df[mask]
    cq_complete = g.groupby("gvkey")["_complete"].sum()
    cq_total = g.groupby("gvkey").size()
    pct = cq_complete.sum() / cq_total.sum() if cq_total.sum() > 0 else 0
    print(f"  {label}: median complete qtrs={cq_complete.median():.0f}, "
          f"fraction complete={pct:.1%}")

print()
print("=== CHECK 2: betaUK-split within treated firms ===")
treated = sub[sub["HIGH_UK_EXPOSURE"]==1].copy()
med_beta = treated.groupby("gvkey")["beta_uk"].first().median()
top = treated[treated["beta_uk"] >= med_beta]
bot = treated[treated["beta_uk"] < med_beta]
tq_top = top.groupby("gvkey").size()
tq_bot = bot.groupby("gvkey").size()
print(f"  betaUK median (treated): {med_beta:.4f}")
print(f"  Top-half:  median complete qtrs={tq_top.median():.0f}, "
      f"firms={len(tq_top)}, betaUK range=[{top['beta_uk'].min():.4f}, {top['beta_uk'].max():.4f}]")
print(f"  Bottom-half: median complete qtrs={tq_bot.median():.0f}, "
      f"firms={len(tq_bot)}, betaUK range=[{bot['beta_uk'].min():.4f}, {bot['beta_uk'].max():.4f}]")

print()
print("=== CHECK 3: Unmatched group-means vs Table 1 Panels B/C ===")
# Pre-period = quarters BEFORE 2016Q3 (pre-Brexit)
pre = sub[sub["cal_yr_qtr"] < 20163].copy()

# Map actual builder column names to paper labels
col_map = {
    "CASH": "CASH",
    "log_assets": "SIZE",
}
# firm_cols has the actual builder output names
# We need the variable value columns (not the lagged name)
# The columns in firm_cols are: brexit_stock_return, brexit_tobins_q,
# brexit_cash_flow, brexit_sales_growth, log_assets_l1
# For group means we want the pre-winsorized, non-lagged values where possible
# But in the estimation frame, we only have the lagged versions.
# For Table 1 comparison, paper reports firm characteristics, not lagged controls.
# So we should compute from the raw data, not the lagged estimation frame.
# Let me construct the pre-period means using the raw (unlagged) builder outputs.

# Rebuild the raw variable values (not lagged) for pre-period
# Use the same builders but merge raw values
pre_vars = panel[["gvkey","cal_yr_qtr","atq","HIGH_UK_EXPOSURE","POST"]].copy()
pre_vars = pre_vars.merge(cash, on=["gvkey","cal_yr_qtr"], how="inner")
pre_vars = pre_vars[pre_vars["atq"].notna()].copy()
pre_vars["SIZE"] = np.log(pre_vars["atq"])

# Also compute T1 CASH (cheq/atq_{t-1}) for Table 1 comparison
# cash df has: gvkey, cal_yr_qtr, CASH(=T8)
# Build T1 CASH: cheq_t / atq_{t-1}
df_t1 = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol","indfmt","datafmt","atq","cheq"]).to_pandas()
df_t1["datadate"] = pd.to_datetime(df_t1["datadate"], errors="coerce")
df_t1 = df_t1[(df_t1["datadate"] >= BUFFER_LO) & (df_t1["datadate"] <= WIN_HI_DATE)]
df_t1 = df_t1[(df_t1["curcdq"]=="USD") & (df_t1["loc"]=="USA") & (df_t1["consol"]=="C")
              & (df_t1["indfmt"]=="INDL") & (df_t1["datafmt"]=="STD")].copy()
for c in ("atq","cheq"): df_t1[c] = pd.to_numeric(df_t1[c], errors="coerce")
df_t1["gvkey"] = df_t1["gvkey"].astype("int64").astype(str).str.zfill(6)
df_t1["cal_yr_qtr"] = (df_t1["datadate"].dt.year * 10 + df_t1["datadate"].dt.quarter).astype("int64")
df_t1 = df_t1.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
df_t1 = df_t1.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
src_t1 = df_t1[["gvkey","cal_yr_qtr","atq"]].rename(columns={"cal_yr_qtr":"_pq","atq":"atq_l1"})
df_t1["_pq"] = df_t1["cal_yr_qtr"].map(_prev_q).astype("int64")
df_t1 = df_t1.merge(src_t1, on=["gvkey","_pq"], how="left").drop(columns="_pq")
df_t1 = df_t1[df_t1["cheq"].notna() & (df_t1["atq_l1"] > 0)].copy()
df_t1["CASH_T1"] = df_t1["cheq"] / df_t1["atq_l1"]
pre_vars = pre_vars.merge(df_t1[["gvkey","cal_yr_qtr","CASH_T1"]], on=["gvkey","cal_yr_qtr"], how="left")

# Merge raw (unlagged) firm controls
raw_cols = []
for cls_name, mod_name in BUILDERS:
    m = importlib.import_module(f"f1d.shared.variables.{mod_name}")
    b = getattr(m, cls_name)().build(range(2009, 2017), root_path=ROOT).data.copy()
    if "gvkey" in b.columns: b["gvkey"] = b["gvkey"].astype(str).str.zfill(6)
    b["cal_yr_qtr"] = b["cal_yr_qtr"].astype("int64")
    col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
    raw_cols.append((col, col))  # (merge_col, label)
    pre_vars = pre_vars.merge(b[["gvkey","cal_yr_qtr",col]], on=["gvkey","cal_yr_qtr"], how="left")

# Merge raw consensus (unlagged)
pre_vars = pre_vars.merge(cons[["gvkey","cal_yr_qtr",cons_col_name]],
                          on=["gvkey","cal_yr_qtr"], how="left")

# Variable display mapping
var_labels = {
    "CASH_T1": "CASH (T1)",
    "SIZE": "SIZE",
    "brexit_tobins_q": "TOBIN_Q",
    "brexit_sales_growth": "SALES_GROWTH",
    "brexit_cash_flow": "CASH_FLOW",
    "brexit_stock_return": "STOCK_RETURNS",
    cons_col_name: "CONSENSUS_EPS",
}

print(f"\n{'Variable':<20s} {'Our T':>8s} {'Paper T':>8s} {'Our C':>8s} {'Paper C':>8s}")
print(f"{'':->20s} {'':->8s} {'':->8s} {'':->8s} {'':->8s}")

paper_t = {"CASH": 0.20, "SIZE": 6.11, "TOBIN_Q": 1.92, "SALES_GROWTH": 0.18,
           "CASH_FLOW": 0.01, "STOCK_RETURNS": 0.02, "CONSENSUS_EPS": 0.01}
paper_c = {"CASH": 0.17, "TOBIN_Q": 1.98}

for src_col, label in var_labels.items():
    if src_col not in pre_vars.columns:
        continue
    pt = pre_vars[(pre_vars["HIGH_UK_EXPOSURE"]==1) & (pre_vars[src_col].notna())][src_col].mean()
    pc = pre_vars[(pre_vars["HIGH_UK_EXPOSURE"]==0) & (pre_vars[src_col].notna())][src_col].mean()
    pt_s = f"{pt:.2f}" if not np.isnan(pt) else "n/a"
    pc_s = f"{pc:.2f}" if not np.isnan(pc) else "n/a"
    pt_p = f"{paper_t[label]:.2f}" if label in paper_t else "---"
    pc_p = f"{paper_c[label]:.2f}" if label in paper_c else "---"
    print(f"{label:<20s} {pt_s:>8s} {pt_p:>8s} {pc_s:>8s} {pc_p:>8s}")

# Also report N for context
nt = pre_vars[pre_vars["HIGH_UK_EXPOSURE"]==1].groupby("gvkey").size().agg(["count","sum"])
nc = pre_vars[pre_vars["HIGH_UK_EXPOSURE"]==0].groupby("gvkey").size().agg(["count","sum"])
print(f"\n  Pre-period treated: {int(nt['count'])} firms, {int(nt['sum'])} fq")
print(f"  Pre-period control: {int(nc['count'])} firms, {int(nc['sum'])} fq")
print(f"  Paper Panel B treated N ~ 11,176 fq; Panel C control N ~ 10,xxx fq")
