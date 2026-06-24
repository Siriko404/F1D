"""Inventory every *_paragraph_ledger.json: prose units, words, and which spine fields exist.
Robust to both ledger shapes (list-of-paragraphs vs P1..Pn fields)."""
import json, re, glob
from pathlib import Path

ROOT = Path(".").resolve()
files = sorted(glob.glob(str(ROOT/"docs/Thesis/rewrite/section*_paragraph_ledger.json")))

def find_prose_units(obj, out):
    """recursively collect every dict that has a 'final_prose' key"""
    if isinstance(obj, dict):
        if "final_prose" in obj:
            out.append(obj)
        for v in obj.values():
            find_prose_units(v, out)
    elif isinstance(obj, list):
        for v in obj:
            find_prose_units(v, out)

def words(s): return len(re.findall(r"\S+", s or ""))
def has(u, *keys): return any(k in u and u[k] for k in keys)

print(f"{'ledger':<34}{'title/sub':<30}{'units':>5}{'filled':>7}{'words':>7}{'prop':>5}{'guard':>6}{'#aud':>5}")
print("-"*100)
tot_u=tot_f=tot_w=0
for f in files:
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    name = Path(f).name.replace("_paragraph_ledger.json","")
    title = str(d.get("title") or d.get("subsection") or d.get("subsection_id") or "")[:28]
    units=[]; find_prose_units(d, units)
    filled = sum(1 for u in units if (u.get("final_prose") or "").strip())
    w = sum(words(u.get("final_prose")) for u in units)
    nprop = sum(1 for u in units if has(u,"proposition_chain","propositions"))
    nguard= sum(1 for u in units if has(u,"guardrails","register_locks"))
    naud  = sum(1 for u in units if has(u,"number_audit","numbers"))
    tot_u+=len(units); tot_f+=filled; tot_w+=w
    print(f"{name:<34}{title:<30}{len(units):>5}{filled:>7}{w:>7}{nprop:>5}{nguard:>6}{naud:>5}")
print("-"*100)
print(f"{'TOTAL':<64}{tot_u:>5}{tot_f:>7}{tot_w:>7}")
print(f"\n{len(files)} ledgers | {tot_u} prose units | {tot_f} with final_prose filled | ~{tot_w:,} words")
