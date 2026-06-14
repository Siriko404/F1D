# Refresh variable_ledger.json to the live 11-table / 5-subsection scope (advisor-approved design).
#  1. Strip stale embedded summary_stats moments (old 2-panel 06-10) -> pointer to the table authority.
#  2. Mark the 3 DROPPED tables (h23/C3, h14c+h18/C7) + their dead-only variables DROPPED (keep history).
#  3. Finalize _meta status.
# Determinism guards: dead-set computed by inverting LIVE tables->variables (not eyeballed), PRINTED,
# and ASSERTED == the expected 12 (halt on any inversion bug). JSON-aware; idempotent; validate at end.
import json, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
LEDGER = ROOT / "docs/Thesis/variable_ledger.json"
STAMP = "2026-06-14"

d = json.loads(LEDGER.read_text(encoding="utf-8"))
tables, ledger_vars = d["tables"], d["variables"]

LIVE_TABLES = {
    "tab:summary_stats", "tab:empire_building_did", "tab:empire_drop_matched",
    "tab:empire_drop_placebo", "tab:empire_cashspec", "tab:h11_prisk_uncertainty",
    "tab:h24_us_epu", "tab:h24b_global_epu", "tab:cash_scrutiny_validity",
    "tab:cash_scrutiny_channel", "tab:reason_gating",
}
DROPPED_TABLES = {"tab:h23_competition_uncertainty", "tab:h14c_ceo2_decomp", "tab:h18_ceo2_decomp"}
EXPECTED_DEAD = {
    "z_log_TotalSimilarity", "BGTLevel_Spread", "BGTLevel_Spread_lead1", "StockPrice",
    "Turnover", "AbsSurpDec", "DailyVola", "CCCL", "SalesGrowth", "RDSales",
    "CashFlowAt", "ClarityCEO",
}
CONCEPT_ALIVE = {"ClarityCEO"}  # dead as a table regressor; alive as the §2.3 DWZ-decomposition concept
AUTHORITY = "docs/Thesis/_tables_from_bible.tex (tab:summary_stats) + docs/Draft/summary_stats.csv"

# --- compute the live/dead variable partition by INVERSION (deterministic) ---
live_vars = set()
for t in LIVE_TABLES:
    live_vars |= set(tables.get(t, {}).get("variables", {}).keys())
dead = sorted(v for v in ledger_vars if v not in live_vars)

print("LIVE table vars (union):", len(live_vars))
print(f"DEAD-only vars ({len(dead)}):", dead)
print("EXPECTED  (12):", sorted(EXPECTED_DEAD))
assert set(dead) == EXPECTED_DEAD, (
    f"DEAD-SET MISMATCH -- inversion bug or scope change. "
    f"extra={set(dead)-EXPECTED_DEAD}  missing={EXPECTED_DEAD-set(dead)}")
print("ASSERT OK: dead-set == expected 12.\n")

# --- 2a. mark dropped tables ---
for t in DROPPED_TABLES:
    if t in tables and not str(tables[t].get("status", "")).startswith("DROPPED"):
        tables[t]["status"] = f"DROPPED {STAMP} (C3 discriminant / C7 presentation cut from thesis; kept for history)"

# --- 2b. mark dead-only variables ---
for v in dead:
    if str(ledger_vars[v].get("status", "")).startswith("DROPPED"):
        continue
    if v in CONCEPT_ALIVE:
        ledger_vars[v]["status"] = (f"DROPPED {STAMP} as a table regressor (h14c/h18 cut); "
            f"ALIVE as the Sec 2.3 DWZ-decomposition concept (ClarityCEO = -CEO FE) -- keep the definition")
    else:
        used = sorted(t for t in DROPPED_TABLES if v in tables.get(t, {}).get("variables", {}))
        ledger_vars[v]["status"] = f"DROPPED {STAMP} (dead-only; used only in dropped tables: {used})"

# --- 1. strip stale summary_stats moments -> pointer (idempotent: only blocks that still carry 'panels') ---
stripped = 0
for v, vd in ledger_vars.items():
    ss = vd.get("summary_stats")
    if isinstance(ss, dict) and "panels" in ss:
        vd["summary_stats"] = {"_authority": AUTHORITY,
            "_note": f"stale 2-panel 06-10 moments removed {STAMP}; the all-universe Table 1 is the live source"}
        stripped += 1

# --- 3. finalize meta ---
m = d["_meta"]
m["status"] = (f"FINALIZED {STAMP} for the 11-table / 5-subsection (Sec 3.1-3.4, 4.1) scope. "
    "3 tables DROPPED (h23/h14c/h18). Embedded summary-stats moments STRIPPED -> authority is "
    "_tables_from_bible.tex. Definitions + construction file:line anchors VERIFIED current (code frozen "
    "since audit pin 7f97a16f; 3/3 spot-checks byte-exact: CashRatio _compustat_engine.py:996, sCFO :356, DWZ eq-4 model).")
m["tables_live"] = sorted(LIVE_TABLES)
m["tables_dropped"] = sorted(DROPPED_TABLES)
m["refresh_log"] = (m.get("refresh_log", []) +
    [f"{STAMP}: stripped {stripped} stale summary_stats blocks -> table-authority pointer; "
     f"marked {len(DROPPED_TABLES)} tables + {len(dead)} dead-only vars DROPPED; finalized scope."])

LEDGER.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
json.loads(LEDGER.read_text(encoding="utf-8"))  # fail-closed validation

print(f"summary_stats blocks stripped: {stripped}")
print(f"dropped tables marked: {sorted(DROPPED_TABLES)}")
print("OK: variable_ledger refreshed; JSON valid.")
