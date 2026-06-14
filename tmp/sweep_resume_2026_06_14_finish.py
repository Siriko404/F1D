# Compaction sweep: bring _RESUME_STATE.json to current reality after the §2-finishing session
# (Keown bib fix, Appendix I, P7 softening, brutal coherence pass). JSON-key edits (no raw-text
# escaping pitfalls); fail-closed (json.load validates at end). CORRECTS the false "5 cites already
# in prose+bibliography" note that caused today's alarm.
import json
import pathlib

RS = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\_RESUME_STATE.json")
r = json.loads(RS.read_text(encoding="utf-8"))

r["updated"] = ("2026-06-14 (§2 FINISHED + provisionally ratified + COHERENCE-PASSED. This session, after "
    "a65872f: Keown bibitem initials fixed via NLM identity (6ac361bc); Appendix I = cash-scrutiny word "
    "list relocated + 2.1-P7 softened (28eb95a3); brutal §2 coherence pass -- 5 fixes + ledger hygiene "
    "(1e330865) + Table-1 PRisk note rendered, numbers verified unchanged (cabc4f45). thesis_draft.tex "
    "compiles clean (23pp, 0 errors/0 undefined). Latest commit cabc4f45. NEXT: user's final §2 PDF read, "
    "then §3/§4 proposition planning. See SESSION_2026_06_14_section2_finish + NEXT_ACTION.)")

r["where_we_are"] = ("[2026-06-14] §2 COMPLETE + provisionally ratified + COHERENCE-PASSED. thesis_draft.tex "
    "= full §2 (2.1-2.5 prose) + all 11 result tables (\\input _tables_from_bible.tex after the bibliography) "
    "+ Appendix I (cash-scrutiny word list; standalone editable appendix_I_cash_scrutiny.tex, FLAGGED for "
    "pending user edits). Compiles clean (23pp, 0 errors/0 undefined). Table 1 = all-universe summary stats "
    "(23 vars) + a note that PRisk is Hassan's scaled index (not a percentage). §2-finishing work this "
    "session: (a) Keown initials A.~J./J.~M. via NLM S4 identity -> section2.1 ledger bib_identity; (b) "
    "Appendix I decoupled from the bible (extract_draft_tables.py truncates the construction page out of the "
    "validity fragment); (c) 2.1-P7 'and we do not try' cut + TODO removed; (d) coherence fixes: sCFO->'cash-"
    "flow volatility', PRisk gloss->'scaled measure', US-EPU FE-disclosure clause, 2.5-P1 'uncertainty and "
    "risk', 2.5-P4 'Appendix~I', 2.5-P5 catalogue-promise softened, 2.1 ledger P3-P7 status->provisional-"
    "ratified. 4 flagged issues verified NON-issues (Hollander/Thewissen/DWZ-eqs/H1b). Findings: "
    "tmp/coherence_2_findings.md. §3/§4/§5/abstract/intro NOT yet written.")

r["NEXT_ACTION"] = ("=== §2 DONE + provisionally ratified + coherence-passed (committed through cabc4f45). "
    "IMMEDIATE: user is doing a final read of the assembled §2 PDF (opened) -- await sign-off, THEN §3/§4 "
    "proposition planning. OPEN ITEMS (deferred, none blocking): (1) CONTROLS CATALOGUE (Appendix II): §2.5 P5 "
    "was softened so it no longer dangles, but the catalogue (incl. the 4 DWZ first-stage controls StockRet/"
    "MarketRet/EPSgrowth/SurpDec) is NOT built -- build via docs/Draft/generate_var_defs_appendix.py RESCOPED "
    "to the locked 11-table suites (it currently targets the OLD 12-suite roster). (2) F: h24/h24b carry "
    "Lagged_DV but h11 does not -- table-design diff, intent UNCONFIRMED; resolve (table note or harmonize) "
    "when §3/§4 discuss these tables. (3) 6 RESULT-table refs (empire run-up/drop/placebo/cashspec, "
    "reason_gating, cash_scrutiny_channel) INCLUDED but UNREFERENCED -- add when §3/§4 results prose is "
    "written. (4) CITATION METADATA: only keown1981 was NLM-identity-checked this session (user scope); the "
    "other ~15 bib entries' CONTENT is NLM-verified (section2.1 ledger + nlm_validity_definitions.json) but "
    "typed vol/pages were NOT re-identity-checked -- optional pre-submission. (5) write §3/§4/§5/abstract/"
    "intro. DISCIPLINE unchanged: programmatic ledger<->tex drift-guarded (JSON-aware); NLM sole paper "
    "authority; no '---'/'--'; hypotheses set off; numbers from regression tables; SHOW/ratify in PDF.")

