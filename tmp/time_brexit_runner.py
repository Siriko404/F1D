"""Time each stage of the Brexit runner to find the bottleneck."""
from __future__ import annotations
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "src")
from pathlib import Path

from f1d.econometric.run_h1_5_brexit_did import (
    load_h1_panel, merge_uncresceo, load_compustat_raw,
    load_brexit_builders, assemble_panel,
    KEY_IV_BETA_UK, KEY_IV_10K, WINDOW_START_YQ, WINDOW_END_YQ,
    MACRO_CONTROLS, FIRM_CONTROLS_LAG1, EPS_CONTROL_LAG1, _fit_one,
)

root = Path.cwd()

def tic(label): return (label, time.time())
def toc(t): label, t0 = t; print(f"  [{time.time()-t0:>6.2f}s] {label}")

t = tic("1. load_h1_panel"); panel, _ = load_h1_panel(root); toc(t)
t = tic("2. merge_uncresceo"); panel = merge_uncresceo(panel, root); toc(t)
t = tic("3. window filter + gvkey set");
panel_brx = panel[(panel["cal_yr_qtr"] >= WINDOW_START_YQ - 1) & (panel["cal_yr_qtr"] <= WINDOW_END_YQ)]
gvkeys_keep = set(panel_brx["gvkey"].unique()); toc(t)
t = tic("4. load_compustat_raw (467 MB parquet)"); raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ); toc(t)
t = tic("5. load_brexit_builders (10 parquets)"); builders = load_brexit_builders(root); toc(t)
t = tic("6. assemble_panel"); cell_panel = assemble_panel(panel, raw_comp, builders); toc(t)

exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
print(f"\n  Panel shape: {cell_panel.shape}; fic100_qtr_id nunique = {cell_panel['fic100_qtr_id'].nunique()}")
print()

for dv in ["cash_brexit_dv", "UncResCEO_c"]:
    for treatment in [KEY_IV_BETA_UK, KEY_IV_10K]:
        t = tic(f"7. fit campello_exact {dv} x {treatment}")
        _ = _fit_one(cell_panel, dv, treatment, exog_cols, "campello_exact"); toc(t)
