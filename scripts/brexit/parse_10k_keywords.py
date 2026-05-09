"""ETL one-shot: parse 9,275 SEC 10-K filings in inputs/10-X_C_2015_10Konly.zip
IN-PLACE (no extraction) → 9-keyword count per filing → durable parquet cache.

Replicates the Campello et al. 2022 JFQA Section IV.A.2 textual-search-based
Brexit exposure measure (spec lines 145-160 of tmp/3did_replication_v2_2026_05_08.md).

KEYWORDS (case-insensitive whole-word match, 9 total):
  Primary 3 (verbatim p.3191):  Brexit, Great Britain, Uncertainty
  Subsumed 6 (verbatim fn 14):  Referendum, Uncertain, United Kingdom, UK,
                                U.K., G.B.

REGEX SPLIT (per audit CRITICAL-1 fix). A single \\b-anchored alternation
silently misses U.K., u.k., G.B., g.b. because \\b between '.' (non-word) and
end-of-token is not a word boundary. Two patterns are used:
  PAT_WB   — 7 keywords with normal word edges, anchored by \\b...\\b
  PAT_ABBR — 2 abbreviations with embedded dots, anchored by lookbehind/lookahead
              (?<![A-Za-z])...(?![A-Za-z]) to prevent matching inside words like
              "trUKker" or "uk.com".

FILENAME PATTERN (per audit CRITICAL-2 + verified empirically 2026-05-08).
SRAF format is YYYY/QTRn/<YYYYMMDD>_<TYPE>_edgar_data_<CIK>_<accession>.txt
where TYPE in {10-K, 10-K-A, 10-KT, 10-KT-A}. The 5 zip-directory entries
(YYYY/, QTRn/) are skipped.

CIK → gvkey MAPPING (per audit MAJOR-5 — time-varying linktable).
For each filing date t = YYYYMMDD parsed from filename:
  valid_link = ccm[ (LINKDT <= t <= LINKENDDT) &
                    (LINKPRIM == 'P') &
                    (LINKTYPE in {'LU', 'LC'}) ]
  if zero matches → unmapped_filings array; if multiple → keep first by LINKDT.

DEDUPLICATION (per audit MINOR-5 — 10-K/A amendments).
Per CIK keep latest filing_date; amendments (10-K-A) have later dates than
the original 10-K and therefore supersede correctly. Genuine off-cycle FY
change (rare) is also resolved to the most-recent filing closer to the Brexit
vote.

PERFORMANCE.
- Compiled re.findall is C-backed; ~milliseconds per filing × 9,275 ≈ 1-3 min.
- Memory peak: 1 file resident at a time (~5 MB max).
- Output ~9,000 rows of integer counts → trivial parquet (<1 MB).

Output:
    outputs/intermediate/brexit_10k_keyword_counts/<ts>/
      keyword_counts_per_filing.parquet  per-filing per-keyword counts
      parse_manifest.json                runtime stats + decode errors +
                                         unmapped_filings + n_filings_per_gvkey

Reusable: builders can read via get_latest_output_dir(); cache survives
across runs of the Brexit pipeline.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------- Regex patterns ----------------

# 7 keywords with normal word edges; \b on both sides.
PAT_WB = re.compile(
    r"\b(brexit|great britain|uncertainty|referendum|uncertain|united kingdom|uk)\b",
    re.IGNORECASE,
)

# 2 abbreviations with embedded dots; \b fails so use lookbehind/lookahead.
PAT_ABBR = re.compile(
    r"(?<![A-Za-z])(u\.k\.|g\.b\.)(?![A-Za-z])",
    re.IGNORECASE,
)

# Filename parser: <yyyy>/QTRn/YYYYMMDD_TYPE_edgar_data_CIK_accession.txt
FILENAME_RE = re.compile(
    r"\d{4}/QTR\d/(\d{8})_([A-Z0-9-]+)_edgar_data_(\d+)_([A-Za-z0-9-]+)\.txt"
)


# ---------------- Per-keyword diagnostic counters ----------------

# Each PAT_WB capture group must be lower-cased + categorized.
WB_KEYWORDS = ["brexit", "great britain", "uncertainty", "referendum", "uncertain", "united kingdom", "uk"]
ABBR_KEYWORDS = ["u.k.", "g.b."]


def count_keywords(text: str) -> Tuple[int, Dict[str, int]]:
    """Run both regex patterns; return total count + per-keyword counts."""
    wb_hits = PAT_WB.findall(text)
    abbr_hits = PAT_ABBR.findall(text)
    total = len(wb_hits) + len(abbr_hits)

    per_kw: Dict[str, int] = {kw: 0 for kw in WB_KEYWORDS + ABBR_KEYWORDS}
    for hit in wb_hits:
        per_kw[hit.lower()] += 1
    for hit in abbr_hits:
        per_kw[hit.lower()] += 1

    return total, per_kw


def parse_filename(filename: str) -> Dict[str, Any] | None:
    """Extract date/type/cik/accession from SRAF zip path. Returns None on no-match."""
    m = FILENAME_RE.match(filename)
    if not m:
        return None
    date_str, ftype, cik, accession = m.groups()
    return {
        "filing_date": pd.to_datetime(date_str, format="%Y%m%d"),
        "filing_type": ftype,
        "cik": int(cik),
        "accession": accession,
    }


# ---------------- CCM time-varying mapping ----------------

def load_ccm(ccm_path: Path) -> pd.DataFrame:
    """Load CCM linktable filtered for primary + canonical/unsearched links.

    Returns DataFrame with [gvkey (str), cik (int), LINKDT (dt), LINKENDDT (dt)].
    """
    ccm = pd.read_parquet(ccm_path)
    ccm = ccm[(ccm["LINKPRIM"] == "P") & (ccm["LINKTYPE"].isin(["LU", "LC"]))].copy()

    ccm["LINKENDDT"] = ccm["LINKENDDT"].astype(str).replace({"E": "2099-12-31"})
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
    ccm = ccm.dropna(subset=["LINKDT", "LINKENDDT", "cik"])
    ccm["cik"] = pd.to_numeric(ccm["cik"], errors="coerce").astype("Int64")
    ccm = ccm.dropna(subset=["cik"]).copy()
    ccm["cik"] = ccm["cik"].astype(int)
    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)
    return ccm[["gvkey", "cik", "LINKDT", "LINKENDDT"]]


def map_cik_to_gvkey(filings: pd.DataFrame, ccm: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """Date-windowed CIK → gvkey merge. Returns (mapped_filings, unmapped_diagnostics)."""
    # Cross-join on cik (small expansion since 1-2 ccm rows per cik typically),
    # then filter by date window.
    merged = filings.merge(ccm, on="cik", how="left")
    in_window = (merged["filing_date"] >= merged["LINKDT"]) & (merged["filing_date"] <= merged["LINKENDDT"])
    matched = merged[in_window].copy()

    # Multiple matches per filing: keep first by LINKDT.
    matched = matched.sort_values(["filing_filename", "LINKDT"], kind="stable")
    matched = matched.drop_duplicates(subset=["filing_filename"], keep="first")
    matched_keys = set(matched["filing_filename"])

    unmapped = filings[~filings["filing_filename"].isin(matched_keys)]
    unmapped_diag = unmapped[["filing_filename", "filing_date", "cik", "filing_type"]].head(50).to_dict("records")

    matched = matched.drop(columns=["LINKDT", "LINKENDDT"])
    return matched, unmapped_diag


# ---------------- Main ETL ----------------

def parse_zip(
    zip_path: Path,
    ccm_path: Path,
    progress_every: int = 500,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Stream all 10-K filings from zip → keyword counts → CIK→gvkey map → dedup.

    Returns (deduplicated keyword-count DataFrame, parse_manifest dict).
    """
    t0 = time.time()
    rows: List[Dict[str, Any]] = []
    decode_errors: List[Dict[str, str]] = []
    n_dirs = 0
    n_unmatched_names = 0
    file_size_total = 0

    logger.info(f"Opening zip: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        infos = zf.infolist()
        logger.info(f"  entries: {len(infos):,}")

        for idx, info in enumerate(infos, start=1):
            if info.is_dir() or info.file_size == 0:
                n_dirs += 1
                continue

            meta = parse_filename(info.filename)
            if meta is None:
                n_unmatched_names += 1
                continue

            try:
                with zf.open(info, "r") as f:
                    raw = f.read()
                text = raw.decode("utf-8", errors="replace")
            except Exception as e:
                decode_errors.append({"filename": info.filename, "error": str(e)})
                continue

            file_size_total += info.file_size
            total, per_kw = count_keywords(text)
            del text, raw  # free memory immediately

            row = {
                "filing_filename": info.filename,
                "filing_date": meta["filing_date"],
                "cik": meta["cik"],
                "filing_type": meta["filing_type"],
                "accession": meta["accession"],
                "file_size": info.file_size,
                "total_count": total,
            }
            # Promote per-keyword counts to columns with sanitized names.
            for kw, c in per_kw.items():
                col = "n_" + kw.replace(" ", "_").replace(".", "_dot").rstrip("_")
                row[col] = c
            rows.append(row)

            if idx % progress_every == 0:
                elapsed = time.time() - t0
                rate = idx / elapsed if elapsed > 0 else 0
                logger.info(
                    f"  [{idx:5d}/{len(infos):5d}] {rate:.1f} files/s, "
                    f"~{(len(infos) - idx) / max(rate, 1e-6):.0f}s remaining"
                )

    df = pd.DataFrame(rows)
    df["fiscal_year"] = df["filing_date"].dt.year - 1  # rough: most 10-Ks file in early year of Y for FY ending Y-1
    df.loc[df["filing_date"].dt.month >= 7, "fiscal_year"] += 1  # off-cycle 10-Ks (FYE later in year)

    parse_secs = time.time() - t0
    logger.info(f"  parsed {len(df):,} filings in {parse_secs:.1f}s")
    logger.info(f"  total bytes scanned: {file_size_total / 1e9:.2f} GB")
    logger.info(f"  decode errors: {len(decode_errors)}")
    logger.info(f"  skipped dirs/zero-len: {n_dirs}")
    logger.info(f"  unmatched filenames: {n_unmatched_names}")

    # CIK → gvkey time-varying merge.
    logger.info("Loading CCM linktable ...")
    ccm = load_ccm(ccm_path)
    logger.info(f"  CCM filtered (LINKPRIM=P, LINKTYPE in [LU,LC]): {len(ccm):,}")

    df_mapped, unmapped_diag = map_cik_to_gvkey(df, ccm)
    n_mapped = len(df_mapped)
    coverage = n_mapped / len(df) if len(df) else 0
    logger.info(f"  CIK-to-gvkey mapping: {n_mapped:,}/{len(df):,} = {coverage:.1%} coverage")

    # MINOR-5 fix: per CIK keep latest filing_date (amendments + off-cycle FY supersede).
    df_mapped = df_mapped.sort_values(["cik", "filing_date"], kind="stable")
    df_dedup = df_mapped.drop_duplicates(subset=["cik"], keep="last").reset_index(drop=True)
    n_dedup = len(df_dedup)
    n_amendments_dropped = n_mapped - n_dedup
    logger.info(f"  per-CIK dedup keep-latest: {n_dedup:,} (dropped {n_amendments_dropped:,} earlier filings/amendments)")

    # n_filings_per_gvkey distribution diagnostic — flag unexpected duplicates.
    pre_dedup_counts = df_mapped.groupby("gvkey").size()
    n_gvkey_multi = (pre_dedup_counts > 2).sum()  # any gvkey with >2 filings is unusual

    manifest = {
        "zip_path": str(zip_path),
        "ccm_path": str(ccm_path),
        "n_zip_entries": len(infos),
        "n_dirs_skipped": n_dirs,
        "n_unmatched_filenames": n_unmatched_names,
        "n_decode_errors": len(decode_errors),
        "decode_errors_sample": decode_errors[:20],
        "n_filings_parsed": int(len(df)),
        "n_filings_cik_mapped": int(n_mapped),
        "cik_to_gvkey_coverage": round(coverage, 4),
        "n_filings_after_dedup": int(n_dedup),
        "n_amendments_or_earlier_dropped": int(n_amendments_dropped),
        "n_gvkey_with_more_than_2_filings": int(n_gvkey_multi),
        "unmapped_filings_sample": unmapped_diag,
        "filing_type_counts": df["filing_type"].value_counts().to_dict(),
        "total_bytes_scanned": int(file_size_total),
        "parse_runtime_seconds": round(parse_secs, 2),
        "total_runtime_seconds": round(time.time() - t0, 2),
    }
    return df_dedup, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zip",
        type=Path,
        default=Path("inputs/10-X_C_2015_10Konly.zip"),
        help="Path to 10-K archive",
    )
    parser.add_argument(
        "--ccm",
        type=Path,
        default=Path("inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/intermediate/brexit_10k_keyword_counts"),
    )
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(message)s")

    if not args.zip.exists():
        logger.error(f"Zip not found: {args.zip}")
        return 1
    if not args.ccm.exists():
        logger.error(f"CCM not found: {args.ccm}")
        return 1

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = args.out / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    df, manifest = parse_zip(args.zip, args.ccm, progress_every=args.progress_every)

    parquet_path = out_dir / "keyword_counts_per_filing.parquet"
    df.to_parquet(parquet_path, index=False)

    manifest["output_parquet"] = str(parquet_path)
    manifest["timestamp"] = ts
    manifest_path = out_dir / "parse_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))

    print(f"\n[OK] parse_10k_keywords complete in {manifest['total_runtime_seconds']:.1f}s")
    print(f"     parquet: {parquet_path}")
    print(f"     manifest: {manifest_path}")
    print(f"     filings parsed: {manifest['n_filings_parsed']:,}")
    print(f"     CIK-to-gvkey coverage: {manifest['cik_to_gvkey_coverage']:.1%}")
    print(f"     dedup keep-latest: {manifest['n_filings_after_dedup']:,}")
    print(f"     filing types: {manifest['filing_type_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