r["files_of_record"]["the_draft"] = ("docs/Thesis/thesis_draft.tex -- FULL §2 (2.1-2.5 prose, provisionally "
    "ratified + coherence-passed) + all 11 result tables \\input via _tables_from_bible.tex after the "
    "bibliography + Appendix I (\\input appendix_I_cash_scrutiny.tex; cash-scrutiny word list, FLAGGED for user "
    "edits). 23pp, compiles clean (0 errors, 0 undefined). [2026-06-14] 2.1-P7 TODO REMOVED + softened. Locate "
    "subsections by \\subsection HEADING, tables by \\label{tab:...}. Preamble adds longtable/adjustbox/"
    "pdflscape. Tables byte-exact from the bible via tmp/extract_draft_tables.py (explicit THESIS_TABLES order; "
    "the validity fragment's construction page is TRUNCATED out -> it now lives in Appendix I). Full prior "
    "draft (abstract/intro/§3-5) recoverable at commit 81efc78; §3/§4/§5 NOT yet rewritten.")

# CRITICAL correction: the false "5 cites already in prose + bibliography" claim.
pe = r["PENDING_EDITS_unapplied"]
pe["_note"] = ("[2026-06-14 CORRECTED -- read FIRST] The 5 names pagan1984 / opler1999 / bates2009 / "
    "petersen2009 / cameron2011 are NOT in the draft -- VERIFIED 2026-06-14 (tmp/verify_cites.py: 16 cited "
    "keys, ALL resolve to bibitems, 0 undefined; these 5 absent from BOTH prose and bibliography). The earlier "
    "wording that they were 'already in the prose + bibliography' was WRONG and triggered a false alarm; they "
    "were forward-looking 'maybe cite for methods' flags, never added (the WRITE_TIME_FLAGS below correctly say "
    "OMITTED/DROPPED). If a methods cite is wanted later: NLM-verify + add bibitem. SEPARATELY: keown1981 "
    "initials were FIXED this session via NLM S4 identity (section2.1 ledger bib_identity.keown1981). ALL 20 "
    "bib entries' CONTENT is NLM-verified (section2.1 ledger + nlm_validity_definitions.json); only keown's "
    "typed metadata was re-identity-checked (others optional pre-submission). " + pe["_note"])

r["section_2_1_paragraphs"]["_status"] = ("[2026-06-14] ALL P1-P7 LOCKED as PROSE in thesis_draft.tex. P7 "
    "softening DONE (cut 'and we do not try'; kept 'Our design cannot distinguish them.'; TODO comment "
    "removed). 2.1 ledger P3-P7 prose_status flipped DRAFTED -> provisional-ratified (P1/P2 stay APPROVED). "
    "Keown initials fixed (bib_identity). NO pending 2.1 changes. The per-paragraph notes below are HISTORICAL "
    "plan rationale.")

# Mark the stale 'push deferred / .tex 2.1-only' notes DONE (the push happened; full §2 in .tex).
r["prose_progress_2026_06_13"]["tex_push_deferred"] = ("[2026-06-14 DONE] The .tex push COMPLETED -- full §2 "
    "(2.1-2.5) is in thesis_draft.tex (NOT 2.1-only). The 2.1-P7 softening rode along and is applied; the TODO "
    "comment is removed. Coherence pass + Appendix I also landed. Historical instruction kept below for context.")
