"""Append _proposed_fixes to the section-3 clones: surgically sweep the DESCRIPTIVE
'stock placebo' framing -> 'comparison' while PROTECTING the fixed identifiers
(tab:empire_drop_placebo label; placebo_cash_PRE1 / placebo_stock_PRE1 variable keys --
they span 18 files: bible .tex, variable_ledger, claim_findings_ledger, compiled body).

AUDIT CONTRACT (for the advisor):
  - sweep() masks the 3 identifier tokens, replaces only the remaining 'placebo'/'Placebo',
    then restores the tokens. The script ASSERTS no proposed text corrupts an identifier
    (no 'empire_drop_comparison' / 'comparison_cash_PRE1' / 'comparison_stock_PRE1').
  - Each fix records field-path + from + to (pulled from the clone, not retyped).
  - Originals untouched; fixes APPENDED under _proposed_fixes. No new cite props (results section).

Run:  python tmp/append_s3_proposed_fixes.py
"""
import json
from pathlib import Path

FORK = Path(__file__).resolve().parents[1]
CD = FORK / "docs" / "Thesis" / "rewrite" / "_phase3_clones"
IDENT = ["empire_drop_placebo", "placebo_cash_PRE1", "placebo_stock_PRE1"]

def sweep(t):
    m = t
    for i, tok in enumerate(IDENT):
        m = m.replace(tok, f"\x00{i}\x00")
    m = m.replace("Placebo", "Comparison").replace("placebo", "comparison")
    for i, tok in enumerate(IDENT):
        m = m.replace(f"\x00{i}\x00", tok)
    return m

def walk(o, path):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k == "_proposed_fixes":
                continue
            yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")

NO_SUP = ("No 'stock suppressed' / stock not pushed below baseline -- the stock comparison arm is a "
          "noisy flat null (-0.0429 n.s.); the cash-vs-stock gap is cash rising, not stock falling. "
          "We interpret, we do not detect (masking register, 2.1/2.2).")

audit_corrupt = []
summary = {}
for s in ["3.1", "3.2", "3.3", "3.4"]:
    path = CD / f"section{s}_paragraph_ledger.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    fixes, keeps = [], 0
    n = 1
    for fpath, txt in walk(d, "doc"):          # WHOLE doc (incl. allocation_coverage), minus _proposed_fixes
        if "placebo" not in txt.lower():
            continue
        to = sweep(txt)
        if to == txt:
            keeps += 1                                    # only identifier tokens -> kept
            continue
        # corruption guard
        for bad in ("empire_drop_comparison", "comparison_cash_PRE1", "comparison_stock_PRE1"):
            if bad in to:
                audit_corrupt.append((s, fpath, bad))
        fixes.append({"fix_id": f"S{s}-F{n}", "locus": fpath, "action": "SWEEP",
                      "change": "descriptive stock placebo -> comparison (identifiers protected)",
                      "reword": {"field": fpath, "from": txt, "to": to}})
        n += 1
    # no-suppression register-lock guard where the stock comparison is discussed
    if s in ("3.2", "3.4"):
        fixes.append({"fix_id": f"S{s}-F{n}", "locus": "stock-comparison paragraph", "action": "ADD_REGISTER_LOCK",
                      "change": "guard regenerated prose against 'stock suppressed'",
                      "proposed_register_lock": NO_SUP})
    d["_proposed_fixes"] = {
        "summary": f"Surgical placebo->comparison sweep of descriptive stock-arm framing ({len(fixes)} "
                   f"fixes); {keeps} identifier hits KEPT (tab:empire_drop_placebo / placebo_*_PRE1, "
                   f"18-file cross-ref). Results section -> no new cite props.",
        "register_locks": ["stock = comparison not inert placebo (matches 2.1/2.2)",
                           "NO stock-suppressed", "we interpret, we do not detect"],
        "fixes": fixes,
    }
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    summary[s] = (len([f for f in fixes if f["action"] == "SWEEP"]), keeps,
                  len([f for f in fixes if f["action"] == "ADD_REGISTER_LOCK"]))

print("=" * 74)
print(f"{'sub':5}{'SWEEP fixes':14}{'identifier KEEPS':18}{'no-suppress locks'}")
for s, (sw, kp, lk) in summary.items():
    print(f"{s:5}{sw:<14}{kp:<18}{lk}")
print("=" * 74)
if audit_corrupt:
    print("!! IDENTIFIER CORRUPTION:", audit_corrupt)
else:
    print("INTEGRITY OK: no identifier token corrupted in any proposed text.")
print("Originals untouched; fixes appended; descriptive framing swept, fixed identifiers preserved.")
