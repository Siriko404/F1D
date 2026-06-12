#!/usr/bin/env python3
"""Enforcement checker + block promotion for thesis_propositions.json.

MODES:
  python tmp/check_propositions.py --check <file> --block "front-matter"
      Check one block or all rows in a file. Read-only.

  python tmp/check_propositions.py --promote "front-matter"
      Check block in thesis_propositions_A.json. If PASS, copy clean rows
      into thesis_propositions_B.json and git-commit B. If FAIL, exit 1,
      never touch B.

Rule: I (Claude) ONLY hand-edit A. The checker owns B + git.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "Thesis" / "audit"
FA = AUDIT / "thesis_propositions_A.json"
FB = AUDIT / "thesis_propositions_B.json"
FO = AUDIT / "thesis_propositions.json"  # pristine seed, never touched

VENDORS = {"Capital IQ", "SDC", "Compustat", "CRSP", "IBES"}
CITE_KEYS = re.compile(r"\\(?:citep|citet)\{([^}]+)\}")
HAS_NUMBER = re.compile(r"\b\d+\.\d+\b|\bSE\s|R\^?2\b|\bn\.s\.\b|\d{2,3},\d{3}|significant at|\d+\\?%\s*level|p<[\d.]")
HAS_MATH = re.compile(r"\$[^$]+\$")
EQ_MENTION = re.compile(r"equation\s*[14]|equation-[14]")
ID_RE = re.compile(r"^[A-Z]{2,3}-\d{3}[a-z]?$")
NULL_FLDS = {"proposition", "category", "check_route", "role", "id"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def fail(msg):
    print("FAIL:", msg)
    return False


def check_rows(rows, label=""):
    """Run all post-conditions on a list of rows. Returns (ok, seeds_dict)."""
    ok = True
    seeds = {}
    for r in rows:
        s = r["seq"]
        seeds.setdefault(s, []).append(r)

    if label:
        print("CHECKER: %s (%d rows, %d seeds)" % (label, len(rows), len(seeds)))

    # 1. seq coverage
    all_seqs = sorted(seeds.keys())
    gap = set(range(min(all_seqs), max(all_seqs) + 1)) - set(all_seqs)
    if gap:
        ok &= fail("COVERAGE GAP: seeds missing rows: %s" % sorted(gap))

    # 2. #A-rows >= total cite-keys
    n_a = sum(1 for r in rows if r["category"] == "A")
    n_keys = sum(len(CITE_KEYS.findall(r.get("verbatim_span", ""))) for r in rows)
    if n_a < n_keys:
        ok &= fail("CITE UNDERCOUNT: %d A-rows < %d cite-keys" % (n_a, n_keys))

    # 3. vendor mentions -> B row
    for r in rows:
        span = r.get("verbatim_span", "")
        for v in VENDORS:
            if v in span:
                b_rows = [x for x in seeds.get(r["seq"], [])
                          if x["category"] == "B" and v in x.get("proposition", "")]
                if not b_rows:
                    ok &= fail("VENDOR NOT COVERED: seq %d mentions '%s' but no B row" % (r["seq"], v))

    # 4. number seeds -> exactly 1 E row
    for r in rows:
        span = r.get("verbatim_span", "")
        if HAS_NUMBER.search(span):
            e_rows = [x for x in seeds.get(r["seq"], []) if x["category"] == "E"]
            if len(e_rows) != 1:
                ok &= fail("E-FAIL seq %d: expected 1 E row, got %d" % (r["seq"], len(e_rows)))

    # 5. math/equation/vartable -> >=1 D row
    for r in rows:
        span = r.get("verbatim_span", "")
        has_d = any(x["category"] == "D" for x in seeds.get(r["seq"], []))
        if HAS_MATH.search(span) or EQ_MENTION.search(span):
            if not has_d:
                ok &= fail("D MISSING: seq %d has math/equation but no D row" % r["seq"])
        if r.get("block") == "appendix-vartable" and r.get("note") == "table-row" and "&" in span:
            if not has_d:
                ok &= fail("D MISSING: seq %d is a vartable &-row but no D row" % r["seq"])

    # 6. bibliography -> 13 I rows, distinct bibkeys
    bib_rows = [r for r in rows if r.get("block") == "bibliography"]
    bibkeys = set(r.get("mapped_bibkey") for r in bib_rows if r.get("mapped_bibkey"))
    if bib_rows:
        if len(bib_rows) != 13:
            ok &= fail("BIB COUNT: %d I-rows, expected 13" % len(bib_rows))
        if len(bibkeys) != 13:
            ok &= fail("BIB KEYS: %d distinct, expected 13 non-null" % len(bibkeys))

    # 7. verbatim clause is substring
    for r in rows:
        prop = r.get("proposition") or ""
        span = r.get("verbatim_span") or ""
        if prop and r.get("category") != "K":
            # extract the quoted clause after the stem ": "
            if ": \"" in prop and prop.endswith("\""):
                clause = prop.split(": \"", 1)[1][:-1]
                if clause and clause not in span:
                    ok &= fail("PARAPHRASE seq %d: clause not in span — '%s'" % (r["seq"], clause[:60]))

    # 8. non-null required fields
    for r in rows:
        for f in NULL_FLDS:
            if r.get(f) is None:
                ok &= fail("NULL %s in seq %d (id=%s)" % (f, r["seq"], r.get("id", "?")))
                break
        if r.get("id") and not ID_RE.match(r["id"]):
            ok &= fail("BAD ID: '%s' (expected PREFIX-NNNx)" % r["id"])

    # 9. K rows: empty proposition, route=none
    for r in rows:
        if r.get("category") == "K":
            if r.get("proposition") != "":
                ok &= fail("K-FAIL seq %d: proposition must be empty, got '%s'" % (r["seq"], r.get("proposition")))
            if r.get("check_route") != "none":
                ok &= fail("K-FAIL seq %d: route must be 'none', got '%s'" % (r["seq"], r.get("check_route")))

    if ok:
        print("  PASS")
    return ok, seeds


def promote_block(block_name):
    """Check block in A. If PASS, replace that block's rows in B and commit B."""
    # load A
    data_a = load(FA)
    rows_a = [r for r in data_a["claims"] if r["block"] == block_name]

    # verify it's not still seed-only
    if all(r.get("proposition") is None for r in rows_a):
        print("PROMOTE ABORT: block '%s' still seed-only (proposition=null) in A" % block_name)
        return 1

    # check
    ok, _ = check_rows(rows_a, "PROMOTE %s" % block_name)
    if not ok:
        print("PROMOTE ABORT: block '%s' FAILED checker — NOT touching B" % block_name)
        return 1

    # load B
    data_b = load(FB)
    rows_b = data_b["claims"]

    # find the seq range for this block in B
    block_seqs = sorted(r["seq"] for r in rows_a)
    lo, hi = block_seqs[0], block_seqs[-1]

    # split B: keep everything OUTSIDE the block range, replace with A's clean block
    before = [r for r in rows_b if r["seq"] < lo]
    inside_clean = rows_a  # from A, verified clean
    after = [r for r in rows_b if r["seq"] > hi]

    # renumber seqs in "after" if block length changed (multi-row seeds)
    old_count = sum(1 for r in rows_b if lo <= r["seq"] <= hi)
    new_count = len(inside_clean)
    delta = new_count - old_count
    if delta != 0:
        for r in after:
            r["seq"] += delta

    data_b["claims"] = before + inside_clean + after
    save(FB, data_b)

    # verify B still parses
    try:
        json.loads(json.dumps(data_b))
    except Exception as e:
        print("PROMOTE FATAL: B corrupted after write: %s" % e)
        return 1

    # git commit B
    try:
        subprocess.run(["git", "add", str(FB)], cwd=str(ROOT), check=True)
        msg = "audit(propositions): identify block '%s' — %d rows, CHECKER PASS" % (block_name, new_count)
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=str(ROOT), check=True)
    except subprocess.CalledProcessError as e:
        print("PROMOTE FATAL: git failed: %s" % e)
        return 1

    print("PROMOTE OK: block '%s' (%d rows) -> B, committed" % (block_name, new_count))

    # count remaining blocks in B still seed-only
    remaining = set(
        r["block"] for r in data_b["claims"] if r.get("proposition") is None
    )
    if remaining:
        print("  remaining seed-only blocks: %s" % ", ".join(sorted(remaining)[:5]))
        if len(remaining) > 5:
            print("  ... +%d more" % (len(remaining) - 5))

    return 0


def check_file(path, block_name=None):
    """Check a file, optionally filtered to one block."""
    data = load(path)
    rows = data["claims"]
    if block_name:
        rows = [r for r in rows if r["block"] == block_name]
    label = "%s/%s" % (Path(path).stem, block_name or "ALL")
    ok, _ = check_rows(rows, label)
    return 0 if ok else 1


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: check_propositions.py --check A|B [--block X] | --promote BLOCK")
        print("  --promote: check block in A -> if PASS, replace in B + git-commit B")
        return 1

    if args[0] == "--promote":
        return promote_block(args[1])

    if args[0] == "--check":
        fname = args[1]
        path = {"A": FA, "B": FB, "O": FO}.get(fname, Path(fname))
        blk = None
        if len(args) >= 4 and args[2] == "--block":
            blk = args[3]
        return check_file(path, blk)

    print("Unknown mode:", args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
