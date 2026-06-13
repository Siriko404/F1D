# NLM Query Guide — hard-won rules (READ before any NLM verification)

Caveman lite. These rules paid in blood. Follow exactly. Skip one → redo everything.

> **THE HEADLINE SCAR (2026-06-13):** a notebook filename is an OPAQUE label, **NEVER the paper's identity.**
> Decoding a filename from your own knowledge — "`qjw024.pdf` is the DOI suffix for Baker-Bloom-Davis", "`w22740` is NBER → Davis" — is a FABRICATION and is FORBIDDEN. The only way to know which file is which paper is to **ask NLM** (identity query, §4). This rule cost a furious correction. Internalize it.

## 0. CORE PRINCIPLE
ONE durable, committed script does it ALL: **resolve source id → query NLM → write answer DIRECTLY into the JSON ledger → `git commit`.** One pass.
- NEVER ad-hoc bash/python to gather or parse NLM answer/content data. Script only. (Listing source titles to pick a candidate match-token is fine — that's string-finding; but a title NEVER establishes identity — §4. Eyeballing titles to *decide which paper a file is* is the exact move that caused the scar.)
- NEVER hand-edit the ledger with NLM data. The script writes it + commits it.
- NEVER read a PDF or `source fulltext` to get content/pages. OUT OF CHANNEL. NLM is the SOLE paper authority.
- NEVER infer a paper's identity from its filename. Identity comes from NLM (§4), not from you.

## 1. CLI CHEAT
```
notebooklm source list -n <NB> --json        # sources: {id, title, created_at}. titles = opaque filenames.
notebooklm clear                              # best-effort ONLY — does NOT reliably reset conversation
notebooklm ask -n <NB> -s <SOURCE_ID> --json "<query>"   # -s = scope to one source (content extraction)
notebooklm clear; notebooklm ask -n <NB> --json "<query>"   # NO -s = search ALL sources -> DISCOVER by content (§3a)
                                              #   (this build has NO --new flag; `clear` first = best-effort isolation)
notebooklm login                              # interactive (browser). AUTH EXPIRES — when source list returns
                                              #   {"error": "...Authentication expired..."}, the USER must run it.
```
`ask --json` → `{answer, references:[{source_id, citation_number, cited_text, start_char, end_char, chunk_id}]}`.
- NB (this project) = `63e3b970-7976-47bc-8291-37ce7ac9bf74`.
- Retry the ask ONCE on timeout/error (NLM chat times out sometimes).
- Windows: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` — titles carry U+2010.
- **ISOLATION**: `--new` is NOT a real option in this CLI build — the `ask --help` *prose* says "Use --new to start fresh" but the options list omits it and passing it errors (`No such option: --new`, rc=2, VERIFIED 2026-06-13). **Do not trust help prose; test a flag before relying on it.** So isolation = `clear` (best-effort ONLY — `conversation_id`/`is_follow_up` can still bleed across asks) + naming the paper self-contained in EVERY query. For discovery, **omit `-s` to search ALL sources** (§3a); add `-s` to scope to one source for extraction.

## 2. ADDRESSING PAPERS — the human key
- Address the paper IN THE QUERY by **TITLE + AUTHOR + YEAR (+ journal/series)**. Human key = title/author/year, **NEVER the NLM id, NEVER the filename.**
- Pull the title/author/year from **our own bib** (`thesis_draft.tex` `\bibitem`s), not from memory.
- Belt + suspenders: scope `-s <id>` (hard single-source) AND name the paper in the query text. Both, every time.

## 3. RESOLVING THE SOURCE_ID — the registry + fail-closed
`-s` needs the UUID. Resolve it **inside the script at runtime**. The id is transient (for `-s` only); never hardcode it as the human key. **TWO ways to get it — prefer discovery (3a) whenever the filename is opaque.**

### 3a. DISCOVER the id by CONTENT — the unbiased default (when you have NO known-good token)
If you don't have a token you KNOW belongs to the paper (i.e. the filename is an opaque publisher code), do **NOT** pick candidate substrings off the filenames — that is filename-bias one level up: it can miss the paper entirely or check the wrong file. Make **NLM discover it by content**:
- Run an **unscoped** ask (NO `-s`; `clear` first for best-effort isolation) that NAMES the paper by title+author+year (from the bib) and asks a paper-specific question.
- NLM searches ALL sources; `references[].source_id` = the source that actually CONTAINS that paper = the id, found by content, zero filename bias.
- VERIFY: references should cohere to ONE source_id and its `cited_text` should be the paper's own content. >1 distinct source_id or off-topic spans ⇒ ambiguous → tighten the query and/or identity-confirm (§4). No relevant source ⇒ the paper is **NOT in the notebook** → tell the user to upload it.
- One unscoped query both DISCOVERS the id and CAPTURES content. Scope follow-ups with `-s <discovered id>`.

### 3b. The registry shortcut — ONLY for known-named files
A title-substring token (below) is a shortcut, valid ONLY when the notebook title genuinely contains author/title words you KNOW are the paper's (e.g. the 2.1 uploads: "harford - corporate cash reserves"). NEVER fabricate a token from a publisher code to assert identity.

Three matcher shapes (use the weakest that is safe):
| shape | when | example |
|---|---|---|
| `{"token": <substr>}` | a durable substring is KNOWN to be in the title | `"harford - corporate cash reserves"`, `"loughran - when is a liability"`, `"dzielinski et al. - straight talkers"`, PII `"s0024630123001000"`, SSRN `"4900453"`, `"118-4-1169"` |
| `{"token":…, "dup":"newest"}` | >1 title matches (duplicate upload) | take newest by `created_at` + **WARN** |
| `{"id": <uuid>}` | OPAQUE/duplicated filename **no** substring can safely select | Matsumoto = `EBSCO-FullText-06_12_2026.pdf` (uploaded twice). **id MUST be identity-verified first — §4** |

- **`source_id_multi([candidates])`**: when unsure which fragment is in the title, give an ORDERED list of candidate substrings; first hit wins (legal: `["485224","usrep485","levinson","basic inc"]`; lm2011: `["loughran","liability not a liability","when is a liability",…]`). Candidates are guesses at what string is IN the title — **NOT** assertions of identity.
- **FAIL CLOSED**: resolve everything in ONE `source list` call, BEFORE any content query. `0 matches` or `>1 without a dup policy` = **HARD EXIT naming the paper**. Never guess; never spend quota on an unresolved/ambiguous source.
- A token being present in a filename (e.g. `qjz021`) lets you *find* the source. It does **NOT** tell you the source IS Hassan et al. — that requires §4.

## 4. ⛔ IDENTITY — a filename is NEVER the paper (the scar)
Publisher codes — DOI suffix `qjw024`, PII `S0165…`, NBER `w22740`, JPE number `688176.pdf`, EBSCO `EBSCO-FullText-….pdf` — are OPAQUE. You may use them as match *tokens* (§3). You may **NEVER conclude "this code = that paper" from your own knowledge of numbering/DOI conventions.** That is decoding-from-memory = fabrication = forbidden.

**For ANY opaque / duplicated / `{"id"}` / uncertain source, identity-confirm via NLM BEFORE spending content quota.** Run the `--identity` mode — it asks the source to state ITS OWN identity, non-leading:
```
Reading only this paper, this source: state ONLY the exact title, the authors, the journal or
working-paper series, and the year of this document. Do not infer beyond what the document states.
```
Only when the source **self-reports the expected title/author/year** do you (a) pin its id as `{"id":…}`, (b) proceed to content.

- **Precedent (do this):** Matsumoto P2.1 — opaque, duplicated EBSCO filename, no substring resolved it → id pinned ONLY after an identity query confirmed "Matsumoto, Pronk & Roelofsen (2011), The Accounting Review." Took the newest of the two copies.
- If identity **can't** be confirmed (self-report doesn't match, or the paper simply isn't in the notebook) → **STOP, tell the user, ask them to upload it.** Never substitute a guess, never query a different file "close enough."
- `--identity` is a cheap 1-call/source check and is SEPARATE from the ~2/paper content quota. When in any doubt, run it.
- **Best avoidance of the scar:** with no known-good token, do NOT identity-check filename *guesses* — DISCOVER by content (§3a); the discovery references already tell you the id. Identity-confirm is for verifying a token/`{id}` match you already have.

## 5. QUERY RULES (E3–E6)
- **Atomic**: ONE checkable proposition per query.
- **Self-contained**: start `"Reading only this paper, "<Title>" by <Author> (<Year>): "`.
- **Non-leading / exploratory**: "what does it conclude about X?" / "how is X defined and at what frequency is it computed?" — **NEVER** "confirm X", never embed the answer you want.
- **Clear** before each ask. **Name** the paper exactly.
- **framing-nonverifiable** props (e.g. "to our knowledge no prior work…") are NOT queried — you cannot prove a negative. Mark and skip.

## 6. EVIDENCE RULES
- ONLY admissible verbatim = structured `references[].cited_text` (NLM extraction spans). NOT the answer prose.
- `cited_text` can be null → skip it.
- Spans carry OCR garble ("nonpro- prietary", `y"= y`). Fine for paraphrase + (author, year). Clean ONLY if you drop a *direct* quote into the thesis.
- **When a PDF chunks badly** (no single clean span carries the claim — e.g. DWZ): build a CONVERGENT basis — reproduce the decisive sentence VERBATIM across TWO independent queries (`--requery`, §13) + round-trip pin it (§7). Record the convergent basis in the verdict note. Do NOT upgrade an answer-only claim to "verbatim".

## 7. PAGE + SECTION (the trap) + the mandatory audit
- Structured refs have NO page. Only `cited_text` + char-offset + chunk_id.
- Get page+section by ASKING NLM in the query (the LOCATOR clause): *"for each sentence you quote, report the exact page printed in the paper and the section (heading/number)."* NEVER derive page from offsets/fulltext.
- **GOTCHA**: NLM's answer-quotes (paged) often DON'T match its structured citation spans. A parsed page attaches to an answer-reproduced sentence, not the verbatim span.
- **MANDATORY POST-CAPTURE AUDIT** (`--audit`): after EVERY capture, test each `located` (answer) quote for substring-membership in a structured `cited_text` span. Match-rate = verbatim-confidence. 100% = solid. <100% ⇒ those pages are ANSWER-ONLY (verbatim unconfirmed) ⇒ pin or distrust. (Scar: P1.2 audited 0/7 — that 0/7 nearly shipped as "done".) NB: the audit UNDERSTATES strength when a verbatim span is ITSELF decisive (then read the span directly; no located round-trip needed).
- **PIN router** (driven by the audit):
  1. Located quote IS a substring of a span → verbatim+page CONFIRMED. zero extra calls.
  2. No match → ONE targeted **page-pin** call: feed the decisive span's distinctive phrase, ask its page+section. Pins page onto the guaranteed-verbatim text.
- **Page = whatever NLM REPORTS** — cannot confirm out-of-channel; NLM's page index has been wrong ("page 3000"). The ONLY independent checks: (a) `cited_text` exists = verbatim guaranteed; (b) page is in the journal's real range. **Section is NOT an independent check** — page+section come from the same answer-generation; NLM can mislocate both together.

## 8. PARSE GOTCHAS
- Embedded straight-quote `"` inside a sentence (`y"=y`) truncates a `"([^"]+)"` capture. Expect truncation; pin from the structured span instead.
- Page regex: anchor to end-of-line `\*\*Page:\*\*[ \t]*([^\n]+)`. NON-greedy `+?` grabbed only "1" of "182". Don't.
- Pinned page/section strings may carry NLM inline markers ("129 [1, 2]") — strip if needed.

## 9. VERDICT (human, not the script)
- Script captures evidence. YOU adjudicate the verdict on the verbatim spans. Script may RECORD the verdict you supply (+commit), never decide it.
- Enum: `PENDING / SUPPORTED / OVERCLAIM / UNSUPPORTED / INCONCLUSIVE_MANUAL`.
- Verdict note must NAME the supporting spans (e.g. "verbatim span n=5/n=8: …").
- **GATING vs NON-GATING**: a prop can be verified NOW but belong to a LATER section's prose. Tag it NON-GATING and do NOT draft it into the current paragraph. (Scar: DWZ price-null P4.3 — captured for §2.3/§3, verdict says "Do NOT draft into P4".)
- **Provisional (not evidence-locked)**: if the basis is answer-only / fragments (no clean `cited_text` span), the verdict is SUPPORTED-but-provisional — re-verify with a clean span (`--requery`, §13) before it is drafted into its home section.

## 10. LEGAL / NON-PAPER SOURCES
- "Verify ONLY thru NLM" applies to them too. UPLOAD the legal source (case opinion, CFR rule) to the notebook, query via NLM like a paper. NEVER verify via web/legal-text out of channel.
- Resolve with `source_id_multi` candidate lists; name the document precisely in the query. Ledger holds them under `verification.parts[]` (one part per sub-source), then `span_pins[]` + verdict.

## 11. LEDGER SHAPE (what the script writes)
```
ledger.resolved_sources = { paper_key: {status, source_id, source_title} }   # persisted by capture()
prop.verification = {
  method, source:{id,title}, query, answer,
  quotes:    [{n, cited_text, start_char, end_char, chunk_id}],   # verbatim spans (admissible)
  located:   [{quote, page, section}],                            # from answer (page+section)
  span_pins: [{phrase, page, section, query, answer}],            # router found no match → pinned
  requery:   [{query, answer, quotes}],                           # §13, appended; never overwrites
  parts:     [...],                                               # legal/multi-source only
  verdict, verdict_note
}
```

## 12. QUOTA + WORKFLOW ORDER
- NLM content calls precious (~2/paper norm, flex to 3). Don't sweep. `--identity` and one `page-pin` are cheap, separate from content quota.
- **Resumable**: skip a prop/query that already has `quotes`. NEVER re-run a captured content query.
- **One paragraph at a time. Verify-first** (no prose until all props SUPPORTED + recorded). **Show-first** (paragraph to user before draft).
- The order, every unit:
  1. Plan props/queries (atomic, non-leading, self-contained; name paper by title/author/year from the bib).
  2. RESOLVE source ids — fail-closed, one `source list` (§3).
  3. **IDENTITY-confirm** opaque/dup/uncertain sources (§4) — before content quota.
  4. CONTENT capture — scoped, named, + LOCATOR; one commit per query; resumable.
  5. AUDIT (substring) → verbatim-confidence (§7).
  6. PIN decisive spans lacking a page (round-trip).
  7. VERDICT (human; only `cited_text` admissible; note names spans).
  8. After drafting: accuracy pass on every UNCITED connective claim (§17).

## 13. THE ENGINE + PER-PAPER SCRIPT + MODES
`nlm_common.py` = the durable engine (import it; don't re-implement):
- `resolve_all` / `require` — fail-closed resolver; `require` prints the map and `sys.exit`s on any problem (no quota spent). `python nlm_common.py` = **self-test**: resolves every registered paper, exits nonzero on any miss/ambiguity, zero content calls. Run it after editing `SOURCES`.
- `ask(sid, paper, q)` — scoped, names the paper, appends LOCATOR, retries once.
- `identity(keys)` — §4 self-identity query, 1 call/source.
- `capture(para, props)` — resolve (fail-closed) → persist `resolved_sources` → per-prop ask → write verification → commit. Resumable.
- `finalize(para, pins, verdicts)` — pin decisive spans (1 call each) + record verdicts.
- `requery(para, prop, key, label, q)` — ONE targeted re-query for a CLEAN span when the first capture chunked into fragments; **appends** to `verification.requery`, never overwrites; one attempt — if still no clean span, fix the verdict NOTE instead.
- `record_verdicts(para, verdicts)` — record verdicts/notes only, NO NLM call.
- `audit(para)` / `show(para)` — substring audit / print the evidence record.

Per-paragraph script (`nlm_pN.py`) is THIN: `PARA`, `PROPS = [(prop_id, paper_key, paper-label-with-title/author/year, question)]`, `PINS`, `VERDICTS`, optional `REQUERY`. argparse modes: default `capture` | `--identity` | `--audit` | `--finalize` | `--requery` | `--verdicts`. (Older `nlm_p1`/`nlm_p2` inline the engine; new scripts import `nlm_common`.)

## 14. PLANNING vs LEDGER (tmp evidence)
During PLANNING (the target ledger not built yet), write captured evidence to a durable **`tmp/…json`** (e.g. `tmp/nlm_dwz_equations.json`), commit per query, fold into the ledger when it's created. Same engine, same rules. Pattern: `nlm_dwz_eqs.py`.

## 15. CONTENT-SCOPING DISCIPLINE — cite the fact, not the mechanism
Cite ONLY the fact the proposition needs; do not import the source's adjacent mechanism/claim. Record the boundary as a DRAFTING CAVEAT in the verdict note. Scars:
- **Keown (P6.3):** cite the pre-announcement price-run-up FACT only — NOT the insider-trading mechanism.
- **Harford (P5.1):** cite that an accumulated cash position EXISTS — NOT deliberate saving-to-fund (it's free-cash-flow stockpiling).
- **Bertrand-Schoar (P4.1):** persistent styles in firm POLICIES (premise only) — NOT the language decomposition (that's DWZ's).
- **DWZ:** they call the residual "the potentially strategic component"; the "residual is where OUR anticipatory signal must live" logic is OURS — never attribute it to DWZ.

## 16. SCRIPT SKELETON (the proven pattern)
New scripts: copy a thin `nlm_p{3,4,5,6}.py` + import `nlm_common`. The bones:
```python
import nlm_common as C
PARA = "P_"
PROPS = [("P_.1", "paper_key", '"<Title>" by <Authors> (<Year>, <Journal>)',
          "<atomic, non-leading question>")]
PINS = [...]; VERDICTS = {...}
# modes: C.capture(PARA, PROPS) | C.identity(keys) | C.audit(PARA) | C.finalize(PARA, PINS, VERDICTS)
```
Add the paper to `C.SOURCES` first (§3), run the `nlm_common.py` self-test, then `--identity` (§4), then capture.

## 17. NEVER (the scars)
- NEVER infer a paper's identity from its filename / DOI suffix / accession number. Ask NLM (§4).
- NEVER pick a source token by guessing from an opaque filename — DISCOVER the id by content (unscoped query naming the paper, §3a).
- NEVER trust a CLI flag because the `--help` PROSE mentions it — verify it's in the OPTIONS list and test it (scar: `--new` looked confirmed in the description, errored `No such option`).
- NEVER spend a content query on an unresolved, ambiguous, or identity-unconfirmed source. Fail closed.
- NEVER ad-hoc data gathering/parsing outside the script (a bare `source list` to look is the only exception).
- NEVER `source fulltext`/PDF to derive pages or content.
- NEVER hardcode the NLM id as the human key.
- NEVER hand-edit NLM data into the ledger.
- NEVER trust answer-prose as verbatim — only structured `cited_text`.
- NEVER re-run captured content queries (quota).
- NEVER expand author names / titles / numbers from memory — bib for names/titles, NLM for content.
- NEVER stop-and-poll every micro-step — deliver the result.
- NEVER ship an UNCITED connective claim unchecked. The verify gate covers only the **cited** propositions; the institutional/legal glue sentences between them slip past verify-first. (Scar: "the firm **must host** the call" — false, calls are voluntary; the advisor caught it, the gate did not.) After drafting, run a separate accuracy pass on every uncited claim — verify it or cut it.
