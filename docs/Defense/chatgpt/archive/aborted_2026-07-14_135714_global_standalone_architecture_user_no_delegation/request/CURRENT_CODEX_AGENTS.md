<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **F1D** (11814 symbols, 20943 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/F1D/context` | Codebase overview, check index freshness |
| `gitnexus://repo/F1D/clusters` | All functional areas |
| `gitnexus://repo/F1D/processes` | All execution flows |
| `gitnexus://repo/F1D/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

# ChatGPT Web — Universal Reasoning Gate

This gate applies to **every task**, not only thesis or defense work.

## Triage Before Work

Before beginning substantive work, explicitly decide whether the task is
reasoning-heavy. Treat a task as reasoning-heavy when it materially involves one
or more of the following:

- planning or architecture;
- investigation, diagnosis, or competing explanations;
- deep or multi-source web research;
- high-stakes factual, legal, academic, financial, or technical judgment;
- synthesis across long files, datasets, or conflicting evidence;
- ambiguous requirements or consequential trade-offs;
- creating a substantial artifact whose structure or content requires judgment;
- reviewing or auditing work where an independent second reasoning pass is useful.

Routine deterministic execution is not reasoning-heavy: simple file operations,
direct lookups, mechanical formatting, running an already-approved plan, or small
unambiguous corrections may proceed locally.

If the task is reasoning-heavy, stop before the substantive decision or execution
and create one exchange folder under:

`../F1D-phase3/docs/Defense/chatgpt/calls/YYYY-MM-DD_HHMMSS_short_subject/`

Every Web call is one self-contained exchange. Its timestamped subject folder must
contain `request/` for every file Sina uploads, `response/` for every file ChatGPT
Web returns, and `EXCHANGE_MANIFEST.json` linking the two sides. Never mix request
or response files from separate calls, and do not use a shared global upload or
received folder for new exchanges.

The governing protocol is:

`../F1D-phase3/docs/Defense/chatgpt/CHATGPT_WEB_PROTOCOL.json`

## Required Web Delivery

- The task, questions, scope, authority hierarchy, and requested outputs must be
  encoded in `WEB_REVIEW_REQUEST.json`.
- ChatGPT Web may research, investigate, reason, plan, perform requested work, and
  create or modify artifacts when the request authorizes it.
- The main response must always be an actual downloadable JSON file conforming to
  `WEB_RESPONSE_SCHEMA.json`.
- Any requested artifacts must be returned as additional downloadable files and
  listed in the main JSON's artifact manifest.
- Every new call's paste-in instruction file must be named
  `PROMPT_YYYY-MM-DD_HHMMSS.txt`, using the exact local creation timestamp from
  that call's exchange-folder name. Do not create new `PASTE_THIS_PROMPT.txt`
  files.
- ChatGPT Web must emit **no conversational text at all**: no acknowledgment, no
  summary, no markdown, and no code block. Its entire response consists only of
  the main JSON attachment and any artifact attachments.
- If it cannot complete the work, it must still return only the main JSON file,
  with `status` set to `PARTIAL` or `BLOCKED` and the limitation recorded there.

Sina transports the files to and from ChatGPT Web. Codex validates the returned
JSON and artifacts, independently checks important claims, and treats the Web
result as advisory rather than automatically authoritative.
