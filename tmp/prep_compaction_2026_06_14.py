# Compaction prep 2026-06-14: user said "consider everything ratified for now".
# (1) Flip 2.3/2.4/2.5 ledger gates -> RATIFIED (provisional). (2) Sweep _RESUME_STATE.json
# stale fields to current reality (§2 ratified; Table 1 built; all 11 tables wired; 5 refs; FB filled).
# Fail-closed: re-validates every JSON at the end.
import json

RAT = "RATIFIED 2026-06-14 (user: 'consider everything ratified for now'; PROVISIONAL, from PDF -- may revisit)"

# ---------- (1) ledger gates ----------
for sub in ("2.3", "2.4", "2.5"):
    p = f"docs/Thesis/rewrite/section{sub}_paragraph_ledger.json"
    d = json.load(open(p, encoding="utf-8"))
    for k, para in d.get("paragraphs", {}).items():
        para["prose_status"] = RAT
        if isinstance(para.get("prose_gate"), dict):
            para["prose_gate"]["all_supported"] = True
            para["prose_gate"]["unlocked"] = True
    d["status"] = RAT + " | prose in thesis_draft.tex (full §2, compiles clean)."
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    json.load(open(p, encoding="utf-8"))  # validate

# ---------- (2) resume sweep ----------
RS = "docs/Thesis/rewrite/_RESUME_STATE.json"
r = json.load(open(RS, encoding="utf-8"))

r["updated"] = ("2026-06-14 (RATIFIED-PROVISIONAL: §2 (2.1-2.5) prose ratified per user 'consider everything "
    "ratified for now'; Table 1 (all-universe, 23 vars) BUILT; all 11 tables WIRED into thesis_draft.tex (22pp, "
    "clean); 5 §2 table refs added; FB economic effect FILLED. Committed a65872f. Compaction-prepped.)")

r["mission"] = r["mission"] + (" [2026-06-14 UPDATE: PROSE PHASE COMPLETE -- §2 (2.1-2.5) ratified (provisional); "
    "Table 1 built (all-universe); all 11 result tables wired into the draft; 5 §2 table refs added; FB filled. "
    "Next = build the Appendix + write §3/§4/§5/abstract/intro.]")

r["where_we_are"] = ("[2026-06-14] §2 COMPLETE + RATIFIED (provisional, user). thesis_draft.tex = full §2 (2.1-2.5 "
    "prose) + all 11 result tables wired via \\input{_tables_from_bible.tex} after the bibliography; compiles clean "
    "(22pp, 0 errors, 0 undefined refs/cites). Table 1 = whole-thesis ALL-UNIVERSE summary stats (23 vars, "
    "docs/Draft/generate_summary_stats.py, per-variable Main-sample); Tables 2-11 = empire run-up/drop/placebo/cashspec "
    "+ convergent h11/h24/h24b + scrutiny validity/channel/reason-gating (the LOCKED 11-table set; "
    "competition/bid-ask(h14c)/SEC(h18)/cash-holdings-moderators(h1,h1.2,h1.3)/Brexit/Boasiako all DROPPED). 2 widest "
    "tables landscape (pdflscape); rest adjustbox max width=\\linewidth. §2 prose carries 5 table refs (summary_stats=Tab1 "
    "in 2.5 P5; convergent=Tab6/7/8 in 2.5 P2; cash_scrutiny_validity=Tab9 in 2.5 P4). FB filled in 2.5 P2 (1-SD -> "
    "~5%/1.5%/2.2% of residual SD; beta x Table-1 SD / Table-1 SD, reconciles with printed coefs). Programmatic "
    "ledger->.tex throughout. §3/§4/§5/abstract/intro/appendix NOT yet written.")

r["files_of_record"]["the_draft"] = ("docs/Thesis/thesis_draft.tex -- FULL §2 (2.1-2.5 prose, all ratified provisional) "
    "+ all 11 result tables \\input via _tables_from_bible.tex after the bibliography; ~22pp, compiles clean (0 errors, "
    "0 undefined refs). Locate subsections by \\subsection HEADING, tables by \\label{tab:...}. Preamble adds "
    "longtable/adjustbox/pdflscape. Tables are byte-exact-content from the bible, assembled by tmp/extract_draft_tables.py "
    "(explicit THESIS_TABLES order, 2 widest landscape). Full prior draft (abstract/intro/§3-5/appendices) recoverable at "
    "commit 81efc78; §3/§4/§5 NOT yet rewritten. P7 (~L43 region) still carries the scrutiny-reframe TODO comment.")

r["NEXT_ACTION"] = ("=== §2 prose RATIFIED (provisional, user 'consider everything ratified for now' 2026-06-14) + Table 1 "
    "built + all 11 tables wired + 5 §2 refs + FB filled, ALL COMMITTED (a65872f). OPEN ITEMS (none blocking; await user "
    "direction): (1) APPENDIX -- §2.5 P4/P5 say 'in the Appendix' but NO Appendix exists yet; build it (the CashScrutiny "
    "cash/liquidity WORD LIST, which currently rides on Table 9's construction page, + the controls catalogue). (2) 2.1-P7 "
    "softening: cut 'and we do not try', keep 'Our design cannot distinguish them.', remove the P7 TODO comment (~L43). "
    "(3) The 6 RESULT tables (empire run-up/drop/placebo/cashspec, reason_gating, cash_scrutiny_channel) are INCLUDED but "
    "UNREFERENCED in prose -- add refs when §3/§4 results prose is written. (4) whole-§2 coherence pass, then write "
    "§3/§4/§5/abstract/intro. DISCIPLINE (unchanged): programmatic ledger->.tex w/ drift+dash+no-competition guards; numbers "
    "from regression tables (summary stats now BUILT all-universe in docs/Draft/summary_stats.csv); tables byte-exact via "
    "tmp/extract_draft_tables.py; NLM sole paper authority; no '---'/'--'; hypotheses set off; SHOW/ratify in PDF.")

s = r["prose_progress_2026_06_13"]["status"]
s["2.3 (whole)"] = "RATIFIED 2026-06-14 (provisional, user). In thesis_draft.tex; DWZ eq (2)/(4)/(5) natbib-cited; dash-free."
s["2.4 (whole)"] = "RATIFIED 2026-06-14 (provisional, user). In thesis_draft.tex; 3 estimating eqs; never-acquirer FE-anchor; dash-free."
s["2.5 (whole)"] = ("RATIFIED 2026-06-14 (provisional, user). Competition DROPPED; P1/P2/P4/P5; 5 table refs added "
    "(summary_stats P5, h11/h24/h24b P2, cash_scrutiny_validity P4); FB FILLED in P2 (~5%/1.5%/2.2% of residual SD). In PDF.")

pa = r.get("subsection_loop_workflow_2026_06_13", {}).get("phase_A_owed_by_subsection", {})
if "2.5" in pa:
    pa["2.5"] = "[2026-06-14 DONE] 2.5 ratified (provisional); FB filled; table refs added. No remaining 2.5 owed."

open(RS, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
json.load(open(RS, encoding="utf-8"))  # validate
print("OK: 2.3/2.4/2.5 ledgers RATIFIED (provisional) + resume swept to current reality. All JSON valid.")
