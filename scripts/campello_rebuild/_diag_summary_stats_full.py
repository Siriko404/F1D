"""DIAG — FULL summary-stats side-by-side: rebuild vs Campello Table 1
(Panels A/B/C). Sina-requested 2026-05-17: "make sure all our variables
min/max/median/mean/percentiles closely match theirs, so we are 100% sure
we are not feeding garbage."

CONSTRAINT (primary source, table1_pdfpage21.txt L369): Campello Table 1
reports ONLY  Mean | SD | Median | IQR | N  for every variable, in three
panels:
    Panel A = universe of COMPUSTAT firms      ~ our UNIVERSE (step1)
    Panel B = treated  (top tercile of βᵁᴷ)    ~ our TREATED (step3)
    Panel C = control  (bottom tercile of βᵁᴷ) ~ our CONTROL (step3)
There is NO published min / max / p1 / p25 / p75 / p99. So:
  • mean / SD / median / IQR / N  → apples-to-apples vs Campello (winsorized)
  • our RAW min / max / range     → garbage sniff, NO Campello benchmark
    (winsorized min/max = the 1% caps by construction → useless for that)

Universe is NOT identical (ours = step1 ∩ βᵁᴷ-estimable, larger-firm
skew); moment gaps can be sample composition, not garbage. This catches
gross garbage / sign flips / scale blowups, NOT a perfect match (chasing
one = symptom-chasing, forbidden). No verdict — evidence for Sina.

Reuses the validated machinery in _diag_moment_fingerprint (no reinvent).
Read-only. Writes tmp/campello_summary_stats_compare_2026_05_17.md + console.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _diag_moment_fingerprint import (  # validated, reused verbatim
    QLO, QHI, ROOT, T1_EXTRACT, _build, _cash_both, _latest, _wins_within,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT_MD = ROOT / "tmp" / "campello_summary_stats_compare_2026_05_17.md"

# var key in Campello extract  ->  display label
CAMP_KEYS = {
    "CASH": "CASH",
    "TOBIN_Q": "TOBIN_Q",
    "CASH_FLOW": "CASH_FLOW",
    "SIZE(LogAssets)": "SIZE",
    "SALES_GROWTH": "SALES_GROWTH",
    "CONSENSUS_EARNINGS_FORECAST": "CONSENSUS_EPS",
    "STOCK_RETURNS": "STOCK_RETURNS",
}
_ROW = re.compile(
    r"^([A-Z][A-Z0-9_&]+(?:\([^)]*\))?)\s+"
    r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+"
    r"([\d,]+)\s*$")


def _parse_panel(start_tok: str, end_tok: str) -> dict:
    txt = T1_EXTRACT.read_text(encoding="utf-8")
    seg = txt.split(start_tok)[-1].split(end_tok)[0]
    out = {}
    for ln in seg.splitlines():
        m = _ROW.match(ln.strip())
        if m:
            out[m.group(1)] = dict(
                mean=float(m.group(2)), sd=float(m.group(3)),
                med=float(m.group(4)), iqr=float(m.group(5)),
                n=int(m.group(6).replace(",", "")))
    return out


CAMP = {
    "UNIVERSE": _parse_panel("PanelA.COMPUSTAT", "Market-BasedApproach"),
    "TREATED": _parse_panel("PanelB.TreatedFirms:", "Market-BasedApproach"),
    "CONTROL": _parse_panel("PanelC.ControlFirms:", "(continuedonnextpage)"),
}


def _raw(s: pd.Series) -> dict:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf],
                                                  np.nan).dropna()
    if s.empty:
        return dict(n=0, mn=np.nan, mx=np.nan)
    return dict(n=int(s.size), mn=float(s.min()), mx=float(s.max()))


def _wmom(s: pd.Series) -> dict:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf],
                                                  np.nan).dropna()
    if s.empty:
        return dict(n=0, mean=np.nan, sd=np.nan, med=np.nan, iqr=np.nan,
                    p1=np.nan, p25=np.nan, p75=np.nan, p99=np.nan)
    p25, p75 = float(s.quantile(.25)), float(s.quantile(.75))
    return dict(n=int(s.size), mean=float(s.mean()), sd=float(s.std(ddof=1)),
                med=float(s.median()), iqr=p75 - p25,
                p1=float(s.quantile(.01)), p25=p25, p75=p75,
                p99=float(s.quantile(.99)))


def _flag(o: dict, c: dict | None) -> str:
    """Crude HINT only (not a verdict): is the winsorized fingerprint in
    the same ballpark as Campello? Tol = 25% of scale on mean & median,
    same sign required."""
    if not c or o["n"] == 0:
        return "—"
    def near(a, b):
        return abs(a - b) <= 0.25 * max(abs(b), 0.05) and (a >= 0) == (b >= 0)
    return "MATCH" if (near(o["mean"], c["mean"]) and
                       near(o["med"], c["med"])) else "CHECK"


def _series(scope_uni: set, scope_g: set | None,
            df: pd.DataFrame, col: str) -> tuple[pd.Series, pd.Series]:
    """Returns (raw_series, winsorized_series) restricted to window +
    scope. Winsor 1% within cal_yr_qtr (Campello convention)."""
    d = df[(df.cal_yr_qtr >= QLO) & (df.cal_yr_qtr <= QHI)].copy()
    gset = scope_g if scope_g is not None else scope_uni
    d = d[d.gvkey.isin(gset)]
    d = d.dropna(subset=[col])
    if d.empty:
        return pd.Series(dtype=float), pd.Series(dtype=float)
    return d[col], _wins_within(d, col)


def main() -> None:
    s1d, s3d = _latest("step1_sample"), _latest("step3_treatment")
    s1 = pd.read_parquet(s1d / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    s1["cal_yr_qtr"] = s1["cal_yr_qtr"].astype("int64")
    trt = pd.read_parquet(s3d / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    trt = trt[trt["in_step1"]]
    UNI = set(s1.gvkey)
    G_T = set(trt[trt.group == "treated"].gvkey)
    G_C = set(trt[trt.group == "control"].gvkey)
    scopes = (("UNIVERSE", None), ("TREATED", G_T), ("CONTROL", G_C))
    print(f"step1={s1d.name}  step3={s3d.name}\n"
          f"universe={len(UNI):,}  treated={len(G_T):,}  "
          f"control={len(G_C):,}\n")

    # Assemble each variable as gvkey/cal_yr_qtr/<col> frames.
    cash = _cash_both()
    sz = s1[s1.atq > 0].copy()
    sz["SIZE"] = np.log(sz["atq"])
    sz = sz[["gvkey", "cal_yr_qtr", "SIZE"]]
    builders = {
        "STOCK_RETURNS": "BrexitStockReturnBuilder",
        "TOBIN_Q": "BrexitTobinsQBuilder",
        "CASH_FLOW": "BrexitCashFlowBuilder",
        "SALES_GROWTH": "BrexitSalesGrowthBuilder",
    }
    frames: dict[str, tuple[pd.DataFrame, str]] = {
        "CASH_T1 (cheq/atq_l1)": (cash, "CASH_T1"),
        "CASH_T8 (cheq/(atq-cheq)_l1)": (cash, "CASH_T8"),
        "SIZE": (sz, "SIZE"),
    }
    for disp, cls in builders.items():
        try:
            b = _build(cls)               # gvkey/cal_yr_qtr/v
            frames[disp] = (b.rename(columns={"v": disp}), disp)
        except Exception as e:             # noqa: BLE001
            print(f"  build error {disp}: {e}")

    # CONSENSUS_EPS = Sina-ratified IBES-summary statsum MEANEST z-score
    # (forecast-only; §G.8) — NOT the superseded Detail within-firm
    # z-score builder. Single source of truth reused (no code drift).
    try:
        from _build_final_did_statsum_consensus import _statsum_meanest_z
        cse = _statsum_meanest_z().rename(
            columns={"cons_fwd": "CONSENSUS_EPS"})
        frames["CONSENSUS_EPS"] = (cse, "CONSENSUS_EPS")
    except Exception as e:                 # noqa: BLE001
        print(f"  build error CONSENSUS_EPS (statsum): {e}")

    camp_key_for = {
        "CASH_T1 (cheq/atq_l1)": "CASH", "CASH_T8 (cheq/(atq-cheq)_l1)": "CASH",
        "SIZE": "SIZE(LogAssets)", "STOCK_RETURNS": "STOCK_RETURNS",
        "TOBIN_Q": "TOBIN_Q", "CASH_FLOW": "CASH_FLOW",
        "SALES_GROWTH": "SALES_GROWTH",
        "CONSENSUS_EPS": "CONSENSUS_EARNINGS_FORECAST",
    }

    md: list[str] = [
        "# Campello Table 1 vs rebuild — full summary-stats compare",
        "",
        f"step1=`{s1d.name}`  step3=`{s3d.name}`  window 2010Q1–2015Q4  "
        "1% winsor within qtr (Campello convention).",
        "",
        "Campello publishes **only mean/SD/median/IQR/N** (no min/max/"
        "pctiles). `ours` = winsorized (apples-to-apples). `RAWmin/RAWmax/"
        "RAWn` = pre-winsor garbage sniff, **no Campello benchmark**. "
        "FLAG = crude same-ballpark HINT (mean&med within 25% & same sign), "
        "NOT a verdict. Universe differs (ours = step1 ∩ βᵁᴷ-estimable, "
        "larger-firm skew) — gaps may be composition, not garbage; perfect "
        "match is NOT the bar (symptom-chasing forbidden).",
    ]

    for scope, gset in scopes:
        cmp = CAMP[scope]
        hdr = (f"\n## {scope}  "
               f"(~Campello Panel {'A' if scope=='UNIVERSE' else 'B' if scope=='TREATED' else 'C'})")
        print(hdr)
        md.append(hdr)
        cols = ("variable", "RAWn", "RAWmin", "RAWmax",
                "ours:mean", "SD", "med", "IQR", "p1", "p99",
                "C:mean", "C:SD", "C:med", "C:IQR", "C:N", "FLAG")
        md.append("\n| " + " | ".join(cols) + " |")
        md.append("|" + "---|" * len(cols))
        for disp, (fr, col) in frames.items():
            raw_s, win_s = _series(UNI, gset, fr, col)
            r, w = _raw(raw_s), _wmom(win_s)
            c = cmp.get(camp_key_for[disp])
            fl = _flag(w, c)
            def f(x, d=3):
                return "n=0" if (isinstance(x, float) and np.isnan(x)) \
                    else (f"{x:,}" if isinstance(x, int) else f"{x:+.{d}f}")
            row = [
                disp, f"{r['n']:,}", f(r["mn"]), f(r["mx"]),
                f(w["mean"]), f(w["sd"]), f(w["med"]), f(w["iqr"]),
                f(w["p1"]), f(w["p99"]),
                f(c["mean"]) if c else "—", f(c["sd"]) if c else "—",
                f(c["med"]) if c else "—", f(c["iqr"]) if c else "—",
                f"{c['n']:,}" if c else "—", fl,
            ]
            md.append("| " + " | ".join(row) + " |")
            print(f"  {disp:30s} ours mean {w['mean']:+.3f} SD {w['sd']:.3f} "
                  f"med {w['med']:+.3f} IQR {w['iqr']:.3f} "
                  f"| RAW[{r['mn']:+.2f},{r['mx']:+.2f}] n{r['n']:,} "
                  f"| C "
                  + (f"mean {c['mean']:+.3f} SD {c['sd']:.3f} "
                     f"med {c['med']:+.3f} IQR {c['iqr']:.3f} N{c['n']:,}"
                     if c else "n/a")
                  + f"  [{fl}]")

    md += [
        "",
        "## How to read FLAG=CHECK",
        "CHECK = winsorized mean/median NOT in Campello's ballpark for that "
        "panel. Could be (a) real construction deviation, (b) sample-"
        "composition (βᵁᴷ-estimable ≠ full COMPUSTAT), or (c) a "
        "Sina-ratified documented non-replication: CONSENSUS_EPS = "
        "IBES-summary statsum MEANEST z-score (forecast-only; §G.8; "
        "z ⇒ SD≈1 vs Campello reported 3.51) / CASH_T8 = superseded "
        "net-of-cash reading (canonical DV = CASH_T1, §F.2). All on "
        "record in campello_variable_audit_2026_05_17.md. No verdict "
        "(gated on Sina).",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nwritten → {OUT_MD}")


if __name__ == "__main__":
    main()
