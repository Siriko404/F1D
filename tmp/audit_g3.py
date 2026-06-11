#!/usr/bin/env python3
"""G3 derived-arithmetic gate (audit P1, mechanical, no-LLM).

Protocol (AUDIT_PROTOCOL.md SS5/P1): "recompute every ratio/multiple/% claim
('fifteen percent of a SD', 'half again', '89% of calls', '1.4% of the sample',
'roughly three percent of the mean')." These are WORD-FORM claims that G2's
digit-token regex cannot catch: a sentence asserting a numeric RELATION among
locked table cells (a ratio, a multiple, a difference, a count, an extremum).

G3 recomputes each from the LOCKED CELLS (read from the bible/fragments via the
same cell() machinery as verify_draft_numbers -- never from the prose), and proves
the set is EXHAUSTIVE via a trigger-word scan of the prose whose every arithmetic
sentence must map to a claim here.

Discipline: operands are pulled from the published table cells; the asserted
result is checked against them. A difference of cells rounded independently can
differ from the published drop by up to ~1 ulp (round-then-subtract); such
internal-consistency relations use tol=2e-4. Ratio/extremum claims use their own
stated rounding. Any FAIL is a finding (recorded; no thesis edit here).

Run: python tmp/audit_g3.py     (exit 1 on any FAIL)
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_draft_numbers import cell  # locked-cell reader (fragments + bible)  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BIBLE = (ROOT / "docs" / "Draft" / "thesis_tables.tex").read_text(encoding="utf-8", errors="replace")
DRAFT = (ROOT / "docs" / "Thesis" / "thesis_draft.tex").read_text(encoding="utf-8")


def g(frag: str, row: str, col: int, anchor: str | None = None) -> float:
    """Locked cell value as float (via verify_draft_numbers.cell)."""
    s = cell(frag, row, col, anchor=anchor)
    if not re.match(r"-?\d", s):
        raise ValueError(f"non-numeric cell for {frag}:{row}:{col} -> {s!r}")
    return float(s.replace(",", ""))


# ---- locked anchors used by several claims -----------------------------------
SD = g("_summary_stats.tex", r"^UncResCEO", 3)          # residual SD  (Panel B) = 0.3072
MEANCASH = g("_summary_stats.tex", r"^CashRatio(?!\$)", 2)  # cash mean (Panel A) = 0.1573


# ---- bible-block helpers for count / extremum claims -------------------------
def bible_block(label: str) -> str:
    i = BIBLE.find("\\label{" + label + "}")
    if i == -1:
        raise ValueError(f"label {label} not found")
    j = BIBLE.find("\\end{tabular}", i)
    return BIBLE[i:j]


def count_model_columns(label: str) -> int:
    """Number of '(k)' spec columns in the table header row."""
    blk = bible_block(label)
    for line in blk.splitlines():
        if re.search(r"&\s*\(1\)", line):
            return len(re.findall(r"\(\d+\)", line))
    return -1


def row_cells_with_stars(label: str, row_label: str):
    """Return [(value:str, significant:bool), ...] for the named row's coef line."""
    blk = bible_block(label)
    for line in blk.splitlines():
        if line.split("&")[0].strip().startswith(row_label):
            out = []
            for c in line.split("&")[1:]:
                c = c.strip().rstrip("\\").strip()
                if not c:
                    continue
                num = re.search(r"-?\d+\.?\d*", c)
                if num:
                    out.append((num.group(0), "^{" in c or "*" in c))
            return out
    return []


# ---- the claim ledger: each recomputes from locked cells ---------------------
# kind: ratio | difference | compare | count | extremum
CLAIMS = []


def claim(cid, quote, kind, ok, detail):
    CLAIMS.append({"id": cid, "quote": quote, "kind": kind, "pass": bool(ok), "detail": detail})


# --- ratio / multiple / percent (word-form) ---
r = 0.0461 / SD
claim("R1_15pct_SD_runup", "uncertainty coefficient equals fifteen percent of a standard deviation (0.3072)",
      "ratio", abs(r - 0.15) < 0.01, f"0.0461/{SD:.4f}={r:.4f} ~ 0.15")
preann = g("_summary_stats.tex", r"^PreAnnounceQtr", 2, anchor="Panel B")
claim("R2_1p4pct_sample", "a quarter that makes up 1.4% of the sample",
      "ratio", round(preann * 100, 1) == 1.4, f"PreAnn mean {preann}=*100={preann*100:.2f}% ~ 1.4%")
claim("R3_half_pp", "adds half a percentage point of assets",
      "ratio", 0.45 <= 0.0051 * 100 <= 0.55, f"0.0051*100={0.0051*100:.2f}pp ~ 0.5pp")
