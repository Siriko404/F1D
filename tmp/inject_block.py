#!/usr/bin/env python3
"""Safe injector: write proposition rows for ONE block into thesis_propositions_A.json.

Usage:
  python tmp/inject_block.py <block_name> <rows.json>

rows.json = { "block": "front-matter", "rows": [ {...}, ... ] }
Each row must include: seed_seq, id, proposition, category, role, check_route

Positional matching: 1st seed_seq group -> 1st seed in A's block, 2nd -> 2nd, etc.
No dependency on absolute seq numbers (which shift as prior blocks expand).
"""
import json
import sys
from pathlib import Path
from copy import deepcopy
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
FA = ROOT / "docs" / "Thesis" / "audit" / "thesis_propositions_A.json"

REQUIRED = {"seed_seq", "id", "proposition", "category", "role", "check_route"}


def fail(msg):
    print("INJECT ABORT:", msg)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("Usage: python tmp/inject_block.py <block_name> <rows.json>")
        sys.exit(1)

    block_name = sys.argv[1]
    rows_path = Path(sys.argv[2])

    payload = json.loads(rows_path.read_text(encoding="utf-8"))
    new_rows = payload["rows"]
    if payload.get("block") != block_name:
        fail("rows.json block='%s' != argv block='%s'" % (payload.get("block"), block_name))

    for i, r in enumerate(new_rows):
        missing = REQUIRED - set(r.keys())
        if missing:
            fail("row %d missing fields: %s" % (i, missing))
        if not r["id"] or not isinstance(r["id"], str):
            fail("row %d has missing/invalid id" % i)

    data = json.loads(FA.read_text(encoding="utf-8"))
    claims = data["claims"]

    # find current rows for this block
    block_rows = [(j, r) for j, r in enumerate(claims) if r["block"] == block_name]
    if not block_rows:
        fail("block '%s' not found in A" % block_name)

    # ordered unique seeds from A's block
    a_seeds = sorted(set(r["seq"] for _, r in block_rows))
    lo, hi = a_seeds[0], a_seeds[-1]

    # group new rows by seed_seq, preserving order
    seed_order = list(OrderedDict.fromkeys(r["seed_seq"] for r in new_rows))
    new_groups = {s: [r for r in new_rows if r["seed_seq"] == s] for s in seed_order}

    if len(seed_order) != len(a_seeds):
        fail("count mismatch: %d seed-groups in JSON vs %d seeds in A block" %
             (len(seed_order), len(a_seeds)))

    # seed_map: old A seq -> original row (for verbatim_span, file_line)
    seed_map = {r["seq"]: r for _, r in block_rows}

    replacement = []
    new_seq = lo
    for gi, group_key in enumerate(seed_order):
        orig_seq = a_seeds[gi]
        orig = seed_map[orig_seq]
        for nr in new_groups[group_key]:
            row = deepcopy(orig)
            row["seq"] = new_seq
            row["id"] = nr["id"]
            row["proposition"] = nr["proposition"]
            row["category"] = nr["category"]
            row["role"] = nr["role"]
            row["check_route"] = nr["check_route"]
            row["mapped_bibkey"] = nr.get("mapped_bibkey", orig.get("mapped_bibkey"))
            row["p2_ref"] = nr.get("p2_ref", orig.get("p2_ref"))
            row["depends_on"] = nr.get("depends_on", [])
            row["verdict"] = nr.get("verdict", orig.get("verdict"))
            row["evidence"] = nr.get("evidence", orig.get("evidence"))
            row["note"] = nr.get("note", orig.get("note"))
            replacement.append(row)
            new_seq += 1

    # splice
    first_idx = block_rows[0][0]
    last_idx = block_rows[-1][0]
    delta = len(replacement) - len(block_rows)

    before = claims[:first_idx]
    after = claims[last_idx + 1:]
    for r in after:
        r["seq"] += delta

    data["claims"] = before + replacement + after

    # integrity checks
    all_seqs = [r["seq"] for r in data["claims"]]
    if len(all_seqs) != len(set(all_seqs)):
        fail("DUPLICATE seqs — corruption prevented")
    if all_seqs != list(range(min(all_seqs), max(all_seqs) + 1)):
        fail("SEQ GAP — corruption prevented")

    expected_total = len(claims) + delta
    if len(data["claims"]) != expected_total:
        fail("TOTAL ROW COUNT mismatch: expected %d, got %d" %
             (expected_total, len(data["claims"])))

    FA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("INJECT OK: block '%s' — %d seeds -> %d rows (delta=%+d, total=%d)" %
          (block_name, len(seed_order), len(replacement), delta, len(data["claims"])))


if __name__ == "__main__":
    main()
