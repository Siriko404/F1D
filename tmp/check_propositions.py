#!/usr/bin/env python3
"""Enforcement checker for thesis_propositions.json — runs after each block.

Verifies coverage + format post-conditions from PROPOSITION_RULES.md §7.
FAIL = a hard guard against silent drops / template violations / missing rows.
Run:  python tmp/check_propositions.py [--all | --block "Introduction"]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "docs" / "Thesis" / "audit" / "thesis_propositions.json"

VENDORS = {"Capital IQ", "SDC", "Compustat", "CRSP", "IBES"}
CITE_KEYS = re.compile(r"\\(?:citep|citet)\{([^}]+)\}")
HAS_NUMBER = re.compile(r"\d+\.\d+|\\bSE\\b|\\bR\^?2\\b|\\bn\.s\.\\b|\d{2,3},\d{3}|significant at|\\d+\\\\?%\s*level|p<")
HAS_MATH = re.compile(r"\$[^$]+\$")
EQ_MENTION = re.compile(r"equation\s*[14]|equation-[14]")
ID_RE = re.compile(r"^[A-Z]{2,3}-\d{3}[a-z]?$")
NULL_FLDS = {"proposition", "category", "check_route", "role", "id"}


def load():
    return json.loads(PROPS.read_text(encoding="utf-8"))


def fail(msg):
    print("FAIL:", msg)
    return False


def check_all(rows):
    ok = True
    seeds = {}
    for r in rows:
        s = r["seq"]
        seeds.setdefault(s, []).append(r)

    # 1. every seq (from the live file) present in >=1 row
    all_seqs = sorted(seeds.keys())
    gap = set(range(1, max(all_seqs) + 1)) - set(all_seqs)
    if gap:
        ok &= fail("COVERAGE GAP: seeds missing rows: %s" % sorted(gap))

    # 2. #A-rows >= total \citep/\citet keys
    n_a = sum(1 for r in rows if r["category"] == "A")
    n_keys = sum(len(CITE_KEYS.findall(r["verbatim_span"])) for r in rows)
    if n_a < n_keys:
        ok &= fail("CITE UNDERCOUNT: %d A-rows < %d cite-keys" % (n_a, n_keys))

    # 3. every vendor mention -> >=1 B row at that seed
    for r in rows:
        span = r["verbatim_span"]
        for v in VENDORS:
            if v in span:
                b_rows = [x for x in seeds.get(r["seq"], [])
                          if x["category"] == "B" and v in x.get("proposition", "")]
                if not b_rows:
                    ok &= fail("VENDOR NOT COVERED: seq %d mentions '%s' but no B row" % (r["seq"], v))

    # 4. every seed firing T5 -> exactly one E row
    for r in rows:
        if HAS_NUMBER.search(r["verbatim_span"]):
            e_rows = [x for x in seeds.get(r["seq"], []) if x["category"] == "E"]
            if len(e_rows) != 1:
                ok &= fail("E-FAIL seq %d: expected 1 E row, got %d" % (r["seq"], len(e_rows)))

    # 5. every $...$ / equation mention / vartable &-row -> >=1 D row
    for r in rows:
        span = r["verbatim_span"]
        has_d = any(x["category"] == "D" for x in seeds.get(r["seq"], []))
        if HAS_MATH.search(span) or EQ_MENTION.search(span):
            if not has_d:
                ok &= fail("D MISSING: seq %d has math/equation but no D row" % r["seq"])
        if r.get("block") == "appendix-vartable" and r.get("note") == "table-row" and "&" in span:
            if not has_d:
                ok &= fail("D MISSING: seq %d is a vartable row but no D row" % r["seq"])

    # 6. bibliography -> 13 I rows, distinct bibkeys
    bib_rows = [r for r in rows if r.get("block") == "bibliography"]
    bibkeys = set(r.get("mapped_bibkey") for r in bib_rows)
    if len(bib_rows) != 13:
        ok &= fail("BIB COUNT: %d I-rows, expected 13" % len(bib_rows))
    if len(bibkeys) != 13 or None in bibkeys:
        ok &= fail("BIB KEYS: %d distinct, expected 13 non-null" % len(bibkeys - {None}))

    # 7. every verbatim clause is substring of its seed's verbatim_span
    for r in rows:
        prop = r.get("proposition") or ""
        span = r.get("verbatim_span") or ""
        if prop and r["category"] != "K":
            clause = prop.split(": ", 1)[-1].strip('"')
            if clause and clause not in span:
                ok &= fail("PARAPHRASE seq %d: '%s' not in '%s'" % (r["seq"], clause[:40], span[:40]))

    # 8. every row has non-null id, category, check_route, role
    for r in rows:
        for f in NULL_FLDS:
            if r.get(f) is None:
                ok &= fail("NULL %s in seq %d (id=%s)" % (f, r["seq"], r.get("id", "?")))
                break
        if r.get("id") and not ID_RE.match(r["id"]):
            ok &= fail("BAD ID: '%s' (expected BLOCKPREF-###x)" % r["id"])

    # 9. K rows: proposition == "" and check_route == "none"
    for r in rows:
        if r.get("category") == "K":
            if r.get("proposition") != "":
                ok &= fail("K-FAIL seq %d: proposition must be empty, got '%s'" % (r["seq"], r["proposition"]))
            if r.get("check_route") != "none":
                ok &= fail("K-FAIL seq %d: route must be 'none', got '%s'" % (r["seq"], r["check_route"]))

    if ok:
        print("CHECKER: PASS (%d rows, %d seeds covered)" % (len(rows), len(seeds)))
    return ok


def main():
    j = load()
    rows = j["claims"]
    if not rows:
        print("CHECKER: no rows yet — FILE IS STILL SEED-ONLY (proposition=null). Nothing to check.")
        return 0
    # Detect: are we still just seeds? (all proposition=null -> seed phase, not proposition phase)
    if all(r.get("proposition") is None for r in rows):
        print("CHECKER: seed phase — no propositions yet. Run after applying the rulebook.")
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "--block":
        blk = sys.argv[2]
        rows = [r for r in rows if r.get("block") == blk]
        print("CHECKER: block='%s' (%d rows)" % (blk, len(rows)))
    ok = check_all(rows)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