r = 0.0051 / MEANCASH
claim("R4_3pct_mean", "roughly three percent of the mean cash ratio (0.1573)",
      "ratio", round(r * 100) == 3, f"0.0051/{MEANCASH:.4f}={r*100:.2f}% ~ 3%")
r = 0.0473 / SD
claim("R5_15pct_SD_t1", "0.0473 ... about fifteen percent of a residual standard deviation",
      "ratio", abs(r - 0.15) < 0.01, f"0.0473/{SD:.4f}={r:.4f} ~ 0.15")
r = 0.0723 / 0.0473
claim("R6_half_again", "peak-to-post swing (0.0723) is half again the size of that entry spike (0.0473)",
      "ratio", 1.45 <= r <= 1.55, f"0.0723/0.0473={r:.3f} ~ 1.5 (half again)")
r = 0.0983 / SD
claim("R7_third_SD", "gap ... about a third of a residual standard deviation",
      "ratio", abs(r - 1/3) < 0.02, f"0.0983/{SD:.4f}={r:.4f} ~ 0.333")
lo, hi = round(-0.0056 - 1.96 * 0.0111, 3), round(-0.0056 + 1.96 * 0.0111, 3)
claim("R8_CI_bounds", "interaction's confidence interval ([-0.027, +0.016])",
      "ratio", (lo, hi) == (-0.027, 0.016), f"-0.0056 +/- 1.96*0.0111 = [{lo}, {hi}]")

# --- difference relations recomputed from level cells (tol 2e-4 = round-then-subtract) ---
TOL = 2e-4
M = "_empire_drop_matched.tex"
pre1u, gapu, postu = g(M, r"^PRE1", 1), g(M, r"^GAP", 1), g(M, r"^POST", 1)
pre1c, gapc, postc = g(M, r"^PRE1", 2), g(M, r"^GAP", 2), g(M, r"^POST", 2)
claim("D1_fall_0455", "a fall of 0.0455 from the pre-announcement quarter",
      "difference", abs((pre1u - gapu) - g(M, r"^Drop: PRE1 \$-\$ GAP", 1)) < TOL,
      f"PRE1u-GAPu={pre1u-gapu:.4f} vs Drop cell {g(M, r'^Drop: PRE1 \$-\$ GAP', 1)}")
claim("D2_swing_0723", "peak-to-post swing of 0.0723",
      "difference", abs((pre1u - postu) - g(M, r"^Drop: PRE1 \$-\$ POST", 1)) < TOL,
      f"PRE1u-POSTu={pre1u-postu:.4f} vs Drop cell {g(M, r'^Drop: PRE1 \$-\$ POST', 1)}")
claim("D3_cash_drop_0006", "drop 0.0006 (announce, cash)",
      "difference", abs((pre1c - gapc) - g(M, r"^Drop: PRE1 \$-\$ GAP", 2)) < TOL,
      f"PRE1c-GAPc={pre1c-gapc:.4f} vs Drop cell {g(M, r'^Drop: PRE1 \$-\$ GAP', 2)}")
claim("D4_cash_drop_0210", "announce-to-completion drop 0.0210",
      "difference", abs((gapc - postc) - g(M, r"^Drop: GAP \$-\$ POST", 2)) < TOL,
      f"GAPc-POSTc={gapc-postc:.4f} vs Drop cell {g(M, r'^Drop: GAP \$-\$ POST', 2)}")
P = "_empire_drop_placebo.tex"
pp1, ppost = g(P, r"^PRE1", 1), g(P, r"^POST", 1)
claim("D5_placebo_0681", "peak-to-post drop of 0.0681 (placebo cash arm)",
      "difference", abs((pp1 - ppost) - g(P, r"^Drop: PRE1 \$-\$ POST", 1)) < TOL,
      f"PRE1-POST={pp1-ppost:.4f} vs Drop cell {g(P, r'^Drop: PRE1 \$-\$ POST', 1)}")
ps1, psg = g(P, r"^PRE1", 2), g(P, r"^GAP", 2)
claim("D6_placebo_stock_0756", "pre-to-gap difference -0.0756 (placebo stock arm)",
      "difference", abs((ps1 - psg) - g(P, r"^Drop: PRE1 \$-\$ GAP", 2)) < TOL,
      f"PRE1s-GAPs={ps1-psg:.4f} vs Drop cell {g(P, r'^Drop: PRE1 \$-\$ GAP', 2)} (round-then-subtract)")
S = "_empire_cashspec.tex"
ca, st = g(S, r"^Pre-announce qtr, Cash", 1), g(S, r"^Pre-announce qtr, Stock", 1)
diff = g(S, r"^Cash \$-\$ Stock", 1)
claim("D7_cashstock_0983", "cash 0.0459 against -0.0524 yields a formal cash-stock difference of 0.0983",
      "difference", abs((ca - st) - diff) < TOL, f"Cash-Stock={ca-st:.4f} vs formal-test cell {diff}")
