#!/usr/bin/env python3
"""NLM verification runner for the thesis Section 2.1 paragraph ledger.

ONE durable, committed script. It is the only sanctioned channel for the NLM
side of verification -- no ad-hoc queries.

What it does, deterministically:
  * resolve  : match each paper to its notebook source by a DURABLE title
               substring (never an eyeballed id); record id+title into the
               ledger; print a found / missing / ambiguous truth table; commit.
  * paragraph: for the requested paragraph, run each external-NLM proposition's
               ONE atomic, self-contained, non-leading query (E3-E6); capture the
               VERBATIM cited_text into the ledger; save the FULL raw response to
               nlm_2.1_raw.json; git-commit each step. Resumable -- a proposition
               that already holds evidence is skipped (no re-burn of quota).

Isolation (two hard guarantees, per nlm.py's proven pattern):
  * `notebooklm clear`              -> no conversation carry-over (self-contained)
  * `notebooklm ask -s <source_id>` -> answer scoped to ONE paper's source
  The source id is used ONLY transiently for -s; the human title+author+year is
  what every query NAMES and what the ledger records.

Verdicts are NOT set here. The script captures evidence; adjudication
(SUPPORTED / OVERCLAIM / ...) is a separate human step on the verbatim cited_text.
Legal-primary propositions (e.g. Basic v. Levinson, Rule 10b-5) are NOT on NLM --
the script skips them and prints a reminder to verify via official legal text.

Usage:
  python docs/Thesis/rewrite/nlm_verify.py --resolve
  python docs/Thesis/rewrite/nlm_verify.py --paragraph P1
  python docs/Thesis/rewrite/nlm_verify.py --paragraph P1 --dry   # print, no calls
  python docs/Thesis/rewrite/nlm_verify.py --baseline             # commit current state only
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

try:                                  # Windows console is cp1252; source titles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # contain U+2010 etc.
except Exception:
    pass

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                       # rewrite -> Thesis -> docs -> F1D
LEDGER = HERE / "section2.1_paragraph_ledger.json"
RAW = HERE / "nlm_2.1_raw.json"
NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")
PREFIX = "Reading only this paper, "

# --- paper registry -----------------------------------------------------------
# key -> {"label": how the QUERY names the paper (title + authors + year + venue),
#         "match": a DURABLE case-insensitive substring unique to its source title}
PAPERS = {
    "verrecchia1983":     {"label": '"Discretionary Disclosure" by Verrecchia (1983, Journal of Accounting and Economics)', "match": "0165410183900113"},
    "dye1985":            {"label": '"Disclosure of Nonproprietary Information" by Dye (1985, Journal of Accounting Research)', "match": "dye-disclosurenonproprietary"},
    "lm2011":             {"label": '"When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks" by Loughran and McDonald (2011, Journal of Finance)', "match": "loughran"},
    "hollander2010":      {"label": '"Does Silence Speak? An Empirical Analysis of Disclosure Choices During Conference Calls" by Hollander, Pronk and Roelofsen (2010, Journal of Accounting Research)', "match": "hollander - does silence"},
    "bushee2018":         {"label": '"Linguistic Complexity in Firm Disclosures: Obfuscation or Information?" by Bushee, Gow and Taylor (2018, Journal of Accounting Research)', "match": "bushee - linguistic complexity"},
    "bertrand_schoar2003": {"label": '"Managing with Style: The Effect of Managers on Firm Policies" by Bertrand and Schoar (2003, Quarterly Journal of Economics)', "match": "118-4-1169"},
    "harford1999":        {"label": '"Corporate Cash Reserves and Acquisitions" by Harford (1999, Journal of Finance)', "match": "harford - corporate cash reserves"},
    "thewissen2024":      {"label": 'the paper by Thewissen et al. (2024) on tone management in earnings press releases around stock-for-stock acquisitions', "match": "4900453"},
    "ragozzino2024":      {"label": 'the paper by Ragozzino and Reuer (2024) on M&A-related earnings-call disclosures', "match": "s0024630123001000"},
}

# --- query plan ---------------------------------------------------------------
# prop_id -> (paper_key, atomic non-leading question). NLM (external) props only.
# P1 is final. P2-P7 are PROVISIONAL -- finalized when each paragraph's turn comes
# (edit this dict; it is the single source of truth for the queries).
QUERIES = {
    # ---- P1 (FINAL) -- disclosure-withholding theory ----
    "P1.1": ("verrecchia1983",
             "under what conditions, if any, does it conclude that a manager who possesses private information will choose not to disclose that information?"),
    "P1.2": ("dye1985",
             "what determines whether a manager discloses or withholds the information it may have, and what role does the possibility that the manager is uninformed play in sustaining non-disclosure?"),

    # ---- P2 (PROVISIONAL) -- call as venue + textual analysis ----
    "P2.1": ("hollander2010",
             "what does it say about the question-and-answer portion of conference calls compared with the prepared managerial presentation, and whether the discussion is more spontaneous or less scripted?"),
    "P2.2": ("lm2011",
             "what does it say about using word lists or dictionaries to measure tone or uncertainty in financial text, and whether such textual measures carry information?"),
    "P2.3": ("bushee2018",
             "what does it conclude about whether linguistic features of corporate disclosures carry information beyond the financial numbers?"),

    # ---- P3 (PROVISIONAL) -- strategic silence -> anticipatory ----
    "P3.1": ("hollander2010",
             "what does it find about managers' choices to answer, deflect, or stay silent on conference calls, and whether such choices are informative to the market?"),

    # ---- P4 (PROVISIONAL) -- managerial style ----
    "P4.1": ("bertrand_schoar2003",
             "what does it conclude about whether individual managers have persistent, distinctive styles that show up as manager fixed effects in firm policies?"),

    # ---- P5 (PROVISIONAL) -- cash-for-acquisitions ----
    "P5.1": ("harford1999",
             "what does it find about whether firms accumulate cash reserves in advance of acquisitions and whether cash-rich firms are more likely to attempt acquisitions?"),

    # ---- P6 (PROVISIONAL) -- nearest work ----
    "P6.1": ("thewissen2024",
             "what disclosure channel, payment method, and timing relative to the acquisition does it study, and what does it measure about the language?"),
    "P6.2": ("ragozzino2024",
             "what does it study about the language of earnings-call disclosures around merger and acquisition activity, and how does it measure it?"),
}

# Propositions verified OUTSIDE NLM (legal primary sources) -- never queried here.
LEGAL_SKIP = {"P1.3", "P1.4"}


def cli(args, timeout):
    return subprocess.run([EXE, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r


def commit(paths, message):
    git("add", *[str(p) for p in paths])
    r = git("commit", "-m", message)
    out = (r.stdout or "") + (r.stderr or "")
    if "nothing to commit" in out:
        print(f"  (git: nothing to commit) {message}")
    else:
        print(f"  git commit: {message}")


def make_evidence(refs):
    """Verbatim cited_text + its EXACT in-source location (char span + chunk)."""
    return [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
             "source_id": x.get("source_id"),
             "start_char": x.get("start_char"), "end_char": x.get("end_char"),
             "chunk_id": x.get("chunk_id")}
            for x in refs if x.get("cited_text")]


def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_ledger(d):
    LEDGER.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def save_raw(d):
    RAW.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def list_sources():
    r = cli(["source", "list", "-n", NOTEBOOK, "--json"], timeout=120)
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit("ERROR: could not list sources.\n" + out[:500] + (r.stderr or "")[:500])
    return json.loads(out[i:])["sources"]


def resolve(commit_it=True):
    """Match each paper -> notebook source by durable title substring; record id+title."""
    sources = list_sources()
    led = load(LEDGER, {})
    reg = led.setdefault("resolved_sources", {})
    print(f"Resolving {len(PAPERS)} papers against {len(sources)} notebook sources:\n")
    for key, p in PAPERS.items():
        hits = [s for s in sources if p["match"].lower() in s["title"].lower()]
        if not hits:
            print(f"  MISSING    {key:<22} (match '{p['match']}')")
            reg[key] = {"status": "MISSING", "match": p["match"], "source_id": None, "source_title": None}
            continue
        if len(hits) > 1:
            hits = sorted(hits, key=lambda s: s.get("created_at", ""), reverse=True)
            print(f"  AMBIGUOUS  {key:<22} {len(hits)} matches -> newest: {hits[0]['title']}")
        chosen = hits[0]
        status = "AMBIGUOUS_NEWEST" if len(hits) > 1 else "OK"
        reg[key] = {"status": status, "match": p["match"],
                    "source_id": chosen["id"], "source_title": chosen["title"],
                    "created_at": chosen.get("created_at")}
        # mirror the id into papers{} if that paper key exists there
        if "papers" in led and key in led["papers"] and isinstance(led["papers"][key], dict):
            led["papers"][key]["nlm_source_id"] = chosen["id"]
            led["papers"][key]["nlm_source_title"] = chosen["title"]
        if status == "OK":
            print(f"  OK         {key:<22} {chosen['title']}")
    save_ledger(led)
    if commit_it:
        commit([LEDGER, Path(__file__)],
               "verify(2.1): resolve notebook sources by title-match; record ids in ledger")
    return led


def ask(source_id, paper_label, question):
    """One isolated, self-contained, source-scoped query. Returns full raw + parsed."""
    try:
        cli(["clear"], timeout=60)
    except Exception:
        pass
    full_q = f"{PREFIX}{paper_label}: {question}"
    try:
        r = cli(["ask", "-n", NOTEBOOK, "-s", source_id, "--json", full_q], timeout=420)
    except subprocess.TimeoutExpired:
        return {"query": full_q, "error": "timeout"}
    out = r.stdout or ""
    i = out.find("{")
    preamble = out[:i].strip() if i > 0 else ""      # e.g. "Matched: <id> (<title>)"
    if i < 0:
        return {"query": full_q, "preamble": preamble, "error": "no JSON",
                "raw": (out + (r.stderr or ""))[:800]}
    try:
        j = json.loads(out[i:])
    except Exception as e:
        return {"query": full_q, "preamble": preamble, "error": f"json parse: {e}",
                "raw": out[i:i + 800]}
    return {"query": full_q, "preamble": preamble, "raw_json": j}


def run_paragraph(pid, dry=False):
    led = load(LEDGER, {})
    reg = led.get("resolved_sources")
    if not reg:
        print("No resolved_sources in ledger -- running --resolve first.\n")
        led = resolve()
        reg = led["resolved_sources"]
    para = led["paragraphs"].get(pid)
    if not para:
        sys.exit(f"ERROR: paragraph {pid} not in ledger.")
    raw = load(RAW, {})
    print(f"\n=== Paragraph {pid} :: {para.get('lit_body','')} ===")
    for prop in para["propositions"]:
        ppid = prop["prop_id"]
        if ppid in LEGAL_SKIP or prop.get("type") == "legal-primary":
            print(f"  LEGAL  {ppid}: verify via official legal text (not NLM) -- skipped.")
            continue
        if prop.get("type") != "external-NLM":
            print(f"  SKIP   {ppid}: type={prop.get('type')}")
            continue
        ev = prop.get("verification", {}).get("evidence")
        if ev:
            print(f"  DONE   {ppid}: evidence already present -- skipped (resumable).")
            continue
        if ppid not in QUERIES:
            print(f"  TODO   {ppid}: no query authored yet -- skipped.")
            continue
        paper_key, question = QUERIES[ppid]
        src = reg.get(paper_key, {})
        if src.get("status") == "MISSING" or not src.get("source_id"):
            print(f"  BLOCK  {ppid}: source '{paper_key}' MISSING in notebook -- cannot verify.")
            continue
        label = PAPERS[paper_key]["label"]
        full_q = f"{PREFIX}{label}: {question}"
        if dry:
            print(f"  DRY    {ppid} [{paper_key}]\n         {full_q}")
            continue
        print(f"  ASK    {ppid} [{paper_key}] ...", flush=True)
        res = ask(src["source_id"], label, question)
        j = res.get("raw_json", {})
        refs = j.get("references", []) if j else []
        evidence = make_evidence(refs)
        v = prop.setdefault("verification", {})
        v["method"] = "NLM"
        v["query_used"] = res.get("query")
        v["source_scoped"] = {"key": paper_key, "id": src["source_id"], "title": src.get("source_title")}
        v["source_matched_preamble"] = res.get("preamble", "")
        v["evidence"] = evidence
        v["answer_nonevidence"] = (j.get("answer", "") if j else res.get("error", ""))
        # verdict left as-is (PENDING) -- human adjudicates on the verbatim cited_text.
        raw[ppid] = res
        save_ledger(led)
        save_raw(raw)
        n_ev = len(evidence)
        commit([LEDGER, RAW, Path(__file__)],
               f"verify(2.1): {ppid} evidence captured ({n_ev} quotes) from {paper_key}")
        print(f"         -> {n_ev} verbatim quote(s) captured"
              + ("" if n_ev else "  [!] no cited_text -- review answer_nonevidence"))
    print(f"\n[{pid}] done. Adjudicate verdicts on the verbatim cited_text, then write prose.")


def rebuild_from_raw():
    """Re-derive ledger evidence (incl. char-offsets + chunk_id) from saved raw. No NLM calls."""
    led = load(LEDGER, {})
    raw = load(RAW, {})
    n = 0
    for para in led["paragraphs"].values():
        for prop in para["propositions"]:
            r = raw.get(prop["prop_id"], {})
            j = r.get("raw_json", {})
            refs = j.get("references", []) if isinstance(j, dict) else []
            if not refs:
                continue
            v = prop.setdefault("verification", {})
            v["evidence"] = make_evidence(refs)
            v["query_used"] = r.get("query", v.get("query_used"))
            v["source_matched_preamble"] = r.get("preamble", v.get("source_matched_preamble", ""))
            v["answer_nonevidence"] = j.get("answer", v.get("answer_nonevidence", ""))
            n += 1
            print(f"  rebuilt {prop['prop_id']}: {len(v['evidence'])} quote(s) with offsets")
    save_ledger(led)
    commit([LEDGER, Path(__file__)], "verify(2.1): rebuild ledger evidence from raw (add char-offsets + chunk_id)")
    print(f"Rebuilt {n} proposition(s) from raw.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true", help="map papers->sources, record ids, commit")
    ap.add_argument("--paragraph", help="run a paragraph's NLM props, e.g. P1")
    ap.add_argument("--dry", action="store_true", help="print queries, do not call NLM")
    ap.add_argument("--baseline", action="store_true", help="commit current ledger+script state only")
    ap.add_argument("--rebuild-from-raw", action="store_true", help="re-derive ledger evidence (offsets+chunk) from raw; no NLM calls")
    args = ap.parse_args()
    if args.rebuild_from_raw:
        rebuild_from_raw()
        return
    if not EXE:
        sys.exit("ERROR: `notebooklm` CLI not found on PATH. Run `notebooklm login` first.")
    if args.baseline:
        commit([LEDGER, Path(__file__)], "verify(2.1): baseline -- deterministic ledger + nlm_verify runner")
        return
    if args.resolve:
        resolve()
    if args.paragraph:
        run_paragraph(args.paragraph, dry=args.dry)
    if not (args.resolve or args.paragraph):
        ap.print_help()


if __name__ == "__main__":
    main()
