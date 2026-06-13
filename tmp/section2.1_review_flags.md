# Section 2.1 — user read-through flags (fix in ONE pass at the end; do NOT touch until user says done)

## FLAG 1 — P1, opening sentence
- **Text:** "...occupies a distinct \emph{disclosure state} rather than a distinct balance-sheet state."
- **Action:** CUT "rather than a distinct balance-sheet state".
- **Why:** unsourced framing (no verified prop backs it) AND contradicts P5 — cash acquirers DO have a distinct balance-sheet state (the accumulated cash), which P5 makes central.
- **Fix path (P1 — NOT in tmp/prose_drafts.json):** direct Edit on the ledger `section2.1_paragraph_ledger.json` final_prose (cf. commit a3a77e6); do NOT use `merge_prose.py` (it ABORTs for P1/P2). Then re-run `push_2_1_to_tex.py` + `latexmk -cd -pdf` + reopen PDF.
- **Status:** pending
