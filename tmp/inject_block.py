#!/usr/bin/env python3
"""Safe injector: write proposition rows for ONE block into thesis_propositions_A.json.

Usage:
  python tmp/inject_block.py <block_name> <rows.json>

rows.json = { "block": "front-matter", "rows": [ {...}, ... ] }
Each row must include: seed_seq, id, proposition, category, role, check_route
Optional: mapped_bibkey, p2_ref, depends_on, note, verdict, evidence

Rules:
  - Every seed_seq in the block's current range MUST be covered.
  - Extra seed_seq values outside the block range = error.
  - seq renumbering is automatic (handles 1-seed -> N-rows expansion).
  - verbatim_span + file_line are carried forward from the original seed row.
  - NEVER delete rows from other blocks.
"""
import json
import sys
from pathlib import Path
from copy import deepcopy

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

    # load new rows
    payload = json.loads(rows_path.read_text(encoding="utf-8"))
    new_rows = payload["rows"]
    if payload.get("block") != block_name:
        fail("rows.json block='%s' != argv block='%s'" % (payload.get("block"), block_name))

    # validate new rows
    for i, r in enumerate(new_rows):
        missing = REQUIRED - set(r.keys())
        if missing:
            fail("row %d missing fields: %s" % (i, missing))
        if not r["id"] or not isinstance(r["id"], str):
            fail("row %d has missing/invalid id" % i)

    # load A
    data = json.loads(FA.read_text(encoding="utf-8"))
    claims = data["claims"]

    # find current rows for this block + their seed_seqs
    block_rows = [(j, r) for j, r in enumerate(claims) if r["block"] == block_name]
    if not block_rows:
        fail("block '%s' not found in A" % block_name)

    old_seqs = {r["seq"] for _, r in block_rows}
    lo, hi = block_rows[0][1]["seq"], block_rows[-1][1]["seq"]

    # verify new rows cover every old seed_seq
    new_seeds = {r["seed_seq"] for r in new_rows}
    missing_seeds = old_seqs - new_seeds
    extra_seeds = new_seeds - old_seqs
    if missing_seeds:
        fail("missing seed_seqs: %s" % sorted(missing_seeds))
    if extra_seeds:
        fail("extra seed_seqs not in block: %s" % sorted(extra_seeds))

    # build seed -> original row lookup (for verbatim_span, file_line)
    seed_map = {r["seq"]: r for _, r in block_rows}

    # build replacement rows, carrying forward verbatim_span + file_line
    replacement = []
    new_seq = lo
    for nr in new_rows:
        orig = seed_map[nr["seed_seq"]]
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
        # keep verbatim_span + file_line + block from original
        replacement.append(row)
        new_seq += 1

    # splice: before + replacement + after (with renumbered seqs)
    first_idx = block_rows[0][0]
    last_idx = block_rows[-1][0]
    delta = len(replacement) - len(block_rows)

    before = claims[:first_idx]
    after = claims[last_idx + 1:]
    for r in after:
        r["seq"] += delta

    data["claims"] = before + replacement + after

    # verify no seq gaps or dups
    all_seqs = [r["seq"] for r in data["claims"]]
    if len(all_seqs) != len(set(all_seqs)):
        fail("DUPLICATE seqs after injection — corruption prevented")
    if all_seqs != list(range(min(all_seqs), max(all_seqs) + 1)):
        fail("SEQ GAP after injection — corruption prevented")

    # verify B still has all other blocks untouched (compare lengths)
    expected_total = len(claims) + delta
    if len(data["claims"]) != expected_total:
        fail("TOTAL ROW COUNT mismatch: expected %d, got %d" % (expected_total, len(data["claims"])))

    # write
    FA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("INJECT OK: block '%s' — %d seeds -> %d rows (delta=%+d, total=%d)" % (
        block_name, len(old_seqs), len(replacement), delta, len(data["claims"])))


if __name__ == "__main__":
    main()