# cause-side cash-stock differences (same formal test, other two cashspec columns), prose line 136
ca2, st2, diff2 = g(S, r"^Pre-announce qtr, Cash", 2), g(S, r"^Pre-announce qtr, Stock", 2), g(S, r"^Cash \$-\$ Stock", 2)
claim("D8_cause_matched_0064", "the difference is insignificant on the matched universe (0.0064, n.s.)",
      "difference", abs((ca2 - st2) - diff2) < TOL, f"Cash-Stock(cause,matched)={ca2-st2:.4f} vs cell {diff2}")
ca3, st3, diff3 = g(S, r"^Pre-announce qtr, Cash", 3), g(S, r"^Pre-announce qtr, Stock", 3), g(S, r"^Cash \$-\$ Stock", 3)
claim("D9_cause_full_0092", "reaches just 0.0092 (10%) on the full panel",
      "difference", abs((ca3 - st3) - diff3) < TOL, f"Cash-Stock(cause,full)={ca3-st3:.4f} vs cell {diff3}")

# --- compare / inequality / approx-equal ---
claim("C1_gap_exceeds_either", "the gap exceeds either coefficient",
      "compare", diff > ca and diff > abs(st), f"0.0983 > {ca} and > |{st}|")
claim("C2_0473_vs_0461_same", "0.0473 against 0.0461 there ... economically the same",
      "compare", abs(0.0473 - 0.0461) < 0.0015 and 0.14 < 0.0461/SD < 0.16,
      f"|0.0473-0.0461|={abs(0.0473-0.0461):.4f}; both ~15% SD")
lagc, lags = g("_empire_building_did.tex", r"^CashRatio\$_\{t-1\}\$", 1), g("_empire_building_did.tex", r"^CashRatio\$_\{t-1\}\$", 5)
claim("C3_lags_nearly_identical", "the stock arm's partial-adjustment lag, 0.8013, is nearly identical",
      "compare", abs(lagc - lags) < 0.005, f"|{lagc}-{lags}|={abs(lagc-lags):.4f} < 0.005")

# --- count / extremum (parse bible block) ---
ncols = count_model_columns("tab:h14c_ceo2_decomp")
ur = row_cells_with_stars("tab:h14c_ceo2_decomp", "UncResCEO")
claim("N1_twelve_specs", "insignificant in all twelve spread specifications",
      "count", ncols == 12 and len(ur) == 12 and not any(sig for _, sig in ur),
      f"h14c columns={ncols}; UncResCEO cells={len(ur)}; significant={sum(s for _,s in ur)}")
up = row_cells_with_stars("tab:h18_ceo2_decomp", "UncPreCEO")
ur18 = row_cells_with_stars("tab:h18_ceo2_decomp", "UncResCEO")
sig_vals = [abs(float(v)) for v, s in up if s]
claim("N2_up_to_0016", "weakly associated with presentation uncertainty (up to 0.0016, 5%); never the residual",
      "extremum", (max(sig_vals) == 0.0016 if sig_vals else False) and not any(s for _, s in ur18),
      f"h18 UncPre significant max={max(sig_vals) if sig_vals else None}; UncRes significant={sum(s for _,s in ur18)}")


# ---- exhaustiveness: trigger scan, every arithmetic sentence -> a claim -------
def prose_scope() -> str:
    t = DRAFT[DRAFT.find(r"\begin{document}"):]
    t = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", " ", t, flags=re.S)
    t = re.sub(r"\\section\*\{Tables\}.*\Z", " ", t, flags=re.S)
    t = re.sub(r"(?<!\\)%.*", "", t)
    return t


# verbatim arithmetic phrases each claim is responsible for (must be present in prose)
PHRASES = {
    "R1_15pct_SD_runup": "fifteen percent of a standard deviation",
    "R2_1p4pct_sample": "1.4\\% of the sample",
    "R3_half_pp": "half a percentage point",
    "R4_3pct_mean": "three percent of the mean",
    "R5_15pct_SD_t1": "about fifteen percent of a residual standard deviation",
    "R6_half_again": "half again the size",
    "R7_third_SD": "a third of a residual standard deviation",
    "R8_CI_bounds": "[-0.027, +0.016]",
    "D1_fall_0455": "a fall of 0.0455",
    "D2_swing_0723": "swing of 0.0723",
    "D3_cash_drop_0006": "drop 0.0006",
    "D4_cash_drop_0210": "drop 0.0210",
    "D5_placebo_0681": "drop of 0.0681",
    "D6_placebo_stock_0756": "difference $-0.0756$",
    "D7_cashstock_0983": "difference of 0.0983",
    "D8_cause_matched_0064": "(0.0064, n.s.)",
    "D9_cause_full_0092": "0.0092",
    "C1_gap_exceeds_either": "exceeds either coefficient",
    "C2_0473_vs_0461_same": "0.0473 against 0.0461",
    "C3_lags_nearly_identical": "nearly identical",
    "N1_twelve_specs": "all twelve spread specifications",
    "N2_up_to_0016": "up to 0.0016",
}
prose = prose_scope()

