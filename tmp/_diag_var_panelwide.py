"""Panel-wide summary stats for each variable vs Table 1 PA anchor."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

panel = pd.read_parquet(latest("variables_panel.parquet"))

ANCHORS = {  # (mean, sd, median, IQR, N) from Table 1 Panel A
    "INVESTMENT": (0.01, 0.02, 0.01, 0.01, 76323),
    "RD": (0.02, 0.05, 0.00, 0.02, 76323),
    "DIVESTITURES (x100)": (0.06, 0.28, 0.00, 0.00, 61151),
    "CASH": (0.22, 0.25, 0.12, 0.27, 78044),
    "NWC": (0.04, 0.19, 0.03, 0.20, 76323),
    "TOBIN_Q": (2.05, 1.96, 1.42, 1.51, 76323),
    "CASH_FLOW": (0.01, 0.06, 0.03, 0.04, 75287),
    "SIZE": (6.32, 1.97, 6.21, 2.78, 78044),
    "SALES_GROWTH": (0.16, 0.62, 0.06, 0.23, 71637),
}

print(f"{'Variable':<22}{'Type':<6}{'mine':>10}{'paper':>10}{'%diff':>10}")
print("-" * 60)
for var in ["INVESTMENT", "RD", "DIVESTITURES", "CASH", "NWC", "TOBIN_Q",
            "CASH_FLOW", "SIZE", "SALES_GROWTH"]:
    if var not in panel.columns:
        print(f"{var}: NOT IN PANEL")
        continue
    s = panel[var].dropna()
    mult = 100 if var == "DIVESTITURES" else 1
    anc_key = "DIVESTITURES (x100)" if var == "DIVESTITURES" else var
    if anc_key not in ANCHORS:
        continue
    am, asd, ame, aiq, an = ANCHORS[anc_key]
    mm = s.mean() * mult
    msd = s.std() * mult
    mme = s.median() * mult
    miq = (s.quantile(.75) - s.quantile(.25)) * mult
    mn = len(s)
    for ttype, mv, av in [("mean", mm, am), ("sd", msd, asd), ("med", mme, ame),
                           ("IQR", miq, aiq), ("N", mn, an)]:
        diff_pct = (mv - av) / max(abs(av), 0.001) * 100 if ttype != "N" else (mv - av) / av * 100
        flag = "✓" if abs(diff_pct) < 30 else "✗"
        print(f"{var:<22}{ttype:<6}{mv:>10.3f}{av:>10.3f}{diff_pct:>9.1f}% {flag}")
    print()
