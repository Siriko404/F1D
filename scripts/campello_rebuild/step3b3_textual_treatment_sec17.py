"""STEP 3b3 — TEXTUAL treatment, §1+§7-SCOPED (Sina 2026-05-18).

Variant of step3b. Same VERBATIM 9-keyword Campello list and >5/0
rule (§IV.A.2 + fn14), but keyword counting is RESTRICTED to 10-K
Item 1 (Business) + Item 7 (MD&A) — Campello's DOCUMENTED text-parse
house convention.

EVIDENCE for the scope (programmatic, supp_FULL.txt L1341-1343,
Appendix E AUTOMATION measure, verbatim):
  "measures how frequently the top-100 automation keywords appear in
   the firm's business description (Section 1 of the 10-K form) and
   management discussion (Section 7 of the 10-K form)."
The Brexit §IV.A.2 text doesn't restate this (says only "parsing
firms' 2015 10-K filings"), so §1+7 for Brexit is implied-by-house-
convention, NOT a Brexit-specific verbatim statement — a labeled,
evidence-grounded variant alongside the verbatim full-filing arm
(step3b). NOT symptom-chasing: scope is Campello's own documented
method, not a target-fitted knob; both arms reported.

Item-boundary parse = standard Loughran-McDonald longest-span
heuristic (skips the table-of-contents short entry; body section is
the long span between the item header and its terminator). Filings
where Item 1 OR Item 7 cannot be located are EXCLUDED (no silent
full-text fallback — that would reintroduce the over-count) and
counted.

Spec/data-plumbing identical to step3b otherwise (zip stream in-place,
SRAF filename, CCM time-varying CIK→gvkey LINKPRIM∈{P,C}/{LU,LC},
dedupe latest filing per CIK). Output:
outputs/campello_rebuild/step3b3_textual_treatment_sec17/<ts>/.
No commit; no verdict (gated); off-ramp forbidden.
"""
from __future__ import annotations

import json
import re
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "inputs" / "10-X_C_2015_10Konly.zip"
CCM = ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
OUTBASE = ROOT / "outputs" / "campello_rebuild" / \
    "step3b3_textual_treatment_sec17"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Campello verbatim 9 keywords (buk_pdfpage14 L229 + fn14 L256-257) —
# UNCHANGED (Sina chose the §1+7 scope lever, not the keyword drop).
PAT_WB = re.compile(
    r"\b(brexit|great britain|uncertainty|referendum|uncertain|"
    r"united kingdom|uk)\b", re.IGNORECASE)
PAT_ABBR = re.compile(r"(?<![A-Za-z])(u\.k\.|g\.b\.)(?![A-Za-z])",
                      re.IGNORECASE)
FNAME = re.compile(
    r"\d{4}/QTR\d/(\d{8})_([A-Z0-9-]+)_edgar_data_(\d+)_([A-Za-z0-9-]+)"
    r"\.txt")
# Item header: "ITEM 7", "Item 7.", "ITEM 1A -", "Item 7A:" etc.
ITEM_RE = re.compile(r"item[\s ]{0,4}(\d{1,2}[ab]?)\s*[\.\:\)\-—]",
                     re.IGNORECASE)
HIGH_T, ZERO_T = 5, 0
CAMPELLO = {"treated": 807, "control": 433}
MIN_SEC = 200          # min chars for a span to count as a real section


def _norm_item(g: str) -> str:
    return g.lower().strip()


def _best_span(text: str, target: str, terms: set[str]) -> str | None:
    """Longest text span from a `target` item header to the nearest
    following terminator header (LM heuristic; TOC entry is short)."""
    marks = [(_norm_item(m.group(1)), m.start(), m.end())
             for m in ITEM_RE.finditer(text)]
    if not marks:
        return None
    best, best_len = None, 0
    for i, (num, s, e) in enumerate(marks):
        if num != target:
            continue
        end = len(text)
        for num2, s2, _e2 in marks[i + 1:]:
            if num2 in terms:
                end = s2
                break
        seg = text[e:end]
        if len(seg) > best_len:
            best, best_len = seg, len(seg)
    return best if (best is not None and best_len >= MIN_SEC) else None


def _sec17(text: str) -> str | None:
    """Item1 (Business) + Item7 (MD&A) concatenated, or None if either
    cannot be located."""
    s1 = _best_span(text, "1", {"1a", "1b", "2", "3", "4"})
    s7 = _best_span(text, "7", {"7a", "8", "9"})
    if s1 is None or s7 is None:
        return None
    return s1 + "\n" + s7


def _count(text: str) -> int:
    return len(PAT_WB.findall(text)) + len(PAT_ABBR.findall(text))


def _load_ccm() -> pd.DataFrame:
    c = pd.read_parquet(CCM, columns=["gvkey", "cik", "LINKPRIM",
                                      "LINKTYPE", "LINKDT", "LINKENDDT"])
    c = c[c["LINKPRIM"].isin(["P", "C"])
          & c["LINKTYPE"].isin(["LU", "LC"])].copy()
    c["LINKDT"] = pd.to_datetime(c["LINKDT"], errors="coerce")
    c["LINKENDDT"] = pd.to_datetime(
        c["LINKENDDT"].astype(str).replace({"E": "2099-12-31"}),
        errors="coerce")
    c["cik"] = pd.to_numeric(c["cik"], errors="coerce")
    c = c.dropna(subset=["gvkey", "cik", "LINKDT", "LINKENDDT"])
    c["cik"] = c["cik"].astype("int64")
    c["gvkey"] = c["gvkey"].astype("int64").astype(str).str.zfill(6)
    return c[["gvkey", "cik", "LINKDT", "LINKENDDT"]]


