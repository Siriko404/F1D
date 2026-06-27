"""STEP 0 + GATE-0 for the proposition-chain referee audit.

Reads the 16 PRISTINE clones (chain + parked _proposed_fixes), APPLIES the fixes to a
throwaway copy, tags provenance, moves NLM verbatim to an appendix, stitches one ordered
corpus.json. Runs GATE-0 (must pass before the panel). Originals are NEVER written.

Apply strategy (robust, path-agnostic): every REWORD/SWEEP carries verbatim from/to, so we
replace string leaves EQUAL to `from` with `to` across the whole section dict (the parked
_proposed_fixes block is popped first, so no self-collision). ADD_PROP inserts the full
proposed_prop into its locus paragraph. This is exactly what GATE-0 then re-verifies.

Run:  python <abspath>/build_corpus.py
"""
import json, copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # ...\rewrite
CD = ROOT / "_phase3_clones"
OUT = ROOT / "_audit"
OUT.mkdir(exist_ok=True)

ORDER = ["_abstract", "1", "2.1", "2.2", "2.3", "2.4", "2.5",
         "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "4.3", "4.4", "5"]

IDENT = ["empire_drop_placebo", "placebo_cash_PRE1", "placebo_stock_PRE1"]
CORRUPT = ["empire_drop_comparison", "comparison_cash_PRE1", "comparison_stock_PRE1"]

BRIGHT_LINES = [
    "masking = MOTIVATION, not mechanism / not identification",
    "NO 'stock suppressed' -- stock -0.0429 n.s. (noisy flat null); the gap is CASH RISING",
    "cite Shleifer-Vishny + Louis as EARNINGS/VALUATION, NEVER tone; thewissen = tone (preprint, supplementary)",
    "SOURCE mechanism (compliance-constrained vs strategic) stays OPEN",
    "war-chest / cash-accumulation CAUSE stays OPEN (C6 cause 0.0064 n.s.)",
    "concentration = motivated, NOT identified; correlational, within-firm, no causal id",
    "concentration-not-strict-specificity; 'we interpret, we do not detect'",
    "each section's own register_locks are bright lines; a fix that hardens/removes a hedge is INVALID",
]

# ---------- helpers ----------
def walk_replace(o, frm, to):
    if isinstance(o, str):
        return (to, 1) if o == frm else (o, 0)
    if isinstance(o, dict):
        c = 0; nd = {}
        for k, v in o.items():
            nd[k], cc = walk_replace(v, frm, to); c += cc
        return nd, c
    if isinstance(o, list):
        c = 0; nl = []
        for v in o:
            nv, cc = walk_replace(v, frm, to); nl.append(nv); c += cc
        return nl, c
    return o, 0

def iter_props(paras):
    plist = list(paras.values()) if isinstance(paras, dict) else paras
    for para in plist:
        if not isinstance(para, dict):
            continue
        for key in ("proposition_chain", "propositions"):
            ch = para.get(key)
            if isinstance(ch, list):
                for p in ch:
                    if isinstance(p, dict) and "prop_id" in p:
                        yield p

def prop_map(paras):
    return {p["prop_id"]: p for p in iter_props(paras)}

def insert_prop(paras, locus, pp):
    """Append pp into the locus paragraph's prop list. Returns True on success."""
    def chain_of(para):
        for key in ("propositions", "proposition_chain"):
            if isinstance(para.get(key), list):
                return para[key]
        return None
    cands = []
    if isinstance(paras, dict):
        if locus in paras:
            cands.append(paras[locus])
        for k, para in paras.items():
            if isinstance(para, dict) and (para.get("para_id") == locus or k == locus):
                cands.append(para)
    else:
        for para in paras:
            if isinstance(para, dict) and para.get("para_id") == locus:
                cands.append(para)
    # fallback: match by prop_id prefix (e.g. P3.4 -> paragraph whose props are P3.x)
    if not cands:
        pid = pp.get("prop_id", "")
        stem = pid.rsplit(".", 1)[0] if "." in pid else pid
        target_paras = list(paras.values()) if isinstance(paras, dict) else paras
        for para in target_paras:
            ch = chain_of(para) or []
            if any(isinstance(x, dict) and str(x.get("prop_id", "")).startswith(stem) for x in ch):
                cands.append(para)
    for para in cands:
        ch = chain_of(para)
        if ch is not None:
            ch.append(pp)
            return True
    return False

def orphans(paras):
    pm = prop_map(paras); ids = set(pm)
    bad = set()
    for pid, p in pm.items():
        for dep in p.get("depends_on", []) or []:
            if dep not in ids:
                bad.add((pid, dep))
    return bad

def extract_evidence(prop):
    """Pop bulky NLM verbatim into a dict; return it (or None). Mutates prop in place."""
    v = prop.get("verification")
    if not isinstance(v, dict):
        return None
    moved = {}
    for kk in ("answer", "quotes", "located", "span_pin", "span_pins"):
        if kk in v:
            moved[kk] = v.pop(kk)
    if isinstance(v.get("parts"), list):
        for part in v["parts"]:
            if isinstance(part, dict):
                pm = {}
                for kk in ("answer", "quotes", "located"):
                    if kk in part:
                        pm[kk] = part.pop(kk)
                if pm:
                    moved.setdefault("parts", []).append(pm)
    if moved:
        v["_evidence_ref"] = f"appendix:{prop['prop_id']}"
    return moved or None

# ---------- build ----------
gate_fails = []
warns = []
sections = []
appendix = {}
tot = {"props": 0, "added": 0, "reworded": 0, "swept": 0, "original": 0, "meta_touched": 0, "fixes": 0}

for sid in ORDER:
    f = CD / f"section{sid}_paragraph_ledger.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    pf = d.pop("_proposed_fixes", {}) or {}
    fixes = pf.get("fixes", [])
    tot["fixes"] += len(fixes)

    orig = copy.deepcopy(d)
    orig_pm = prop_map(orig["paragraphs"])
    orig_count = len(orig_pm)
    orig_orphans = orphans(orig["paragraphs"])

    work = copy.deepcopy(d)
    added_ids = []

    # 1. apply
    for fx in fixes:
        a = fx.get("action")
        if a in ("REWORD", "SWEEP") and isinstance(fx.get("reword"), dict):
            frm, to = fx["reword"]["from"], fx["reword"]["to"]
            work, c = walk_replace(work, frm, to)
            if c == 0:
                gate_fails.append((sid, fx.get("fix_id", "?"), "FROM-not-matched"))
            elif c > 1:
                warns.append((sid, fx.get("fix_id", "?"), f"OVER-REPLACE c={c} -- eyeball intended"))
        elif a == "ADD_PROP":
            pp = copy.deepcopy(fx.get("proposed_prop"))
            if not pp or "prop_id" not in pp:
                gate_fails.append((sid, fx.get("fix_id", "?"), "ADD_PROP-malformed")); continue
            ok = insert_prop(work["paragraphs"], fx.get("locus"), pp)
            if not ok:
                gate_fails.append((sid, fx.get("fix_id", "?"), f"ADD_PROP-insert-failed locus={fx.get('locus')}"))
            else:
                added_ids.append(pp["prop_id"])

    new_pm = prop_map(work["paragraphs"])

    # 2. provenance tags (before evidence extraction so diffs are faithful)
    for pid, p in new_pm.items():
        if pid in added_ids or pid not in orig_pm:
            p["_provenance"] = "ADDED"; tot["added"] += 1
            continue
        before = json.dumps(orig_pm[pid], ensure_ascii=False, sort_keys=True)
        after = json.dumps(p, ensure_ascii=False, sort_keys=True)
        stmt_changed = orig_pm[pid].get("statement") != p.get("statement")
        if before == after:
            p["_provenance"] = "ORIGINAL-locked"; tot["original"] += 1
        elif not stmt_changed:
            # only meta (role/evidence/etc.) touched -- the CLAIM is unchanged; don't flag for claim-scrutiny
            p["_provenance"] = "ORIGINAL-locked"; p["_meta_touched"] = True
            tot["original"] += 1; tot["meta_touched"] += 1
        else:
            acts = set()
            for fx in fixes:
                if fx.get("action") in ("REWORD", "SWEEP") and isinstance(fx.get("reword"), dict):
                    if fx["reword"]["from"] in before:
                        acts.add(fx["action"])
            if acts == {"SWEEP"}:
                p["_provenance"] = "SWEPT"; tot["swept"] += 1
            else:
                p["_provenance"] = "REWORDED"; tot["reworded"] += 1
            p["_original_statement"] = orig_pm[pid].get("statement")

    # 3. GATE-0 structural
    new_count = len(new_pm)
    if new_count != orig_count + len(added_ids):
        gate_fails.append((sid, "COUNT", f"{new_count} != {orig_count}+{len(added_ids)}"))
    new_orphans = orphans(work["paragraphs"])
    for pid, dep in (new_orphans - orig_orphans):
        gate_fails.append((sid, pid, f"NEW depends_on orphan: {dep}"))
    for pid, dep in (new_orphans & orig_orphans):
        warns.append((sid, pid, f"pre-existing depends_on orphan: {dep}"))
    ws, os_ = json.dumps(work, ensure_ascii=False), json.dumps(orig, ensure_ascii=False)
    for tok in IDENT:
        if tok in os_ and tok not in ws:
            gate_fails.append((sid, "IDENT", f"lost: {tok}"))
    for tok in CORRUPT:
        if tok in ws:
            gate_fails.append((sid, "IDENT", f"corruption: {tok}"))

    # 4. evidence -> appendix
    for pid, p in new_pm.items():
        mv = extract_evidence(p)
        if mv:
            appendix[pid] = mv

    tot["props"] += new_count
    # section-level logic / register context (fixes already applied to these too, e.g. _plan F9/F10)
    ctx = {}
    for k in ("_plan", "register_global", "register", "allocation_coverage"):
        if k in work:
            ctx[k] = work[k]
    gov = work.get("_governing", {})
    if isinstance(gov, dict) and "claim_ceiling" in gov:
        ctx["claim_ceiling"] = gov["claim_ceiling"]
    sections.append({
        "section_id": sid,
        "title": d.get("title", ""),
        "fix_summary": pf.get("summary", ""),
        "guards_added": [fx.get("proposed_register_lock") or fx.get("proposed_guardrail")
                         for fx in fixes if fx.get("action") in ("ADD_REGISTER_LOCK", "ADD_GUARDRAIL")],
        "section_context": ctx,
        "paragraphs": work["paragraphs"],
    })

gate_pass = len(gate_fails) == 0
corpus = {
    "meta": {
        "purpose": "proposition-chain referee audit corpus (fixes applied to a throwaway copy; originals pristine)",
        "sections": len(sections), "total_props": tot["props"], "total_fixes": tot["fixes"],
        "provenance": {k: tot[k] for k in ("original", "added", "reworded", "swept")},
        "gate0": "PASS" if gate_pass else "FAIL",
    },
    "bright_lines": BRIGHT_LINES,
    "sections": sections,
    "appendix": appendix,
}
(OUT / "corpus.json").write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")

# ---------- report ----------
print("=" * 78)
print(f"STEP 0  corpus.json written  ({len(sections)} sections, {tot['props']} props, {tot['fixes']} fixes)")
print(f"        provenance: ORIGINAL={tot['original']} (meta-only touched {tot['meta_touched']})  "
      f"ADDED={tot['added']}  REWORDED={tot['reworded']}  SWEPT={tot['swept']}")
print(f"        appendix entries (props w/ NLM verbatim): {len(appendix)}")
print("=" * 78)
print(f"GATE-0: {'PASS' if gate_pass else 'FAIL'}")
if gate_fails:
    print(f"  {len(gate_fails)} FAILURES:")
    for x in gate_fails:
        print("   ", x)
if warns:
    print(f"  {len(warns)} warnings (pre-existing, not blocking):")
    for x in warns[:20]:
        print("   ", x)
print("=" * 78)

# ---------- eyeball aids (advisor pre-fan-out checks) ----------
def para_props(sec_id, para_id):
    for s in sections:
        if s["section_id"] != sec_id:
            continue
        paras = s["paragraphs"]
        para = paras.get(para_id) if isinstance(paras, dict) else \
            next((x for x in paras if isinstance(x, dict) and x.get("para_id") == para_id), None)
        if para:
            for key in ("propositions", "proposition_chain"):
                if isinstance(para.get(key), list):
                    return [(p.get("prop_id"), p.get("_provenance")) for p in para[key]]
    return None

print("EYEBALL  ADD_PROP placement (must be INSIDE the named paragraph):")
print("  §2.1 P5 :", para_props("2.1", "P5"))
print("  §2.2 P3 :", para_props("2.2", "P3"))
missing_ref = []
for s in sections:
    for p in iter_props(s["paragraphs"]):
        v = p.get("verification")
        if isinstance(v, dict) and "_evidence_ref" in v:
            key = v["_evidence_ref"].split(":", 1)[1]
            if key not in appendix:
                missing_ref.append(p["prop_id"])
print("  evidence_ref unresolved:", missing_ref or "none")
print("  §2.1 _plan folded into section_context:",
      bool(next(s for s in sections if s["section_id"] == "2.1")["section_context"].get("_plan")))
print("=" * 78)
# sanity: provenance total must equal prop total
assert tot["original"] + tot["added"] + tot["reworded"] + tot["swept"] == tot["props"], "provenance miscount"
print("provenance accounting OK" if gate_pass else "FIX GATE FAILURES BEFORE RUNNING THE PANEL")
