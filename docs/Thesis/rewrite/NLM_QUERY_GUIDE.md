# NLM Query Guide — hard-won rules (READ before any NLM verification)

Caveman lite. These rules paid in blood (2026-06-12). Follow exactly. Skip one → redo everything.

## 0. CORE PRINCIPLE
ONE durable, committed script does it ALL: **query NLM → write answer DIRECTLY into the JSON ledger → `git commit`.** One pass.
- NEVER ad-hoc bash/python one-liners to gather or parse NLM data. Script only.
- NEVER hand-edit the ledger with NLM data. The script writes it + commits it.
- NEVER read a PDF or `source fulltext` to get content/pages. OUT OF CHANNEL. NLM is the SOLE paper authority.

## 1. CLI CHEAT
```
notebooklm source list -n <NB> --json        # sources: {id, title}. titles = opaque filenames.
notebooklm clear                              # best-effort ONLY — does NOT reliably reset conversation
notebooklm ask -n <NB> -s <SOURCE_ID> --json "<query>"
```
`ask --json` → `{answer, references:[{source_id, citation_number, cited_text, start_char, end_char, chunk_id}]}`.
- NB (this project) = `63e3b970-7976-47bc-8291-37ce7ac9bf74`.
- Retry the ask ONCE on timeout/error (NLM chat times out sometimes).
- Windows: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` — titles carry U+2010.
- **ISOLATION (clear is a LIE)**: same `conversation_id` + `is_follow_up:true` persist across asks AND sessions — `clear` does NOT mint a fresh conversation, so prior Q&A CAN bleed. REAL isolation = `-s` (one source) + naming the paper in every query (self-contained). `ask --help` text mentions `--new` but it is NOT in the options list — UNVERIFIED, test before trusting. Until then: every query MUST stand alone.

## 2. ADDRESSING PAPERS (the ID fight)
- Address paper in the QUERY by **TITLE + AUTHOR + YEAR**. Human key = title/author/year, NEVER the NLM id.
- BUT `-s` needs the source_id (UUID). Resolve it **inside the script at runtime**: match a durable title-substring (e.g. ScienceDirect PII `0165410183900113`, or `dye-disclosurenonproprietary`) against `source list`. ID is transient (for `-s` only).
- Belt + suspenders: `-s <id>` (hard single-source scope) AND name the paper in the query text. Both.
- If a match is AMBIGUOUS (duplicate uploads) → take newest, warn.

## 3. QUERY RULES (E3–E6)
- **Atomic**: ONE checkable proposition per query.
- **Self-contained**: start `"Reading only this paper, "<Title>" by <Author> (<Year>): "`.
- **Non-leading / exploratory**: "what does it conclude about X?" — NEVER "confirm X".
- **Clear** before each ask. **Name** the paper exactly.

## 4. EVIDENCE RULES
- ONLY admissible verbatim = structured `references[].cited_text` (NLM extraction spans). NOT the answer prose.
- `cited_text` can be null → skip it.
- Spans carry OCR garble ("nonpro- prietary", `y"= y`). Fine for paraphrase + (author, year). Clean ONLY if you drop a *direct* quote into the thesis.

## 5. PAGE + SECTION (the trap)
- Structured refs have NO page. Only cited_text + char-offset + chunk_id.
- Get page+section by ASKING NLM in the query: *"for each sentence you quote, report the exact page printed in the paper and the section (heading/number)."* NEVER derive page from offsets/fulltext.
- **GOTCHA**: NLM's answer-quotes (paged) often DON'T match its structured citation spans. So a parsed page attaches to an answer-reproduced sentence, not the verbatim span.
- **MANDATORY POST-CAPTURE AUDIT** (the self-check that stops a false "done"): after EVERY capture, test each `located` (answer) quote for substring-membership in a structured `cited_text` span. The match-rate IS your verbatim-confidence. 100% = solid. <100% ⇒ those pages are ANSWER-ONLY (verbatim unconfirmed) ⇒ pin or distrust. (This session: P1.1 = 2/4, P1.2 = 0/7. The 0/7 is what nearly shipped as "done".)
- **PAIRING / PIN** (router by the audit):
  1. Located quote IS a substring of a span → verbatim+page CONFIRMED. zero extra calls.
  2. No match → ONE targeted **page-pin** call: feed the decisive span's distinctive phrase, ask its page+section. Pins page onto the guaranteed-verbatim text.
