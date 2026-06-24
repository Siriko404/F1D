"""FREE post-pass: 3 deterministic checks on the 14 saved lit_review findings.
No LLM, no re-run. Measures how the proposed auto-flags actually fire on real output.
  1. hedge/negation token in any our_quote   (litotes/meaning-shift risk)
  2. digit in any our_quote                   (number-touch risk)
  3. each exemplar_quote in its CITED paper    (attribution fidelity; gate allows ANY paper)
Reports per finding so we can eyeball true vs false flags."""
import json, re
from pathlib import Path

ROOT = Path(".").resolve()
WF = ROOT/"docs/Thesis/rewrite/style_profiles"   # not used; journal path below
JOURNAL = Path(r"C:/Users/sinas/.claude/projects/C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D/ef5c9060-5c18-48e5-b556-5bb839b73b23/subagents/workflows/wf_8f466ec8-146/journal.jsonl")
BUNDLE = ROOT/"docs/papers/style_exemplars/bundles/lit_review.json"

# ---- same forgiving normalization the harness gate uses ----
def norm(s):
    s = (s or '').lower()
    s = re.sub(r"[‘’‛′]", "'", s)
    s = re.sub(r"[“”″]", '"', s)
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"[^\w]+", " ", s)
    s = re.sub(r"\b\d+\b", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()
def issub(q, hay): n = norm(q); return len(n) > 0 and n in norm(hay)

# ---- hedge/negation token set (deliberately a first-cut; we measure bluntness) ----
HEDGE = {"not","no","never","cannot","nor","neither","without","may","might","could",
         "would","suggest","suggests","consistent","empty","rather","merely","only",
         "less","fewer","tend","tends","appear","appears","seem","seems","likely",
         "unlikely","possibly","potential","necessarily","hardly","scarcely","nothing"}
def hedge_hits(s):
    toks = re.findall(r"[a-z']+", (s or '').lower())
    return sorted({t for t in toks if t in HEDGE})
def digit_hits(s): return bool(re.search(r"\d", s or ""))

# ---- load ground truth bundle ----
b = json.loads(BUNDLE.read_text(encoding="utf-8"))
ex_by_paper = {}
for s in b["exemplars"]:
    ex_by_paper.setdefault(s["paper"], []).extend(s["paragraphs"])
all_papers = set(ex_by_paper)
our_by_id = {u["para_id"]: u["final_prose"] for u in b["ours"]}

# ---- load 14 raw findings + redteam from journal ----
panel_num = {"a34c766208a78a281":1,"aea7729edcde94a00":2,"ae074c14344f2fd0e":3}
raw = {}; rt = None
for l in JOURNAL.read_text(encoding="utf-8").splitlines():
    l = l.strip()
    if not l: continue
    d = json.loads(l)
    if "result" not in d: continue
    r = d["result"]
    if isinstance(r, str):
        try: r = json.loads(r)
        except: pass
    aid = d.get("agentId","")
    if isinstance(r, dict) and "findings" in r: raw[panel_num[aid]] = r["findings"]
    elif isinstance(r, dict) and "keep" in r: rt = r

items = {}
for pn in (1,2,3):
    for fi, f in enumerate(raw[pn]):
        items[f"a{pn}-f{fi+1}"] = f

# fate
rej = {x["id"] for x in rt["reject"]}
canon = set(); mergedaway = {}
for m in rt["merge"]:
    canon.add(m["canonical"])
    for i in m["ids"]:
        if i != m["canonical"]: mergedaway[i] = m["canonical"]
keep = set(rt["keep"]) | canon
def fate(i):
    if i in rej: return "REJECT"
    if i in mergedaway: return f"merge>{mergedaway[i]}"
    if i in keep: return "KEEP"
    return "?"

# ---- run the 3 checks ----
print(f"{'id':<7}{'fate':<12}{'hedge?':<8}{'digit?':<7}{'attribution':<12} detail")
print("-"*100)
attribution_problems = []; hedge_keepers = []
for i, f in items.items():
    ft = fate(i)
    # check 1: hedge in our_quotes
    hh = sorted({h for q in f.get("our_quotes",[]) for h in hedge_hits(q.get("quote",""))})
    # check 2: digit in our_quotes
    dg = any(digit_hits(q.get("quote","")) for q in f.get("our_quotes",[]))
    # check 3: each exemplar quote in its CITED paper
    att = []
    for q in f.get("exemplar_quotes",[]):
        pp = q.get("paper",""); quote = q.get("quote","")
        in_cited = pp in ex_by_paper and issub(quote, "\n".join(ex_by_paper[pp]))
        if in_cited: continue
        elsewhere = [p for p in all_papers if p != pp and issub(quote, "\n".join(ex_by_paper[p]))]
        att.append((pp, elsewhere, quote[:45]))
    att_tag = "OK" if not att else ("FUZZY" if all(e for _,e,_ in att) else "FAIL")
    detail = ""
    if hh: detail += f"hedge={hh} "
    if att: detail += "| ".join(f"[{p}->{(e or 'NONE')}]" for p,e,_ in att)
    print(f"{i:<7}{ft:<12}{('YES' if hh else '-'):<8}{('YES' if dg else '-'):<7}{att_tag:<12} {detail}")
    if att: attribution_problems.append((i, att))
    if hh and ft == "KEEP": hedge_keepers.append((i, hh))

print("\n--- SUMMARY ---")
print(f"attribution issues (quote not in cited paper): {len(attribution_problems)} findings")
for i, att in attribution_problems:
    for p, e, qt in att:
        print(f"   {i}: claimed={p}  actual={e or 'NOT FOUND ANYWHERE'}  quote='{qt}...'")
print(f"\nKEPT findings that touch a hedge token (would auto-flag for human): {[i for i,_ in hedge_keepers]}")
print("Eyeball: which are TRUE (edit really touches the hedge) vs FALSE alarms?")
