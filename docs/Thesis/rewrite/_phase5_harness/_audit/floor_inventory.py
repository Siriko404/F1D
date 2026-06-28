# Issue-1 honesty-floor inventory + safety gate. Tags every floor-element mention by section so the
# de-hedging can (a) be planned from ground truth and (b) be PROVEN safe: re-run after thinning and confirm
# no section that carried an element before drops it to ZERO after. Read-only. Runs on the fresh FLAT.
#   usage:  python _audit/floor_inventory.py            -> print the per-section ledger + element/section grid
#           python _audit/floor_inventory.py --counts   -> print only the section x element count grid (for diffing)
import re, sys
from pathlib import Path

FLAT = Path(__file__).resolve().parents[1].parents[1] / "_uottawa_rewrite" / "_thesis_FLAT.tex"
txt = FLAT.read_text(encoding="utf-8")

# the locked honesty-floor elements and their surface signatures (case-insensitive)
ELEM = {
 "CORR":   r"correlational",
 "NOCAUSE":r"no caus|identifies no|does not\b[^.]{0,30}\bidentif|not a causal|causal (claim|effect|reading|one)|assert[s]? no cause|establish[a-z]* (a |no )?cause|identif[a-z]* no caus|no causal",
 "WITHIN": r"within.?firm|compared with (itself|themselves)|against (that same|its own|their own)",
 "MECH":   r"mechanism|war.?chest|unestablished|is not established|left open|remains open",
 "SUPP":   r"definitive|as proof\b|supportive",
 "CONC":   r"concentrat|strict[a-z]* specific|rather than (strict )?specific",
 "POWER":  r"powered (test|equivalence)|failure to find|absence of (an? )?associat|underpowered|not[, ]+by itself, a test|is not a test",
 "NULL":   r"noisy[, ]+(flat )?null|flat[, ]+noisy null|imprecise null|noisy (flat )?null",
 "BYPROD": r"by-product",
}
COMPILED = {k: re.compile(v, re.I) for k, v in ELEM.items()}

# split the FLAT into (heading, body) blocks at every \chapter/\section; ignore table/bib/appendix blocks
parts = re.split(r"\\(?:chapter|section)\*?\{([^}]*)\}", txt)
# parts = [pre, head1, body1, head2, body2, ...]
blocks = [(parts[i], parts[i+1]) for i in range(1, len(parts)-1, 2)]

def sentences(body):
    # drop comment lines + table/figure environments so we only see prose
    body = re.sub(r"(?m)^%.*$", "", body)
    body = re.sub(r"\\begin\{(table|tabular|minipage|figure)\}.*?\\end\{\1\}", "", body, flags=re.S)
    # rough sentence split on '. ' before a capital / start; keep it simple, this is an inventory
    chunks = re.split(r"(?<=[.;])\s+(?=[A-Z\\])", body)
    return [c.strip() for c in chunks if c.strip()]

grid = {}   # heading -> {elem: count}
ledger = []
for head, body in blocks:
    counts = {k: 0 for k in ELEM}
    for s in sentences(body):
        tags = [k for k, rx in COMPILED.items() if rx.search(s)]
        if tags:
            for k in tags:
                counts[k] += 1
            ledger.append((head, tags, re.sub(r"\s+", " ", s)[:240]))
    if any(counts.values()):
        grid[head] = counts

if "--counts" in sys.argv:
    print("%-46s %s" % ("SECTION", " ".join("%-7s" % k for k in ELEM)))
    for head, c in grid.items():
        print("%-46s %s" % (head[:46], " ".join("%-7d" % c[k] for k in ELEM)))
    tot = {k: sum(c[k] for c in grid.values()) for k in ELEM}
    print("%-46s %s" % ("== TOTAL ==", " ".join("%-7d" % tot[k] for k in ELEM)))
    sys.exit(0)

cur = None
for head, tags, s in ledger:
    if head != cur:
        print("\n=== %s ===" % head); cur = head
    print("  [%s] %s" % (",".join(tags), s))
print("\n%d floor sentences across %d sections" % (len(ledger), len(grid)))
