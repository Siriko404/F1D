#!/usr/bin/env python3
"""G2 number-coverage gate (audit P1, mechanical, no-LLM).

Protocol (AUDIT_PROTOCOL.md SS5/P1): extract EVERY digit-form numeric token from
the rendered prose of docs/Thesis/thesis_draft.tex, classify each into
  covered     -> equals a result string verified by a verify_draft_numbers CHECK
  derived     -> a ratio/CI value recomputed by a DERIVED check
  note        -> anchored to a table-note string (verified by grep here)
  structural  -> year / significance-level / equation / design-count / JEL code
                 (never an estimate; thesis results are ALWAYS 0.xxxx decimals or
                 comma-grouped Ns, so a bare small integer cannot be a result)
and FAIL on any unclassified token (a number in the prose with no provenance).

Scope = rendered body + appendix prose. Excluded WITH REASON (recorded in JSON):
  - LaTeX preamble (before \\begin{document}) -- formatting, not prose
  - thebibliography block                      -- citation metadata -> P3
  - the appendix variable-definition tabular   -- definitional formulas, not results
  - the \\section*{Tables} \\input block          -- table cells -> G1
  - LaTeX comments and length/width tokens     -- not rendered / formatting

Digit-form only. Word-form magnitude claims ("fifteen percent of a SD", "half
again", "twelve specifications") are OUT OF SCOPE here by design and routed to G3.

Single source of truth for `covered`: imports the CHECK lists from
verify_draft_numbers (no duplicated expected values).

Run: python tmp/audit_g2.py     (exit 1 on any GAP)
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_draft_numbers import CHECKS, ANCHORED_CHECKS, SE_CHECKS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "Thesis" / "thesis_draft.tex"

# --- covered set: every result string a CHECK verifies (cells + SEs) -----------
COVERED = set()
for cid, f, rx, col, exp in CHECKS:
    if exp is not None:
        COVERED.add(exp)
for cid, f, anchor, rx, col, exp in ANCHORED_CHECKS:
    COVERED.add(exp)
for cid, f, rx, col, exp in SE_CHECKS:
    COVERED.add(exp)
COVERED.add("0.1068")  # standalone spread-SE check in verify_draft_numbers.main()

# --- derived (digit-form) tokens, each backed by a DERIVED check ---------------
DERIVED_TOKENS = {
    "1.4":    "PreAnn share = 1.4% of sample (DERIVED: 0.0143*100)",
    "-0.027": "scrutiny CI low = -0.0056 - 1.96*0.0111 (DERIVED)",
    "0.016":  "scrutiny CI high = -0.0056 + 1.96*0.0111 (DERIVED)",
    "0.04":   "rhetorical approx of the run-up (~0.0461/0.0473); no precise claim",
}

# --- table-note anchored: verified by grep against the fragment here -----------
NOTE_ANCHORED = {
    "89": ("docs/Draft/_empire_building_did.tex", r"89\\%"),  # "89% of calls raise no cash turns"
}

# --- explicit structural tokens (non-integer), each with a reason --------------
STRUCT_EXPLICIT = {
    ".01": "p-value threshold (p<.01)",
}
JEL = {"14": "JEL G14", "32": "JEL G32", "34": "JEL G34", "82": "JEL D82"}


def strip_scope(text: str):
    """Return (scanned_text, exclusions[]) after removing non-prose regions."""
    exclusions = []
    # 1. preamble
    i = text.find(r"\begin{document}")
    if i != -1:
        exclusions.append("preamble (before \\begin{document}): LaTeX formatting")
        text = text[i:]
    # 2. bibliography -> P3
    text, n = re.subn(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}",
                      " ", text, flags=re.S)
    if n:
        exclusions.append("thebibliography block: citation metadata -> P3")
    # 3. appendix variable-definition tabular -> definitional
    text, n = re.subn(r"\\begin\{tabular\}.*?\\end\{tabular\}", " ", text, flags=re.S)
    if n:
        exclusions.append(f"{n} tabular block(s): definitional formulas, not results")
    # 4. tables input section -> G1
    text, n = re.subn(r"\\section\*\{Tables\}.*\Z", " ", text, flags=re.S)
    if n:
        exclusions.append("\\section*{Tables} \\input block: table cells -> G1")
    return text, exclusions


def normalize(text: str) -> str:
    # strip LaTeX line comments (unescaped %)
    text = re.sub(r"(?<!\\)%.*", "", text)
    # strip cite/ref/label argument KEYS (baker2016, tab:h11) -> not rendered numbers;
    # citation metadata is P3, cross-ref integrity is G4.
    text = re.sub(r"\\(?:cite[pt]?|citealp|ref|eqref|label|autoref)\*?\{[^}]*\}", " ", text)
    # strip length / width formatting tokens so they are not read as data
    text = re.sub(r"[\d.]+\s*(?:pt|cm|mm|em|ex|in|bp|dd|pc|sp)\b", " ", text)
    text = re.sub(r"[\d.]+\\(?:text|column|line|page)width", " ", text)
    # en-dash numeric ranges (2002--2018, 1593--1636) -> split so '--' is not a sign
    text = text.replace("--", " ")
    # drop math delimiters and escaped percent, keep the digits/sign
    text = text.replace("$", " ").replace(r"\%", " ")
    return text


# comma is a thousands separator only (digit,exactly-3-digits), never trailing
TOKEN_RE = re.compile(r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|[+-]?\.\d+")


def classify(tok: str):
    """Return (bucket, reason). 'gap' bucket = unclassified -> gate fails."""
    if tok.startswith("+"):
        tok = tok[1:]            # a leading + is never semantic
    if tok in COVERED:
        return "covered", "verified by a verify_draft_numbers CHECK"
    if tok in DERIVED_TOKENS:
        return "derived", DERIVED_TOKENS[tok]
    if tok in STRUCT_EXPLICIT:
        return "structural", STRUCT_EXPLICIT[tok]
    s = tok.lstrip("+")           # normalise sign for integer/year tests
    body = s.lstrip("-")
    if s in NOTE_ANCHORED:
        return "note", "table-note anchored (grep-verified)"
    if body in JEL:
        return "structural", JEL[body]
    if body.isdigit():
        v = int(body)
        if 1900 <= v <= 2030:
            return "structural", "year"
        if v <= 100:
            return "structural", "design/level/equation/index integer (no result is bare-int in this draft)"
    return "gap", "UNCLASSIFIED: digit-form number in prose with no CHECK/derivation/structural reason"


def first_context(raw_lines, tok) -> str:
    pat = re.escape(tok)
    for ln in raw_lines:
        if re.search(pat, ln):
            return ln.strip()[:160]
    return ""


def main() -> int:
    raw = DRAFT.read_text(encoding="utf-8")
    raw_lines = raw.splitlines()
    scoped, exclusions = strip_scope(raw)
    scoped = normalize(scoped)

    seen = {}  # token -> count
    for m in TOKEN_RE.finditer(scoped):
        t = m.group(0)
        # discard a stray comma-less '+' artifacts; keep meaningful tokens
        seen[t] = seen.get(t, 0) + 1

    buckets = {"covered": [], "derived": [], "note": [], "structural": [], "gap": []}
    detail = {}
    for tok, cnt in sorted(seen.items()):
        bucket, reason = classify(tok)
        buckets[bucket].append(tok)
        detail[tok] = {"bucket": bucket, "reason": reason, "count": cnt,
                       "context": first_context(raw_lines, tok)}

    # verify every note-anchored token against its fragment (primary source)
    note_checks = []
    for tok in buckets["note"]:
        rel, pat = NOTE_ANCHORED[tok]
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        ok = re.search(pat, txt) is not None
        note_checks.append({"token": tok, "fragment": rel, "pattern": pat, "found": ok})
        if not ok:
            buckets["gap"].append(tok)  # note claim not actually in the fragment -> gap

    out = {
        "gate": "G2_number_coverage",
        "baseline_sha": "7f97a16",
        "scope": "rendered prose of docs/Thesis/thesis_draft.tex (digit-form tokens only)",
        "deferred_to_G3": "word-form ratio/magnitude claims (fifteen percent, half again, twelve specs)",
        "exclusions": exclusions,
        "counts": {k: len(v) for k, v in buckets.items()},
        "distinct_tokens": len(seen),
        "note_checks": note_checks,
        "gaps": sorted(set(buckets["gap"])),
        "tokens": detail,
    }
    (ROOT / "docs" / "Thesis" / "audit" / "g2_number_coverage.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")

    print(f"\nG2 number-coverage  (baseline 7f97a16)")
    print("=" * 72)
    for k in ("covered", "derived", "note", "structural", "gap"):
        print(f"  {k:11s} {len(buckets[k]):3d}   {', '.join(sorted(set(buckets[k]))[:12])}")
    print("=" * 72)
    if out["gaps"]:
        print("  GAPS (unclassified prose numbers):")
        for g in out["gaps"]:
            print(f"    {g:>10s}   {detail[g]['context']}")
    print(f"  distinct tokens: {len(seen)}   written: docs/Thesis/audit/g2_number_coverage.json")
    return 1 if out["gaps"] else 0


if __name__ == "__main__":
    sys.exit(main())