- **Page = whatever NLM REPORTS** — cannot confirm out-of-channel; NLM page index has been wrong before ("page 3000"). **Section is NOT an independent check** — page+section come from the SAME answer-generation, so NLM can mislocate both together. The ONLY independent checks: (a) `cited_text` exists = verbatim guaranteed; (b) page is in the journal's real range. Section helps localize, but never call it confirmation.

## 6. PARSE GOTCHAS
- Embedded straight-quote `"` inside a sentence (`y"=y`) truncates a `"([^"]+)"` capture. Expect truncation; pin from the structured span instead.
- Page regex: anchor to end-of-line `\*\*Page:\*\*[ \t]*([^\n]+)`. NON-greedy `+?` grabbed only "1" of "182". Don't.
- Pinned page/section strings may carry NLM inline markers ("129 [1, 2]") — strip if needed.

## 7. VERDICT (human, not the script)
- Script captures evidence. YOU adjudicate verdict on the verbatim spans. Script may RECORD the verdict you supply (+commit), never decide it.
- Enum: `PENDING / SUPPORTED / OVERCLAIM / UNSUPPORTED / INCONCLUSIVE_MANUAL`.
- Verdict note must NAME the supporting spans (e.g. "n=5/n=8: ...").

## 8. LEGAL / NON-PAPER SOURCES
- "Verify ONLY thru NLM" applies to them too. UPLOAD the legal source (case opinion, CFR rule) to the notebook, query via NLM like a paper. NEVER verify via web/legal-text out of channel.

## 9. LEDGER SHAPE (what the script writes per prop)
```
verification = {
  method, source:{id,title}, query, answer,
  quotes:   [{n, cited_text, start_char, end_char, chunk_id}],   # verbatim spans
  located:  [{quote, page, section}],                            # from answer (page+section)
  span_pin: {phrase, page, section},                             # only if router found no match
  verdict, verdict_note
}
```

## 10. QUOTA + WORKFLOW
- NLM calls precious (~2/paper norm, flex to 3). Don't sweep.
- **Resumable**: skip a prop that already has `quotes`. Never re-run a captured content query.
- Page-pin = 1 targeted call, not a re-query.
- One paragraph at a time. Verify-first (no prose till all props SUPPORTED + recorded). Show-first (paragraph to user before draft).

## 11. NEVER (the scars)
- NEVER ad-hoc data gathering/parsing outside the script.
- NEVER `source fulltext`/PDF to derive pages or content.
- NEVER hardcode the NLM id as the human key.
- NEVER hand-edit NLM data into the ledger.
- NEVER trust answer-prose as verbatim — only structured cited_text.
- NEVER re-run content queries (quota).
- NEVER stop-and-poll every micro-step — deliver the result.

## 12. SCRIPT SKELETON (the proven pattern — copy from `nlm_p1.py`)
```python
NB = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
PREFIX = "Reading only this paper, "
LOCATOR = (" For each sentence you quote in support, report the exact page number "
           "printed in the paper and the section (heading or number) where it appears.")
# prop_id -> (paper named in query, durable title-substring, atomic non-leading question)

def run(args, t): return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                                        encoding="utf-8", errors="replace", timeout=t)
def source_id(match):                      # resolve id at runtime by title substring
    src = json.loads(run([EXE,"source","list","-n",NB,"--json"],120).stdout.split("{",1)[1].join(["{",""]))
    # (in practice: find first source whose title contains `match`; return id,title)
def ask(sid, paper, q):                    # -s scopes to ONE source; name paper in query
    run([EXE,"clear"],60)                  # best-effort only
    full = f"{PREFIX}{paper}: {q}{LOCATOR}"
    out = run([EXE,"ask","-n",NB,"-s",sid,"--json",full],420).stdout
    return full, json.loads(out[out.find("{"):])     # retry once on error/timeout
# per prop: ask -> write verification{method,source,query,answer,
#   quotes:[{n,cited_text,start_char,end_char,chunk_id}], located:[{quote,page,section}]}
#   -> json.dump ledger -> git add ledger+script -> git commit. ONE prop per commit.
# finalize(): substring-audit; pin unmatched decisive spans (1 call); record verdicts.
```
Full working version: `docs/Thesis/rewrite/nlm_p1.py` (run `--finalize` for pin + verdicts).