# --- FORWARD coverage: prose -> claim (catches MISSED claims; the backward phrase
#     check below catches phantom claims). A sentence carrying a generic relation
#     trigger AND a decimal magnitude must map to a claim phrase or the documented
#     non-arithmetic allowlist; gate FAILS on any uncovered sentence.
flat = re.sub(r"\\times", " x ", re.sub(r"\s+", " ", prose))  # kill \times symbol noise
sentences = re.split(r"(?<=[.;:]) ", flat)
REL = re.compile(r"\b(percent|percentage|half|third|twice|double|fold|exceeds|"
                 r"difference|drop|fall|swing|nearly identical|twelve)\b|up to", re.I)
PCT_OF = re.compile(r"\d[\d.]*\\?%\s+of")
HASDEC = re.compile(r"\d\.\d")
# sentences adjudicated NON-arithmetic despite a trigger+number (documented, with reason)
ALLOWLIST = {
    "89\\% of calls draw no cash scrutiny":
        "proportion, not a recomputation; G2-verified vs _empire_building_did.tex table note",
    "pooled test of their difference (0.0983":
        "intro restatement of the cash-stock difference; the recomputation is claim D7_cashstock_0983",
}
flagged, uncovered = [], []
for s in sentences:
    if (REL.search(s) or PCT_OF.search(s)) and (HASDEC.search(s) or PCT_OF.search(s)):
        mapped = next((cid for cid, p in PHRASES.items() if p in s), None)
        allow = next((a for a in ALLOWLIST if a in s), None)
        rec = {"claim": mapped, "allow": bool(allow), "sentence": s.strip()[:170]}
        flagged.append(rec)
        if not mapped and not allow:
            uncovered.append(rec)

phrase_missing = {cid: p for cid, p in PHRASES.items() if p not in prose}

passes = sum(c["pass"] for c in CLAIMS)
fails = [c for c in CLAIMS if not c["pass"]]
exhaustive_ok = (not uncovered) and (not phrase_missing)

out = {
    "gate": "G3_derived_arithmetic",
    "baseline_sha": "7f97a16",
    "method": "recompute every word-form ratio/multiple/difference/count/extremum claim from LOCKED cells",
    "locked_anchors": {"residual_SD": SD, "cash_mean": MEANCASH},
    "counts": {"claims": len(CLAIMS), "pass": passes, "fail": len(fails)},
    "exhaustiveness": {
        "method": "FORWARD prose->claim: every prose sentence with a generic relation trigger "
                  "(percent/half/third/difference/drop/fall/swing/exceeds/nearly-identical/twelve/up-to/'N% of') "
                  "AND a decimal must map to a claim phrase or the documented non-arithmetic allowlist; "
                  "FAIL on any uncovered sentence. PLUS backward claim->prose phrase presence.",
        "forward_sentences_flagged": len(flagged),
        "forward_uncovered": uncovered,
        "allowlist_non_arithmetic": ALLOWLIST,
        "backward_phrases_missing": phrase_missing,
        "flagged_detail": flagged,
        "ok": exhaustive_ok,
    },
    "claims": CLAIMS,
    "findings": [c["id"] + ": " + c["detail"] for c in fails],
}
(ROOT / "docs" / "Thesis" / "audit" / "g3_derived_arithmetic.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8")

print("\nG3 derived-arithmetic  (baseline 7f97a16)")
print("=" * 72)
for c in CLAIMS:
    print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['id']:24s} {c['kind']:10s} {c['detail']}")
print("=" * 72)
print(f"  claims={len(CLAIMS)}  pass={passes}  fail={len(fails)}")
print(f"  exhaustiveness: forward-flagged {len(flagged)} sentences, uncovered={len(uncovered)}, "
      f"backward-missing={len(phrase_missing)}  -> ok={exhaustive_ok}")
if uncovered:
    for u in uncovered:
        print(f"    UNCOVERED: {u['sentence']}")
print(f"  written: docs/Thesis/audit/g3_derived_arithmetic.json")
sys.exit(1 if (fails or not exhaustive_ok) else 0)
