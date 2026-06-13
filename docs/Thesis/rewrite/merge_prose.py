#!/usr/bin/env python3
"""Programmatic prose transfer: tmp/prose_drafts.json -> section2.1_paragraph_ledger.json.

The paragraph prose is moved by CODE, never re-typed into the ledger by hand, so a
rewrite cannot drift a single word. SURGICAL: only the target paragraph's slice is
touched (final_prose + prose_status + prose_gate booleans); the rest of the ledger
stays byte-identical. Three guards make it safe:
  1. empty-slot guard -- refuses to write unless final_prose is currently "" (no clobber);
  2. uniqueness guard -- every text anchor must occur exactly once inside the slice;
  3. parse + structural diff-guard -- reparses the result and asserts the ONLY changed
     JSON paths are the four intended ones, and the stored prose == the draft byte-for-byte.

  python merge_prose.py P3            # validate + write ledger (empty-slot only)
  python merge_prose.py P3 --commit   # + git-commit the ledger
  python merge_prose.py P3 --dry      # validate only, write nothing
  python merge_prose.py P3 --update   # re-transfer over EXISTING prose (keeps diff-guard)
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "section2.1_paragraph_ledger.json"
DRAFTS = HERE.parents[2] / "tmp" / "prose_drafts.json"
ORDER = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]


def changed_paths(a, b, prefix=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            out += changed_paths(a.get(k), b.get(k), prefix + "." + k)
    elif a != b:
        out.append(prefix or "<root>")
    return out


def replace_once(text, old, new, required=True):
    n = text.count(old)
    if n == 0:
        if required:
            raise SystemExit("ABORT: anchor not found in slice: " + repr(old))
        return text
    if n > 1:
        raise SystemExit("ABORT: anchor not unique (%dx) in slice: %r" % (n, old))
    return text.replace(old, new)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ORDER:
        raise SystemExit("usage: merge_prose.py <%s> [--commit] [--dry]" % "|".join(ORDER))
    para = sys.argv[1]
    commit = "--commit" in sys.argv
    dry = "--dry" in sys.argv
    update = "--update" in sys.argv  # re-transfer over an already-filled final_prose

    raw = LEDGER.read_text(encoding="utf-8")
    before = json.loads(raw)
    drafts = json.loads(DRAFTS.read_text(encoding="utf-8"))
    if para not in drafts:
        raise SystemExit("ABORT: %s absent from %s" % (para, DRAFTS))
    prose = drafts[para]["final_prose"]
    status = drafts[para].get("prose_status", "DRAFTED")
    if not prose.strip():
        raise SystemExit("ABORT: %s final_prose is empty in drafts" % para)

    # scope every edit to the target paragraph's slice
    i = raw.index('"%s": {' % para)
    nxt = ORDER[ORDER.index(para) + 1] if para != ORDER[-1] else None
    j = raw.index('"%s": {' % nxt, i) if nxt else None
    head = raw[:i]
    body = raw[i:j] if j is not None else raw[i:]
    tail = raw[j:] if j is not None else ""

    enc = json.dumps(prose, ensure_ascii=False)  # exact JSON string literal
    if update:
        old_enc = json.dumps(before["paragraphs"][para]["final_prose"], ensure_ascii=False)
        if old_enc == '""':
            raise SystemExit("ABORT: %s final_prose is empty -- use normal transfer, not --update" % para)
        body = replace_once(body, '"final_prose": ' + old_enc, '"final_prose": ' + enc)
    else:
        body = replace_once(body, '"final_prose": ""', '"final_prose": ' + enc)  # empty-slot guard
        body = replace_once(body, '"prose_status": "BLOCKED"', '"prose_status": "%s"' % status)
        body = replace_once(body, '"all_supported": false', '"all_supported": true', required=False)
        body = replace_once(body, '"unlocked": false', '"unlocked": true', required=False)

    new = head + body + tail
    after = json.loads(new)  # must still be valid JSON

    allowed = {
        ".paragraphs.%s.final_prose" % para,
        ".paragraphs.%s.prose_status" % para,
        ".paragraphs.%s.prose_gate.all_supported" % para,
        ".paragraphs.%s.prose_gate.unlocked" % para,
    }
    diffs = changed_paths(before, after)
    bad = [d for d in diffs if d not in allowed]
    if bad:
        raise SystemExit("ABORT: unexpected JSON changes: %s" % bad)
    if after["paragraphs"][para]["final_prose"] != prose:
        raise SystemExit("ABORT: post-write prose mismatch")

    print("OK %s: changed %s" % (para, sorted(diffs)))
    if dry:
        print("dry-run: ledger NOT written")
        return
    LEDGER.write_text(new, encoding="utf-8")
    print("wrote ledger")
    if commit:
        subprocess.run(["git", "add", str(LEDGER)], check=True)
        subprocess.run([
            "git", "commit",
            "-m", "draft(2.1/%s): record advisor-cleared prose (programmatic transfer from tmp)" % para,
            "-m", "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>",
        ], check=True)
        print("committed %s" % para)


if __name__ == "__main__":
    main()