def main() -> None:
    print("=== STEP 3b3 — TEXTUAL treatment §1+§7-scoped (9-kw) ===\n")
    t0 = time.time()
    rows, n_dir, n_badname, n_decerr, n_secfail = [], 0, 0, 0, 0
    with zipfile.ZipFile(ZIP, "r") as zf:
        infos = zf.infolist()
        print(f"zip entries: {len(infos):,}  (streaming, ≤1 resident)")
        for i, info in enumerate(infos, 1):
            if info.is_dir() or info.file_size == 0:
                n_dir += 1
                continue
            m = FNAME.match(info.filename)
            if not m:
                n_badname += 1
                continue
            date_str, ftype, cik, _acc = m.groups()
            try:
                with zf.open(info, "r") as f:
                    text = f.read().decode("utf-8", errors="replace")
            except Exception:
                n_decerr += 1
                continue
            scoped = _sec17(text)
            del text
            if scoped is None:
                n_secfail += 1
                continue                  # exclude — no silent fallback
            tot = _count(scoped)
            del scoped
            rows.append({"filing_date": pd.to_datetime(date_str,
                         format="%Y%m%d"), "filing_type": ftype,
                         "cik": int(cik), "total_count": tot})
            if i % 1500 == 0:
                print(f"  …{i:,}/{len(infos):,} "
                      f"(secfail {n_secfail:,}, {time.time()-t0:.0f}s)")
    f = pd.DataFrame(rows)
    print(f"\nparsed {len(f):,} filings WITH §1+7  (dirs {n_dir}, "
          f"badname {n_badname}, decode-err {n_decerr}, §1+7-fail "
          f"{n_secfail:,})  {time.time()-t0:.0f}s")

    f = (f.sort_values(["cik", "filing_date"], kind="stable")
           .drop_duplicates("cik", keep="last"))
    print(f"after CIK dedupe (latest filing): {len(f):,} CIKs")

    ccm = _load_ccm()
    mg = f.merge(ccm, on="cik", how="left")
    ok = ((mg["filing_date"] >= mg["LINKDT"])
          & (mg["filing_date"] <= mg["LINKENDDT"]))
    mp = (mg[ok].sort_values(["cik", "LINKDT"], kind="stable")
              .drop_duplicates("cik", keep="first"))
    n_unmapped = f["cik"].nunique() - mp["cik"].nunique()
    print(f"CIK→gvkey mapped: {mp['cik'].nunique():,}  "
          f"unmapped: {n_unmapped:,}")

    g = mp.groupby("gvkey", as_index=False)["total_count"].sum()
    g["group"] = "_excl"
    g.loc[g["total_count"] == 0, "group"] = "control"
    g.loc[g["total_count"] > HIGH_T, "group"] = "treated"
    g["HIGH_UK_EXPOSURE"] = g["group"].map(
        {"treated": 1.0, "control": 0.0}).astype("float64")

    nt = int((g["group"] == "treated").sum())
    nc = int((g["group"] == "control").sum())
    nx = int((g["group"] == "_excl").sum())
    print(f"\n  treated (>5)  : {nt:,}   (Campello 807)")
    print(f"  control (==0) : {nc:,}   (Campello 433)")
    print(f"  excluded(1-5) : {nx:,}")
    print(f"  total firms   : {len(g):,}")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    od = OUTBASE / ts
    od.mkdir(parents=True, exist_ok=True)
    keep = g[g["group"].isin(["treated", "control"])][
        ["gvkey", "total_count", "group", "HIGH_UK_EXPOSURE"]]
    keep.to_parquet(od / "treatment_textual.parquet", index=False)
    (od / "summary.json").write_text(json.dumps({
        "step": "3b3_textual_treatment_sec17",
        "scope": "10-K Item 1 (Business) + Item 7 (MD&A) ONLY — "
            "Campello documented text-parse house convention "
            "(supp_FULL.txt L1341-1343 Appendix E, verbatim for the "
            "automation measure; implied-by-house-convention for "
            "Brexit, NOT a Brexit-specific verbatim statement). "
            "Loughran-McDonald longest-span Item parse; TOC skipped; "
            "§1+7-unparseable filings EXCLUDED (no full-text fallback).",
        "keywords": ["Brexit", "Great Britain", "Uncertainty",
                     "Referendum", "Uncertain", "United Kingdom",
                     "UK", "U.K.", "G.B."],
        "rule": "treated >5 / control ==0 / 1-5 excluded (verbatim)",
        "n_filings_with_sec17": int(len(f)),
        "n_sec17_parse_fail_excluded": int(n_secfail),
        "n_ciks_after_dedupe": int(f["cik"].nunique()),
        "n_cik_mapped": int(mp["cik"].nunique()),
        "n_unmapped": int(n_unmapped),
        "treated": nt, "control": nc, "excluded_1_5": nx,
        "total_firms": int(len(g)),
        "campello_realized": CAMPELLO,
        "campello_t8_textual_cash_benchmark": {
            "delta_hat": 0.357, "se": 0.062, "n": 24195,
            "rsquared": 0.24, "stars": "***",
            "source": "Campello et al. 2022 JFQA Table 8 col.2 "
                "(programmatic table8_pdfpage31.txt L298-308)"},
        "note": "labeled §1+7 variant ALONGSIDE the verbatim "
            "full-filing arm (step3b); both reported; verdict gated.",
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {od}")


if __name__ == "__main__":
    main()