r["subsection_loop_workflow_2026_06_13"]["first_tex_push_baggage"] = ("[2026-06-14 DONE] Push completed; "
    "2.1-P7 softening applied (TODO removed); Appendix I added; all \\bibitems present (0 undefined). "
    "Historical note retained below.")

# Defensive: mark the historical scrutiny-reframe P7 change-list item DONE if present.
try:
    cl = r["scrutiny_reframe_DECIDED_2026_06_13"]["change_list"]
    k = "section2.1 P7 (thesis_draft.tex ~L67, LOCKED prose)"
    if k in cl and not str(cl[k]).startswith("[2026-06-14 DONE]"):
        cl[k] = "[2026-06-14 DONE] applied (cut 'and we do not try'; kept 'cannot distinguish'; TODO removed). " + cl[k]
except Exception:
    pass

# New durable record of this session's work.
r["SESSION_2026_06_14_section2_finish"] = {
    "_what": "§2-finishing session (after a65872f). ALL COMMITTED. Latest = cabc4f45.",
    "keown_bib_fix": "bibitem keown1981 -> 'Keown, A.~J., and J.~M. Pinkerton' recovered via NLM S4 identity "
        "(docs/Thesis/rewrite/nlm_bib_identity.py -> section2.1 ledger bib_identity.keown1981, verdict "
        "SUPPORTED). Commit 6ac361bc.",
    "appendix_I": "Cash-Scrutiny Variable Construction (Link 1) RELOCATED mid-draft -> standalone "
        "docs/Thesis/appendix_I_cash_scrutiny.tex (Appendix I), DECOUPLED from the bible "
        "(extract_draft_tables.py truncates the construction page out of _cash_scrutiny_validity.tex). FLAGGED "
        "pending user edits. Commit 28eb95a3.",
    "p7_softening": "2.1-P7 'and we do not try' CUT (kept 'Our design cannot distinguish them.') + TODO removed. "
        "Commit 28eb95a3.",
    "coherence_pass": "Brutal §2 coherence pass (advisor-hardened, verify-first). 5 fixes: A sCFO->'cash-flow "
        "volatility' (5-yr rolling SD oancf/atq; biddle2009/ocf_volatility.py); B PRisk gloss->'scaled measure "
        "of the share...' + Table-1 scaling note (rendered, numbers verified unchanged); E US-EPU industry-FE "
        "disclosure clause (firm-FE marginal p<.10); H 2.5-P1 'uncertainty and risk'; I 2.5-P4 'Appendix~I'; G "
        "2.5-P5 catalogue-promise softened. J: 2.1 ledger P3-P7 status->provisional-ratified. Commits 1e330865 "
        "+ cabc4f45. NON-issues verified (NO fix): D Hollander '6 of 10' (verbatim span n2); F Lagged_DV "
        "(table-design diff, not §2 prose; intent unconfirmed->§3/§4); K H1b theta_gap=0 (standard predicted "
        "value; §2.4 tests the drop); L Thewissen (stock-for-stock confirmed via spans n2/n3/n6); N DWZ eq "
        "(2)=ratio/(4)=decomposition/(5)=market-response, verified VERBATIM in tmp/nlm_dwz_equations.json. "
        "Findings record: tmp/coherence_2_findings.md.",
    "deferred": "See NEXT_ACTION items 1-4: controls catalogue (Appendix II), F lagged-DV intent, 6 result-"
        "table refs, other-15 citation metadata identity.",
    "edit_scripts": "tmp/edit_sCFO_label.py, edit_prisk_gloss.py, fix_prisk_ledger_drift.py (JSON-escape drift "
        "fix), edit_E_fe_disclosure.py, edit_coherence_HIGJ.py; verify: verify_cites.py, audit_nlm_ledger.py, "
        "verify_2_numbers.py, verify_remaining.py. All committed.",
}

RS.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
json.loads(RS.read_text(encoding="utf-8"))  # fail-closed validation
print("OK: resume swept to 2026-06-14 §2-finish reality; false cite-note CORRECTED; JSON valid.")
