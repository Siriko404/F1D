"""Extract Campello et al. (2022 JFQA) Supplementary Table C.2
(Summary Statistics: Matched Sample) → clean JSON.

Programmatic parse of docs/papers/campello_supplementary_text.txt (NO hand-typed
cell values, per feedback_no_llm_cell_transcription). Captures treated + control
means for the 7 variables that overlap our PSM matched sample (the 6 propensity
covariates + CASH), for Panel A (market β^UK) and Panel B (textual).

Output: outputs/campello_rebuild/campello_c2/campello_c2_matched.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "papers" / "campello_supplementary_text.txt"
OUT = ROOT / "outputs" / "campello_rebuild" / "campello_c2"

# C.2 label (verbatim, in file) -> our covariate key
LABELS = {
    "STOCK_RETURNS": "brexit_stock_return",
    "TOBIN_Q": "brexit_tobins_q",
    "CASH_FLOW": "brexit_cash_flow",
    "SALES_GROWTH": "brexit_sales_growth",
    "SIZE (Log Assets)": "log_assets_l1",
    "CONSENSUS_EARNINGS_FORECAST": "cons_fwd",
    "CASH": "CASH",
}
NUM = re.compile(r"[-–]?\d+\.\d+")


def _panel(lines: list[str], start_kw: str, end_kw: str) -> dict:
    txt = "\n".join(lines)
    seg = txt[txt.index(start_kw):txt.index(end_kw)]
    out = {}
    for label, key in LABELS.items():
        # anchor at line start; CASH must NOT match CASH_FLOW / NON_CASH_*
        pat = re.compile(rf"(?m)^\s*{re.escape(label)}(?![_A-Za-z])\s+(.+)$")
        m = pat.search(seg)
        if not m:
            raise ValueError(f"label not found in panel: {label}")
        nums = [float(x.replace("–", "-")) for x in NUM.findall(m.group(1))]
        out[key] = {"campello_label": label,
                    "treated": nums[0], "control": nums[1]}
    return out


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    data = {
        "source": "Campello et al. (2022 JFQA) Supplementary Table C.2",
        "method": ("3-NN with replacement; propensity = lagged STOCK_RETURNS, "
                   "1q-ahead CONSENSUS_EARNINGS_FORECAST, TOBIN_Q, CASH_FLOW, "
                   "SALES_GROWTH, SIZE"),
        "extracted_from": str(SRC.relative_to(ROOT)),
        "market": _panel(lines, "Panel A: Market-Based Approach",
                         "Panel B: Textual-Search-Based Approach"),
        "textual": _panel(lines, "Panel B: Textual-Search-Based Approach",
                          "Table C.1"),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "campello_c2_matched.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"written: {OUT / 'campello_c2_matched.json'}")
    for arm in ("market", "textual"):
        print(f"\n{arm}:")
        for key, v in data[arm].items():
            print(f"  {v['campello_label']:<28} T={v['treated']:+.3f} "
                  f"C={v['control']:+.3f}")


if __name__ == "__main__":
    main()
