# Restricted Agno Counsel Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the five ratified DeepSeek V4-Pro counsel experts once while mechanically
limiting each expert to C1, C2, public-web discovery, private raw web snapshots, and its
own append-only journal.

**Architecture:** A Python host creates one policy object and one Agno agent per ratified
expert. The model never receives a general filesystem or shell tool. A tool named `bash`
parses a deliberately tiny command grammar and performs allowed operations directly
without invoking a shell; `web_search` supplies discovery-only results. Agno sessions and
runs persist in SQLite, while a coordinator writes an atomic status file and exposes
start-once, status, cancel, and continue commands.

**Tech Stack:** Python 3.12+, Agno 2.7.2, DeepSeek V4-Pro, httpx, DDGS, SQLite, pytest,
Node.js 24 journal enforcement, uv with an external virtual environment.

## Global Constraints

- Exactly five ratified prompts and five ratified manifests; never hand-edit generated prompts.
- Each expert can read only C1, C2, and snapshots under `downloads/<expert>/`.
- No repository enumeration, arbitrary filesystem access, subprocess shell, cross-expert reads, or provider-secret exposure.
- Web-search output is discovery-only; evidence requires raw HTTP capture and journal registration.
- Every journal append runs the persisted `tools/journal.js` with JSON on stdin.
- One initial run per expert; no automatic substantive retry.
- No real API call until all unit, policy-adversarial, and offline-integration tests pass.
- Preserve all artifacts under the counsel run; keep the Python environment outside the repository.

---

### Task 1: Project skeleton and immutable run configuration

**Files:**
- Create: `harness/pyproject.toml`
- Create: `harness/src/counsel_harness/__init__.py`
- Create: `harness/src/counsel_harness/config.py`
- Test: `harness/tests/test_config.py`

**Interfaces:**
- Produces: `RunConfig.load(run_dir: Path) -> RunConfig` and `ExpertConfig` records containing prompt, manifest, journal, and private-download paths.

- [ ] Write tests asserting exactly five experts, two manifest sources per expert, both `must_read`, prompt existence, prompt/spec identity inputs, private download paths, and rejection of any manifest path outside `context-sources`.
- [ ] Run `uv run pytest tests/test_config.py -q` and confirm failure because `counsel_harness.config` does not exist.
- [ ] Implement frozen dataclasses and strict loader validation; do not load the API key.
- [ ] Re-run the test and confirm it passes.

### Task 2: Restricted Bash proxy and raw-web boundary

**Files:**
- Create: `harness/src/counsel_harness/policy.py`
- Create: `harness/src/counsel_harness/bash_proxy.py`
- Create: `harness/src/counsel_harness/web.py`
- Test: `harness/tests/test_policy.py`
- Test: `harness/tests/test_bash_proxy.py`
- Test: `harness/tests/test_web.py`

**Interfaces:**
- Produces: `ExpertPolicy.resolve_read(ref_or_path: str) -> Path`, `BashProxy.run(command: str) -> str`, `RawDownloader.download(url: str, relative_name: str) -> Path`, and `WebDiscovery.search(query: str, max_results: int) -> list[dict]`.

- [ ] Write failing adversarial tests for repository paths, `..`, symlinks, archive paths, other experts' downloads/journals, command chaining, pipes, substitutions, environment expansion, arbitrary executables, private/loopback/link-local URLs, redirect-to-private URLs, oversized responses, and overwrite attempts.
- [ ] Write failing positive tests for bounded text extraction from C1/C2 or private snapshots, fixed-string/regex search, raw HTTPS capture into the private subtree, and discovery results labeled non-evidence.
- [ ] Run the three test modules and verify the expected missing-implementation failures.
- [ ] Implement a non-shell parser supporting only bounded read/search/count commands, canonical journal heredoc append, and raw curl/wget-style capture; perform operations with Python/Node argument arrays, never `shell=True`.
- [ ] Implement DNS/IP validation on every redirect, byte limits, filename/path validation, exclusive file creation, timeout limits, and exact expert ownership checks.
- [ ] Re-run all three modules and confirm every positive and adversarial test passes.

### Task 3: Journal bridge and secret isolation

**Files:**
- Create: `harness/src/counsel_harness/journal_bridge.py`
- Create: `harness/src/counsel_harness/secrets.py`
- Test: `harness/tests/test_journal_bridge.py`
- Test: `harness/tests/test_secrets.py`

**Interfaces:**
- Produces: `JournalBridge.append(entry: dict) -> AppendResult` and `load_deepseek_key(dpapi_path: Path) -> SecretStr`.

