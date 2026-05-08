# Red-Team Audit — 3 DiD Specs — 2026-05-08

## Audit metadata

- **Auditor:** red-team subagent
- **Source:** NotebookLM F1D notebook (active_notebook_id `f1d`, URL `https://notebooklm.google.com/notebook/63e3b970-7976-47bc-8291-37ce7ac9bf74`)
- **Audit skill:** `~/.claude/skills/notebooklm-paper-audit/SKILL.md`
- **Spec file under audit:** `tmp/3did_replication_instructions_2026_05_08.md`
- **Mandate:** distrust prior memory + spec; verify every load-bearing item from primary source via 6 sequential NLM queries (2 per paper × 3 papers).
- **Protocol:** Q1 = exhaustive verbatim audit (~13 numbered items per skill template). Q2 = follow-up on holes/ambiguities/contradictions revealed by Q1. New session per paper, reuse session_id within a paper.
- **Anti-leading-question discipline:** never ask "is X correct?"; always ask "what does the paper say about X?".
- **No page numbers:** NLM page index unreliable — section/equation/table refs only.

## Critical audit targets per paper (cross-checked from spec)

**Brexit (Campello et al 2022):**
- baseline β^UK rolling-window length (memory: 24mo; Q3 said NOT IN PAPER for baseline)
- baseline β^UK vol-input frequency (daily-rolling-σ vs σ-of-monthly-returns)
- 10-K term list — memory had 9; NLM Q1 found 7 in Footnote 14
- DV form: Table 1 (CHE/lag(AT)) vs Table 8 (CHE/(AT−CHE)_lag) — which is BASELINE?
- PRE quarters: 2010Q1–2016Q2 panel vs Table 8 "two quarters preceding (2015Q3–Q4)" (Trump-mit spec or baseline?)
- Headline N: 17,170 (β^UK) vs 24,195 (10-K) per recent Q1 — verify
- 6th macro control: 1Q-ahead consensus earnings forecasts (data source?)
- HP industry-FE granularity: FIC100 vs FIC50/200/300/400
- Parallel-trends formal test details (Tables C4/C5 — likely supplementary)

**Databreach (Boasiako 2020):**
- NCSL law list source
- Firm HQ-state assignment rule (Compustat addzip-based?)
- "Cash and marketable securities" exact Compustat mapping
- "Industry Cash Flow Volatility" formula (10-yr window? 2-digit SIC?)
- Crisis-period exclusion (2007–2009?)
- All 4 FE (state+year+industry+firm) verbatim confirmed
- State-cluster SE confirmed

**Restatement (Chen 2017):**
- Hennes-Leone-Miller 2008 GAO data acquisition path
- PSM 1:1 no-replace (caliper? FF48 industry restriction?)
- DV exact Compustat mapping (#CHE/#AT verbatim)
- ALL 18 PSM probit X-variables (X1+X2+X3 sets)
- Firm FE + matched-pair-×-year cluster (Gow 2010) verbatim
- Pseudo-event placebo procedure
- Channel test PS_DEMAND construction

---

## Paper 1 — Brexit (Campello, Cortés, d'Almeida, Kankanhalli 2022 JFQA, DOI 10.1017/S0022109021000600)

### NLM Q1 — verbatim audit

(populated below)

### NLM Q2 — hole/ambiguity follow-up

(populated below)

### Brexit final verdict

(populated below)

---

## Paper 2 — Databreach (Boasiako, O'Connor Keefe 2020 EFM, DOI 10.1111/eufm.12289)

### NLM Q1 — verbatim audit

(populated below)

### NLM Q2 — hole/ambiguity follow-up

(populated below)

### Databreach final verdict

(populated below)

---

## Paper 3 — Restatement (Chen, Cheng, Lin, Tang 2017 JAAF, DOI 10.1177/0148558x17732654)

### NLM Q1 — verbatim audit

(populated below)

### NLM Q2 — hole/ambiguity follow-up

(populated below)

### Restatement final verdict

(populated below)

---

## Cross-paper summary

(populated last)
