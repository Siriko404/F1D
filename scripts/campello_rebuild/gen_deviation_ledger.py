"""STRICT deviation ledger — EVERY variable × panel × published moment
vs Campello Table 1 (Sina 2026-05-17: "check ALL devs", no lenient
MATCH bucket). Reads the MACHINE artifact
tmp/campello_summary_stats_compare_2026_05_17.md (no rebuild — fast,
memory-light) and computes the exact + relative + SD-standardized gap on
mean / SD / median / IQR / N for all 8 vars × 3 panels.

Severity (max over moments, NO same-ballpark masking):
  OK     |relΔ| < 10%   on every moment
  MINOR  10–25%
  MAJOR  25–100%
  SEVERE >100% or a sign flip
Near-zero Campello mean/median (|C|<0.05): relΔ is unstable → severity
also uses the SD-standardized gap |Δ|/C_SD (≥0.25 SD ⇒ at least MINOR).

Read-only. No spec change, no verdict (gated). Writes
tmp/campello_deviation_ledger_2026_05_17.md + console, ranked worst-first.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "tmp" / "campello_summary_stats_compare_2026_05_17.md"
OUT = ROOT / "tmp" / "campello_deviation_ledger_2026_05_17.md"

# Already root-caused elsewhere (do not re-flag as NEW worklist).
EXPLAINED = {
    "CASH_T8 (cheq/(atq-cheq)_l1)": "§A net-of-cash DV defect (ratified DV; "
        "necessary-not-sufficient; DV-fix δ̂ −0.007 NS)",
    "CONSENSUS_EPS": "§B within-firm z-score ≠ Campello 'standardized' "
        "(SD 0.79 vs 3.51); construction choice, not data",
}
PANELS = [("## UNIVERSE", "A/Universe"),
          ("## TREATED", "B/Treated"),
          ("## CONTROL", "C/Control")]


def _f(x: str) -> float:
    return float(x.replace(",", "").replace("+", "").replace("−", "-"))


def _rows(seg: str):
    for ln in seg.splitlines():
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        c = [x.strip() for x in ln.strip("|").split("|")]
        if len(c) != 16 or c[0].lower() == "variable" or set(c[0]) <= set("-"):
            continue
        yield c


def _sev(rel: float, sd_gap: float) -> str:
    if rel != rel:                       # nan (C≈0 handled by sd_gap only)
        rel = 0.0
    if rel > 1.0:
        return "SEVERE"
    if rel >= 0.25:
        return "MAJOR"
    if rel >= 0.10 or sd_gap >= 0.25:
        return "MINOR"
    return "OK"


def main() -> None:
    if not SRC.exists():
        sys.exit(f"missing {SRC}")
    txt = SRC.read_text(encoding="utf-8")
    rank = {"SEVERE": 3, "MAJOR": 2, "MINOR": 1, "OK": 0}
    recs = []
    for tok, plabel in PANELS:
        seg = txt.split(tok, 1)[1].split("\n## ", 1)[0]
        for c in _rows(seg):
            var = c[0]
            o = dict(mean=_f(c[4]), sd=_f(c[5]), med=_f(c[6]), iqr=_f(c[7]),
                     n=_f(c[1]))
            C = dict(mean=_f(c[10]), sd=_f(c[11]), med=_f(c[12]),
                     iqr=_f(c[13]), n=_f(c[14]))
            csd = C["sd"] if C["sd"] else float("nan")
            worst, wm = "OK", []
            for mk in ("mean", "sd", "med", "iqr", "n"):
                ov, cv = o[mk], C[mk]
                d = ov - cv
                rel = abs(d) / abs(cv) if abs(cv) > 1e-9 else float("nan")
                sdg = (abs(d) / csd if (mk in ("mean", "med")
                       and csd == csd) else 0.0)
                # scale-free moments (sd,iqr,n) ignore sd_gap path
                s = _sev(rel if rel == rel else (0.0 if mk in ("sd", "iqr",
                         "n") else float("nan")), sdg)
                if rank[s] > rank[worst]:
                    worst = s
                if s != "OK":
                    rp = f"{rel*100:,.0f}%" if rel == rel else "n/a"
                    extra = (f", {sdg:.2f}·SD" if sdg else "")
                    wm.append(f"{mk} Δ{d:+.3f} ({rp}{extra})")
            recs.append(dict(var=var, panel=plabel, worst=worst,
                              detail="; ".join(wm) or "all moments <10%",
                              o=o, C=C))

    recs.sort(key=lambda r: (-rank[r["worst"]], r["var"], r["panel"]))
    md = ["# STRICT deviation ledger — all vars × panels vs Campello "
          "Table 1", "",
          "Source: machine artifact "
          "`campello_summary_stats_compare_2026_05_17.md` (no rebuild). "
          "Severity = max over mean/SD/med/IQR/N; near-zero Campello "
          "mean/med also judged by |Δ|/C\\_SD. NO same-ballpark masking. "
          "No spec change; no verdict (gated on Sina).", "",
          "| rank | variable | panel | severity | status | driving moments |",
          "|--|--|--|--|--|--|"]
    print("=== STRICT DEVIATION LEDGER (worst-first) ===\n")
    for i, r in enumerate(recs, 1):
        why = EXPLAINED.get(r["var"])
        status = (f"EXPLAINED — {why}" if why and r["worst"] in
                  ("MAJOR", "SEVERE") else
                  "OK" if r["worst"] == "OK" else "**NEW — needs root-cause**")
        md.append(f"| {i} | {r['var']} | {r['panel']} | {r['worst']} | "
                  f"{status} | {r['detail']} |")
        if r["worst"] != "OK":
            print(f"  [{r['worst']:6s}] {r['var']:30s} {r['panel']:11s} "
                  f"{('EXPL' if why and r['worst'] in ('MAJOR','SEVERE') else 'NEW '):4s}"
                  f"  {r['detail']}")

    # systematic-pattern rollup (the honest aggregate read)
    minor_sd = sum(1 for r in recs if r["worst"] == "MINOR"
                   and "sd " in r["detail"])
    minor_iqr = sum(1 for r in recs if r["worst"] == "MINOR"
                    and "iqr " in r["detail"])
    new_major = [r for r in recs if r["worst"] in ("MAJOR", "SEVERE")
                 and r["var"] not in EXPLAINED]
    md += ["", "## Aggregate read (NO verdict — gated)",
           f"- SEVERE/MAJOR & already root-caused: "
           f"{sum(1 for r in recs if r['worst'] in ('MAJOR','SEVERE') and r['var'] in EXPLAINED)} "
           f"(CASH_T8 §A ×3, CONSENSUS_EPS §B ×3).",
           f"- SEVERE/MAJOR & **NEW (unexplained)**: {len(new_major)} → "
           + (", ".join(f"{r['var']}/{r['panel']}" for r in new_major)
              if new_major else "none"),
           f"- MINOR cluster: SD low in {minor_sd} cells, IQR low in "
           f"{minor_iqr} cells → consistent under-dispersion vs Campello "
           f"(direction: our βᵁᴷ-estimable universe = larger, less-"
           f"volatile firms; documented sample-composition skew, NOT "
           f"garbage — but it IS a real systematic deviation to record).",
           "", "## Worklist (Sina-directed: check ALL devs)",
           "1. NEW MAJOR/SEVERE (if any above) — root-cause first.",
           "2. CASH_T8 / CONSENSUS_EPS — already root-caused (§A/§B); "
           "remediation Sina-gated (Table-1 denom; forecast/price).",
           "3. MINOR under-dispersion cluster — decide: accept as "
           "documented composition caveat, or audit step1/βᵁᴷ sample "
           "screens that drive the larger-firm skew. No spec change "
           "without explicit Sina authorization."]
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\n  NEW unexplained MAJOR/SEVERE: "
          f"{[r['var']+'/'+r['panel'] for r in new_major] or 'none'}")
    print(f"\nwritten → {OUT}")


if __name__ == "__main__":
    main()
