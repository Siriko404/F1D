# Global ChatGPT Web Call System — Binding Requirements

These requirements supersede any repository-local placement proposed in the prior design.

## Canonical root

The entire product must live under this single Windows directory:

`C:\Users\sinas\OneDrive\Desktop\Projects\GptWebCall`

This root must contain all product code, the local companion, Chrome extension source and builds, schemas, protocol documentation, configuration, global database/state, project registry, call request/response folders, validation records, logs, quarantine, backups, tests, fixtures, installers, and migration tools.

No F1D, thesis, or other working repository is the product's permanent home. Existing repository-local exchanges may be imported or indexed read-only, but the new system must not require its infrastructure to be installed inside each project.

## Invocation from Codex and Claude Code

The product must have one canonical, client-neutral Markdown protocol at a stable path under the canonical root. A user must be able to invoke the system from any Codex or Claude Code session by giving an instruction equivalent to:

> Read `C:\Users\sinas\OneDrive\Desktop\Projects\GptWebCall\WEB_CALL_PROTOCOL.md` and follow it for this task.

That Markdown file must be sufficient to tell either client:

- how to classify a task as routine or reasoning-heavy;
- when a Web call is required;
- how to locate and invoke the installed local CLI/companion;
- how to register or select the current external project without moving that project's source into the system root;
- how to prepare the minimum context package by copying approved source snapshots into the global call folder;
- how to use the Go/Done user workflow;
- how to validate, accept, correct, integrate, and record completion;
- how to use the manual fallback when the extension or companion is unavailable;
- and how to resume safely after context compaction or a different client/session takes over.

The canonical protocol may contain short client-specific adapter sections only when Codex and Claude Code genuinely require different commands or instruction syntax. The underlying state, calls, schemas, and lifecycle must remain shared and client-neutral.

## Global state and project isolation

The system must support many unrelated projects concurrently from one installation. It must keep a global project registry and stable project IDs. Each registered project may point to an external working directory, but all Web-call evidence and operational state must remain under `GptWebCall`.

The system must prevent calls, files, responses, approvals, and integrations from being mixed across projects. Every call must be bound to a project, request package digest, and expected output set.

The system must not silently modify an external project. Codex or Claude Code may integrate an accepted artifact into the external project only as an explicit, separately recorded action governed by that project's own repository instructions and tests.

## Deterministic core and wrapper

The timestamped JSON-and-folder exchange model remains the durable source of evidence. The extension and local companion are wrappers around that deterministic core, not replacements for it.

The first release must use the conservative approved boundary from the prior review:

- Go shows the exact frozen prompt and files, records user authorization, opens ChatGPT, copies the prompt only after a user action, and reveals the request folder.
- The user attaches files, presses ChatGPT Send, reviews the result, and downloads returned files through normal ChatGPT controls.
- Done opens an explicit native file picker. The user selects the returned files. The companion copies, hashes, binds, validates, quarantines failures, and records the result.
- No response DOM scraping, private endpoint use, cookie/session access, automatic Send, automatic retry, or automatic/programmatic Output extraction is allowed.

The manual file-based workflow must always remain usable.

## Prompt filename rule

Every new exchange prompt file must be named:

`PROMPT_YYYY-MM-DD_HHMMSS.txt`

The timestamp must exactly match the exchange-folder timestamp. New `PASTE_THIS_PROMPT.txt` files are prohibited. Legacy files retain historical names unchanged.

## OneDrive constraint

The canonical root is inside OneDrive. The design must explicitly address locking, SQLite/WAL behavior, sync conflicts, atomic writes, backup, restore, and single-host versus multi-host assumptions. It must not ignore or hand-wave the risk of placing transactional state in a synchronized directory. The user requires the system to live under the canonical root, so any volatile runtime staging outside that root must be justified, minimized, recoverable, and leave the durable authoritative state under the canonical root.

## Delivery expectation

The immediate goal is an implementation-ready standalone architecture delta and repository plan—not code from ChatGPT Web. Codex will inspect the returned design, create the new standalone repository, implement it test-first, and verify it end to end.
