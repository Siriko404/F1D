"""Per-keyword × per-SECTION decomposition of the textual Brexit count.
FAST (single-pass regex, multiprocessed) + memory-aware + FULL DETAIL DUMP.

Splits EVERY 2015 10-K into ALL its Item sections (preamble, 1, 1A, 1B, 2, 3,
4, 5, 6, 7, 7A, 8, 9, 9A, 9B, 10..15 — whatever headers appear) and counts
each of the 9 Brexit terms in EVERY section, plus a whole-document count.
Writes:

  per_filing.json    one record/filing: every section's per-term counts + len
  detail_long.parquet  flat (filename, cik, gvkey, section, term, count, sec_len)
                       — ~1.6M rows, easy to query/pivot
  firm_summary.json  one record/gvkey (latest filing, CCM-mapped, summed):
                     per-term firm totals + whole/§1+7 group (treated/control)
  summary.json       aggregate per-term table (whole & §1+7) vs Campello 807/433

Perf: one combined regex (single finditer/section), ProcessPoolExecutor over
filings; workers hold ONE 10-K at a time, free text, return only numbers/strings.
Reuses step3b3's Item-header regex + CCM loader (no drift). Read-only on inputs.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))
ZIP = ROOT / "inputs" / "10-X_C_2015_10Konly.zip"
OUTBASE = ROOT / "outputs" / "campello_rebuild" / "textual_keyword_decomp"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import step3b3_textual_treatment_sec17 as s3  # noqa: E402

FNAME = re.compile(
    r"\d{4}/QTR\d/(\d{8})_([A-Z0-9-]+)_edgar_data_(\d+)_([A-Za-z0-9-]+)\.txt")
COMBINED = re.compile(
    r"\b(brexit|great britain|uncertainty|referendum|uncertain|"
    r"united kingdom|uk)\b|(?<![A-Za-z])(u\.k\.|g\.b\.)(?![A-Za-z])", re.I)
TERMS = ["brexit", "great britain", "uncertainty", "referendum", "uncertain",
         "united kingdom", "uk", "u.k.", "g.b."]
ITEM_RE = s3.ITEM_RE          # reuse exact header pattern
MIN_SEC = 1                   # keep every non-empty body span (full detail)


def _count_terms(text: str) -> dict:
    """ONE finditer pass; full 9-term dict (explicit zeros)."""
    d = {t: 0 for t in TERMS}
    for m in COMBINED.finditer(text):
        d[m.group(0).lower()] += 1
    return d


def _sections(text: str) -> dict:
    """Split into ALL Item sections. For each item label, the body = the
    LONGEST span from that header to the next (any) item header (TOC entry is
    short, so longest = body). '_preamble' = text before the first item.
    Returns {label: span_text}."""
    marks = [(s3._norm_item(m.group(1)), m.start(), m.end())
             for m in ITEM_RE.finditer(text)]
    secs: dict[str, str] = {}
    if not marks:
        secs["_preamble"] = text
        return secs
    pre = text[:marks[0][1]]
    if pre.strip():
        secs["_preamble"] = pre
    best_len: dict[str, int] = {}
    for i, (num, _s, e) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(text)
        seg = text[e:end]
        if len(seg) > best_len.get(num, -1):
            best_len[num] = len(seg)
            secs[num] = seg
    return {k: v for k, v in secs.items() if len(v) >= MIN_SEC}


def _process_batch(names: list[str]) -> list[dict]:
    """Worker: own zip handle; per filing record whole + every-section term
    counts + section lengths. Returns numeric/string dicts only (text freed)."""
    out = []
    with zipfile.ZipFile(ZIP, "r") as zf:
        for name in names:
            m = FNAME.match(name)
            if not m:
                continue
            date_str, ftype, cik, _acc = m.groups()
            try:
                with zf.open(name, "r") as f:
                    text = f.read().decode("utf-8", errors="replace")
            except Exception:
                continue
            whole = _count_terms(text)
            secs = _sections(text)
            sec_rec = {lbl: {"len": len(span), "counts": _count_terms(span)}
                       for lbl, span in secs.items()}
            del text, secs
            out.append({
                "filename": name, "cik": int(cik), "filing_date": date_str,
                "filing_type": ftype,
                "len_whole": sum(s["len"] for s in sec_rec.values()),
                "counts_whole": whole, "total_whole": sum(whole.values()),
                "n_sections": len(sec_rec),
                "sections_found": sorted(sec_rec.keys()),
                "sections": sec_rec,
            })
    return out


def _firm_summary(df: pd.DataFrame, ccm: pd.DataFrame) -> pd.DataFrame:
    """Dedupe latest filing/CIK, CCM time-map to gvkey, sum per-term per scope,
    classify >5/==0 for whole & §1+7. Mirrors step3b3 aggregation."""
    r = (df.sort_values(["cik", "filing_date"], kind="stable")
           .drop_duplicates("cik", keep="last"))
    mg = r.merge(ccm, on="cik", how="left")
    fd = pd.to_datetime(mg["filing_date"], format="%Y%m%d")
    ok = (fd >= mg["LINKDT"]) & (fd <= mg["LINKENDDT"])
    mp = (mg[ok].sort_values(["cik", "LINKDT"], kind="stable")
              .drop_duplicates("cik", keep="first"))
    cols = ([f"whole_{t}" for t in TERMS] + [f"sec17_{t}" for t in TERMS]
            + ["total_whole", "total_sec17"])
    g = mp.groupby("gvkey", as_index=False)[cols].sum()
    g["group_whole"] = "_excl"
    g.loc[g["total_whole"] == 0, "group_whole"] = "control"
    g.loc[g["total_whole"] > 5, "group_whole"] = "treated"
    g["group_sec17"] = "_excl"
    g.loc[g["total_sec17"] == 0, "group_sec17"] = "control"
    g.loc[g["total_sec17"] > 5, "group_sec17"] = "treated"
    return g


def main() -> None:
    t0 = time.time()
    with zipfile.ZipFile(ZIP, "r") as zf:
        names = [i.filename for i in zf.infolist()
                 if not i.is_dir() and i.file_size and FNAME.match(i.filename)]
    n = len(names)
    workers = max(1, (os.cpu_count() or 2) - 1)
    chunk = max(1, n // (workers * 4))
    batches = [names[i:i + chunk] for i in range(0, n, chunk)]
    print(f"{n:,} filings | {workers} workers | {len(batches)} batches")

    rows, done = [], 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(_process_batch, batches):
            rows.extend(res); done += 1
            if done % 8 == 0:
                print(f"  …{done}/{len(batches)}  ({len(rows):,} filings, "
                      f"{time.time()-t0:.0f}s)")
    print(f"parsed {len(rows):,} filings in {time.time()-t0:.0f}s")

    # Flat long-form (one row per filing×section×term) + wide DF for firm agg.
    long_recs, flat = [], []
    for r in rows:
        i1 = r["sections"].get("1", {}).get("counts")
        i7 = r["sections"].get("7", {}).get("counts")
        has17 = i1 is not None and i7 is not None
        d = {"cik": r["cik"], "filing_date": r["filing_date"],
             "total_whole": r["total_whole"],
             "total_sec17": (sum(i1.values()) + sum(i7.values())
                             if has17 else None)}
        for t in TERMS:
            d[f"whole_{t}"] = r["counts_whole"][t]
            d[f"sec17_{t}"] = (i1[t] + i7[t]) if has17 else None
        flat.append(d)
        # Write ALL 9 terms (including explicit 0s — e.g. brexit) for the whole
        # doc and EVERY found section. Zeros are signal here, not noise.
        for t in TERMS:
            long_recs.append((r["filename"], r["cik"], r["filing_date"],
                              "_whole", t, r["counts_whole"][t], r["len_whole"]))
        for lbl, sec in r["sections"].items():
            for t in TERMS:
                long_recs.append((r["filename"], r["cik"], r["filing_date"],
                                  lbl, t, sec["counts"][t], sec["len"]))
    df = pd.DataFrame(flat)
    ccm = s3._load_ccm()
    fsum = _firm_summary(df, ccm)

    # attach gvkey to long-form (latest filing already; just map any cik)
    long_df = pd.DataFrame(long_recs, columns=["filename", "cik", "filing_date",
                            "section", "term", "count", "sec_len"])

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    od = OUTBASE / ts
    od.mkdir(parents=True, exist_ok=True)
    with (od / "per_filing.json").open("w", encoding="utf-8") as f:
        json.dump(rows, f, separators=(",", ":"))      # compact (machine-read)
    long_df.to_parquet(od / "detail_long.parquet", index=False)
    (od / "firm_summary.json").write_text(
        json.dumps(fsum.to_dict(orient="records"), indent=1), encoding="utf-8")

    def _decomp(scope: str) -> list[dict]:
        sub = df.dropna(subset=[f"{scope}_{TERMS[0]}"])
        sub = (sub.sort_values(["cik", "filing_date"], kind="stable")
                  .drop_duplicates("cik", keep="last"))
        return sorted(
            [{"term": t, "total_occ": int(sub[f"{scope}_{t}"].sum()),
              "alone_gt5": int((sub[f"{scope}_{t}"] > 5).sum()),
              "filings_ge1": int((sub[f"{scope}_{t}"] > 0).sum())}
             for t in TERMS], key=lambda x: -x["total_occ"])

    tre_w = int((fsum["group_whole"] == "treated").sum())
    con_w = int((fsum["group_whole"] == "control").sum())
    tre_s = int((fsum["group_sec17"] == "treated").sum())
    con_s = int((fsum["group_sec17"] == "control").sum())
    # section coverage: how often each Item appears
    sec_cov = (long_df.groupby("section")["cik"].nunique()
               .sort_values(ascending=False).head(25).to_dict())
    summary = {
        "n_filings": len(rows), "runtime_s": round(time.time() - t0, 1),
        "campello": {"treated": 807, "control": 433},
        "whole_filing": {"treated": tre_w, "control": con_w,
                         "per_term": _decomp("whole")},
        "sec17_item1_plus_7": {"treated": tre_s, "control": con_s,
                               "per_term": _decomp("sec17")},
        "section_coverage_firms": {k: int(v) for k, v in sec_cov.items()},
    }
    (od / "summary.json").write_text(json.dumps(summary, indent=2),
                                     encoding="utf-8")

    print(f"\nWHOLE   treated={tre_w:,} control={con_w:,}  [Campello 807/433]")
    print(f"§1+7    treated={tre_s:,} control={con_s:,}  [Campello 807/433]")
    print(f"sections seen (top): "
          f"{', '.join(list(sec_cov.keys())[:15])}")
    print(f"\nwritten → {od}")
    print("  per_filing.json     every filing, every section, per-term counts")
    print("  detail_long.parquet flat filing×section×term (query/pivot)")
    print("  firm_summary.json   per-gvkey totals + group")
    print("  summary.json        aggregate per-term + section coverage")


if __name__ == "__main__":
    main()
