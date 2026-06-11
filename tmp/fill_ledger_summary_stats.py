"""Fill variable_ledger.json summary_stats slots from the new Table 1 summary.json.

Round-trips the ledger through json (order-preserving), adds:
  - tables entry for tab:summary_stats
  - per-variable summary_stats (panel A / B moments)
  - _meta bookkeeping
Validates by re-loading before overwrite.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "Thesis" / "variable_ledger.json"
SUMMARY = sorted((ROOT / "outputs" / "econometric" / "summary_stats").glob("*/summary.json"))[-1]

led = json.loads(LEDGER.read_text(encoding="utf-8"))
s = json.loads(SUMMARY.read_text(encoding="utf-8"))
rel = SUMMARY.relative_to(ROOT).as_posix()

# variable -> {panel: moments}
slots: dict[str, dict] = {}
for pid in ("A", "B"):
    for row in s["panels"][pid]["rows"]:
        m = {k: row[k] for k in ("n", "mean", "sd", "p25", "p50", "p75")}
        slots.setdefault(row["var"], {})[pid] = m

filled, missing = [], []
for var, panels in slots.items():
    if var in led["variables"]:
        led["variables"][var]["summary_stats"] = {
            "exhibit": "tab:summary_stats", "source": rel, "panels": panels}
        filled.append(var)
    else:
        missing.append(var)

led["tables"]["tab:summary_stats"] = {
    "title": "Summary Statistics",
    "fragment": "docs/Draft/_summary_stats.tex",
    "generator": "scripts/gen_summary_stats_table.py (computes moments on the exact "
                 "estimation samples of tab:empire_building_did cash arm by importing "
                 "gen_empire_did_table loaders; N-gated against that table's "
                 "summary.json — aborts on mismatch; tex rendered FROM the written "
                 "summary.json)",
    "design": {
        "panel_A": "CashRatio-equation universe (col 1; N=67,590, 2,232 firms): "
                   "CashRatio, CashRatio_lag, PreAnnounceQtr, 7 controls",
        "panel_B": "UncResCEO-equation universe (col 2; N=27,622, 1,248 firms): "
                   "UncResCEO, PreAnnounceQtr, 7 controls; CashScrutiny + "
                   "HighCashScrutiny rows on the matched universe (cols 3-4; "
                   "N=26,216, 1,237 firms)",
        "statistics": "N, mean, SD, p25, median, p75 (4 dp)",
        "registry": "config/exhibit_registry.yaml id=summary_stats (first exhibit)"
    },
    "variables": {v: "descriptive moments" for v in slots},
}

led["_meta"]["tables_done"].append("tab:summary_stats")
led["_meta"]["status_note"] = ("ALL 13 regression tables recorded 2026-06-10; "
                               "tab:summary_stats (Table 1) generated + slots filled 2026-06-10.")

out = json.dumps(led, indent=2, ensure_ascii=False)
json.loads(out)  # validate
LEDGER.write_text(out, encoding="utf-8")
print(f"filled: {sorted(filled)}")
print(f"vars in table 1 but NOT in ledger: {sorted(missing)}")