- [ ] Write failing tests proving stdin JSON reaches `journal.js`, only the assigned journal is writable, Node errors propagate without modification, provider secrets never enter subprocess environments/logs/status files, and DPAPI output is never printed.
- [ ] Run the tests and verify missing-implementation failure.
- [ ] Implement Node invocation with an explicit sanitized environment and `stdin` bytes; implement Windows DPAPI decryption through a small private function returning a non-printing secret wrapper.
- [ ] Re-run tests and confirm they pass.

### Task 4: Agno agents, persistence, and coordination controls

**Files:**
- Create: `harness/src/counsel_harness/agents.py`
- Create: `harness/src/counsel_harness/coordinator.py`
- Test: `harness/tests/test_agents.py`
- Test: `harness/tests/test_coordinator.py`

**Interfaces:**
- Produces: `build_agents(config, key) -> dict[str, Agent]`, `Coordinator.start_once()`, `Coordinator.status()`, `Coordinator.cancel(slug)`, and `Coordinator.continue_run(slug, message)`.

- [ ] Write failing tests with fake model adapters proving five independent sessions, exact prompt loading, only `bash` and `web_search` tool exposure, returned run IDs atomically persisted, duplicate-launch rejection, per-expert cancellation, and continuation in the same Agno session.
- [ ] Run both modules and verify missing-implementation failure.
- [ ] Implement DeepSeek V4-Pro agents with SQLite persistence, telemetry disabled, tracing persisted locally, 60 tool/model iterations, and 120-minute expert timeout.
- [ ] Implement concurrent start-once coordination, cancellation, continuation, crash-state persistence, and final-response validation requiring only journal path plus counts.
- [ ] Re-run tests and confirm they pass.

### Task 5: CLI, AgentOS surface, and passive completion monitor

**Files:**
- Create: `harness/src/counsel_harness/cli.py`
- Create: `harness/src/counsel_harness/agent_os_app.py`
- Test: `harness/tests/test_cli.py`
- Test: `harness/tests/test_agent_os_app.py`

**Interfaces:**
- Produces commands `validate`, `launch`, `status`, `cancel <slug>`, `continue <slug> <message>`, and an AgentOS FastAPI application exposing native session/run/cancel/continue routes.

- [ ] Write failing CLI tests for successful offline validation, launch refusal before gates, launch refusal after a start marker, status exit codes, cancellation, and continuation.
- [ ] Write a failing FastAPI test asserting the five registered agents and native run/cancel/continue route presence without making a model call.
- [ ] Run tests and verify missing-implementation failure.
- [ ] Implement the CLI and AgentOS app using the same agent factory and database.
- [ ] Re-run tests and confirm they pass.

### Task 6: Offline end-to-end adversarial validation

**Files:**
- Create: `harness/tests/test_offline_integration.py`
- Create: `harness/VALIDATION.md`

**Interfaces:**
- Consumes all prior components; produces a reproducible FIRE-readiness verdict.

- [ ] Write a fake-model integration that attempts allowed C1/C2 reads, a denied third-repository-file read, denied archive and cross-agent reads, a raw local HTTP download, source registration, grounded quote append, context check-ins, and journal seal.
- [ ] Run it first and confirm failure before the complete integration fixture exists.
- [ ] Add only the minimal integration fixture/server needed to exercise real components.
- [ ] Run `uv run pytest -q` and the copied Node test suite; require zero failures.
- [ ] Run `python -m counsel_harness.cli validate`, persist hashes/test counts/access probes in `VALIDATION.md`, and require `FIRE READY`.

### Task 7: FIRE, passive monitoring, and mechanical read-back

**Files:**
- Create during execution: `harness/status.json`, `harness/start-marker.json`, `harness/launch.log`, `agentos.sqlite`, `journal/*.jsonl`, `downloads/<expert>/*`, `reports/*.json`, `readback-verdict.json`, and `readback.md`.

**Interfaces:**
- Produces sealed journals and mechanically verified read-back artifacts.

- [ ] Decrypt the DPAPI key only in the coordinator process and launch all five runs once.
- [ ] Attach a passive harness-native completion notification; do not perform model polling work.
- [ ] On notification, run `node tools/journal.js status <run_dir>` and require all journals sealed; use crash recovery only for incomplete experts.
- [ ] Run `node tools/verify-readback.js <run_dir>` before editing any audited artifact.
- [ ] Assemble and render each journal mechanically, concatenate verbatim render output into `readback.md`, and add no prose or ranking.
