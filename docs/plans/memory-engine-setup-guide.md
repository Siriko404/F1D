# Self-Evolving Memory Engine for Claude Code

A per-repo memory system that makes Claude Code smarter across sessions. Based on Karpathy's LLM Wiki pattern, extended with cognitive-science-inspired memory tiers and automated consolidation.

Everything is repo-local. No global config is touched. No other repo is affected. You set it up per repo, only where you want it.

## Prerequisites

- **Node.js** (any recent version — v18+)
- **Claude Code** (v2.1.59+ for auto memory support, v2.2+ for hooks)
- **A git repo** (optional but recommended — the guide auto-adds .gitignore entries)

---

## How It Works

### The Problem

Claude Code starts every session with a blank slate. It reads your CLAUDE.md file for project instructions, but it doesn't remember what happened last session — what decisions were made, what errors were hit, what patterns were discovered. Every session starts from zero.

### The Solution

This system gives Claude Code a persistent, structured memory that lives as plain markdown files in your repo. Two hooks (small scripts) fire automatically:

1. **SessionStart hook** — runs when you open Claude Code. On the first session of each day, it tells Claude to consolidate yesterday's memories before starting work.
2. **PreCompact hook** — runs when Claude's context window fills up. It tells Claude to save what it's learned before the context is compressed.

Claude then reads and writes to the memory files during your session, building up knowledge over time.

### The Four Memory Tiers

The system uses four tiers of memory, inspired by how human memory works:

```
 Tier 1: WORKING MEMORY     (raw observations, 48-hour lifespan)
    ↓ heartbeat archives
 Tier 2: EPISODIC MEMORY     (compressed session summaries)
    ↓ heartbeat extracts patterns
 Tier 3: SEMANTIC MEMORY     (established facts with confidence scores)
    ↓ heartbeat recognizes workflows
 Tier 4: PROCEDURAL MEMORY   (learned step-by-step procedures)
```

**Working memory** (`_agent/memory/working/`): Notes captured during a session. Things like "user prefers tabs over spaces" or "the build breaks when X" or "decided to use approach Y for Z reason." These are raw, unprocessed. They expire after 48 hours — either promoted or discarded.

**Episodic memory** (`_agent/memory/episodic/`): End-of-session summaries. What happened, what was decided, what patterns were noticed, what's still unresolved. One file per session, named by date.

**Semantic memory** (`_agent/memory/semantic/`): Facts established across multiple sessions. "This user always wants error handling in API routes" or "The test suite takes 3 minutes and should not be run in watch mode." Each fact has a confidence score (0.0–0.95) that increases when reinforced by new evidence. Facts not reinforced in 90 days get flagged as potentially stale.

**Procedural memory** (`_agent/memory/procedural/`): Workflows Claude has learned from repeated patterns. "When deploying, always run tests first, then build, then push to staging." These are the highest-value memories — they let Claude execute multi-step workflows it's learned from your habits.

### The Heartbeat

On the **first Claude Code session of each day** (not a cron job — it fires only when you actually work), the heartbeat consolidation runs:

1. Archives working memory older than 48 hours → compresses into episodic summaries
2. Reviews recent episodic entries → extracts recurring patterns
3. Promotes patterns seen in 2+ episodes → creates/updates semantic facts with confidence scores
4. Recognizes repeatable workflows in semantic memory → promotes to procedural memory
5. Flags semantic facts not reinforced in 90+ days as stale
6. Writes a daily briefing summarizing the memory state

This is what makes the system self-evolving: each day, raw observations get compressed, filtered, and promoted into higher-value memories. Over weeks, the semantic and procedural tiers accumulate real, useful patterns.

### The Hot Cache

`_agent/memory/hot.md` is a fast-resume file. At the end of each session, Claude writes the current focus, recent decisions, and open threads here. At the start of the next session, Claude reads it first — instant context recovery without replaying all memory files.

---

## Setup (from scratch, in any repo)

### Step 1: Create the directory structure

Open a terminal at your repo root and run:

```bash
mkdir -p _agent/memory/working _agent/memory/episodic _agent/memory/semantic _agent/memory/procedural
mkdir -p .claude/hooks .claude/rules
```

### Step 2: Create the seed files

Create the heartbeat tracker (empty file — tells the hook no heartbeat has run yet):

```bash
touch _agent/memory/.last_heartbeat
```

Create `_agent/memory/heartbeat-log.md`:

```markdown
---
title: Heartbeat Log
type: heartbeat-log
---

# Heartbeat Log

Chronological record of memory consolidation runs. Append-only.
```

Create `_agent/memory/hot.md`:

```markdown
---
title: Hot Cache
type: hot-cache
---

# Hot Cache — Recent Context

Fast-resume cache. Read at session start. Updated at end of meaningful sessions.

## Current Focus
_Not yet populated._

## Recent Decisions
_None yet._

## Open Threads
_None yet._
```

### Step 3: Create the heartbeat hook

This script runs on every Claude Code session start. It checks if today's heartbeat has already run. If not, it tells Claude to consolidate memory before doing anything else.

Create `.claude/hooks/heartbeat.js`:

```javascript
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const cwd = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const memoryDir = path.join(cwd, '_agent', 'memory');
const heartbeatFile = path.join(memoryDir, '.last_heartbeat');
const today = new Date().toISOString().split('T')[0];

// Skip if memory structure doesn't exist or user opted out
if (fs.existsSync(path.join(cwd, '_agent', '.no-memory')) || !fs.existsSync(memoryDir)) {
  process.exit(0);
}

const mp = memoryDir.replace(/\\/g, '/');
let lastHeartbeat = '';
try { lastHeartbeat = fs.readFileSync(heartbeatFile, 'utf8').trim(); } catch (e) {}

if (lastHeartbeat !== today) {
  // First session of the day — write date immediately (prevents duplicate triggers)
  try { fs.writeFileSync(heartbeatFile, today, 'utf8'); } catch (e) {}

  const output = {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: [
        '[HEARTBEAT] First session of the day (' + today + ').',
        'Memory path: ' + mp,
        '',
        'Run the Heartbeat Protocol before proceeding:',
        '',
        '1. Read ' + mp + '/working/ — archive files with created date >48hr to ' + mp + '/episodic/ as compressed summaries. Delete archived originals.',
        '2. Read recent ' + mp + '/episodic/ entries — identify recurring patterns, preferences, decisions.',
        '3. Promote patterns appearing in 2+ episodes to ' + mp + '/semantic/ (create or update, set confidence).',
        '4. If any semantic note describes a repeatable workflow, promote to ' + mp + '/procedural/.',
        '5. Flag semantic notes not reinforced in 90+ days with stale: true.',
        '6. Write daily briefing to ' + mp + '/working/daily-brief-' + today + '.md.',
        '7. Append entry to ' + mp + '/heartbeat-log.md.',
        '',
        'Then load ' + mp + '/hot.md and proceed with user requests.',
      ].join('\n'),
    },
  };
  console.log(JSON.stringify(output));
} else {
  // Heartbeat already ran today — just load context
  const output = {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: [
        '[MEMORY] Heartbeat already ran today (' + today + ').',
        'Memory path: ' + mp,
        'Load ' + mp + '/hot.md for recent context.',
        'Check ' + mp + '/working/ for recent observations.',
        'Save notable observations, decisions, errors to ' + mp + '/working/ during this session.',
      ].join('\n'),
    },
  };
  console.log(JSON.stringify(output));
}
```

### Step 4: Create the precompact hook

This script runs when Claude's context window fills up and is about to be compressed. It tells Claude to save important information before it's lost.

Create `.claude/hooks/precompact.js`:

```javascript
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const cwd = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const memoryDir = path.join(cwd, '_agent', 'memory');
const today = new Date().toISOString().split('T')[0];

// Skip if memory structure doesn't exist or user opted out
if (fs.existsSync(path.join(cwd, '_agent', '.no-memory')) || !fs.existsSync(memoryDir)) {
  process.exit(0);
}

const mp = memoryDir.replace(/\\/g, '/');
const output = {
  hookSpecificOutput: {
    hookEventName: 'PreCompact',
    additionalContext: [
      '[MEMORY SAVE] Context is about to compact. Save critical information now:',
      '',
      '1. Save any unsaved observations/decisions/errors to ' + mp + '/working/',
      '2. If this was a substantial session, write a summary to ' + mp + '/episodic/' + today + '-N.md (increment N from existing files)',
      '3. Update ' + mp + '/hot.md with current focus, recent decisions, open threads',
      '',
      'Use YAML frontmatter formats defined in .claude/rules/memory-engine.md.',
    ].join('\n'),
  },
};
console.log(JSON.stringify(output));
```

### Step 5: Register the hooks

Create `.claude/settings.local.json` — this tells Claude Code to run the hooks for THIS repo only:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/heartbeat.js\""
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/.claude/hooks/precompact.js\""
          }
        ]
      }
    ]
  }
}
```

**Why `settings.local.json`?** This file is personal (not shared via git). The hooks reference local paths. Each person who clones the repo creates their own `settings.local.json`.

### Step 6: Create the memory engine rules

This file teaches Claude the memory protocol — what each tier means, what file formats to use, when to save, when to promote. Claude Code automatically reads all `.md` files in `.claude/rules/` at session start.

Create `.claude/rules/memory-engine.md`:

```markdown
# Memory Engine — Self-Evolving Per-Repo Memory

## Four Tiers

| Tier | Path | TTL | Purpose |
|------|------|-----|---------|
| Working | `_agent/memory/working/` | 48hr | Raw observations from current/recent sessions |
| Episodic | `_agent/memory/episodic/` | Indefinite | Compressed session summaries |
| Semantic | `_agent/memory/semantic/` | 90-day stale flag | Cross-session established facts with confidence |
| Procedural | `_agent/memory/procedural/` | Indefinite | Learned workflows and repeated patterns |

Promotion: working -> episodic -> semantic -> procedural. Each tier is more compressed, more confident, longer-lived.

## File Formats

### Working (`_agent/memory/working/*.md`)

Name files descriptively: `obs-api-error-handling.md`, `decision-use-postgres.md`, etc.

    ---
    type: observation | decision | error | preference
    created: YYYY-MM-DDTHH:MM:SS
    tags: [relevant, tags]
    ---
    Content of the observation.

### Episodic (`_agent/memory/episodic/YYYY-MM-DD-N.md`)

N = session number for that day (1, 2, 3...). Increment from existing files.

    ---
    type: episode
    date: YYYY-MM-DD
    session: N
    tags: [topic1, topic2]
    ---
    ## Summary
    What happened.
    ## Key Decisions
    - Decision and rationale
    ## Patterns Noticed
    - Pattern
    ## Open Threads
    - Unresolved item

### Semantic (`_agent/memory/semantic/*.md`)

Name files by the fact: `user-prefers-tabs.md`, `build-requires-node-20.md`, etc.

    ---
    type: semantic
    created: YYYY-MM-DD
    updated: YYYY-MM-DD
    confidence: 0.85
    reinforced_count: 3
    last_reinforced: YYYY-MM-DD
    evidence: ["episodic/2026-04-08-1.md"]
    tags: [category]
    ---
    The distilled fact. Evidence and confidence rationale.

Confidence scale: 0.6 initial, +0.1 per reinforcement, cap at 0.95.

### Procedural (`_agent/memory/procedural/*.md`)

Name files by the workflow: `deploy-to-staging.md`, `handle-migration.md`, etc.

    ---
    type: procedure
    created: YYYY-MM-DD
    updated: YYYY-MM-DD
    trigger: "when [condition]"
    tags: [workflow]
    ---
    ## Steps
    1. Step one
    2. Step two
    ## Notes
    Caveats or variations.

## Heartbeat Protocol

Triggered automatically on the first Claude Code session of each day. Run these steps before user requests:

1. **Archive stale working memory**: files with `created` >48hr -> compress to `episodic/`. Delete originals.
2. **Pattern extraction**: Read 5 most recent `episodic/` files. Find recurring themes.
3. **Promote to semantic**: Patterns in 2+ episodes -> create/update `semantic/` note. Initial confidence 0.6. Reinforcement increments count, raises confidence (cap 0.95).
4. **Promote to procedural**: Semantic notes describing trigger -> steps -> outcome workflows -> create `procedural/` note.
5. **Stale check**: Semantic notes with `last_reinforced` >90 days -> add `stale: true`.
6. **Daily briefing**: Write `working/daily-brief-YYYY-MM-DD.md` summarizing state.
7. **Log**: Append to `heartbeat-log.md`.

## Session Lifecycle

**On start:**
1. Read `_agent/memory/hot.md` for recent context
2. Scan `_agent/memory/working/` for recent observations
3. If `[HEARTBEAT]` in context -> run Heartbeat Protocol first

**During session:**
- Save notable observations, decisions, errors to `_agent/memory/working/`
- Only save things that would be useful in future sessions
- Don't over-capture

**Before ending meaningful sessions:**
1. Save session summary to `_agent/memory/episodic/YYYY-MM-DD-N.md`
2. Update `_agent/memory/hot.md` with current focus, recent decisions, open threads

**On compaction (`[MEMORY SAVE]` in context):**
- Save unsaved observations to `_agent/memory/working/`
- Write episodic summary if substantial work was done
- Update `_agent/memory/hot.md` for post-compaction resume
```

### Step 7: Update .gitignore

Add these lines to your `.gitignore` (create the file if it doesn't exist):

```
# Claude Code memory engine (personal, not committed)
_agent/

# Local Claude settings (personal, not committed)
.claude/settings.local.json
```

---

## Verification

After completing all steps, run these from your repo root to verify:

```bash
# Test 1: Heartbeat triggers on first run
echo "" > _agent/memory/.last_heartbeat
CLAUDE_PROJECT_DIR="$(pwd)" node .claude/hooks/heartbeat.js
# Expected: JSON containing [HEARTBEAT]

# Test 2: Heartbeat is idempotent on same day
CLAUDE_PROJECT_DIR="$(pwd)" node .claude/hooks/heartbeat.js
# Expected: JSON containing [MEMORY] (not HEARTBEAT)

# Test 3: PreCompact hook fires
CLAUDE_PROJECT_DIR="$(pwd)" node .claude/hooks/precompact.js
# Expected: JSON containing [MEMORY SAVE]

# Test 4: Opt-out works
touch _agent/.no-memory
CLAUDE_PROJECT_DIR="$(pwd)" node .claude/hooks/heartbeat.js
# Expected: no output (empty)
rm _agent/.no-memory
```

If all four tests produce expected output, the setup is complete.

---

## What to Commit vs What to Gitignore

**Commit** (shareable — the engine itself):
```
.claude/hooks/heartbeat.js
.claude/hooks/precompact.js
.claude/rules/memory-engine.md
```

**Gitignore** (personal — your memory data and local config):
```
_agent/                      # Your memory data
.claude/settings.local.json  # Your local hook registration
```

If you clone a repo that has the engine committed, you only need to:
1. Create the `_agent/memory/` directories (step 1)
2. Create the seed files (step 2)
3. Create `.claude/settings.local.json` (step 5)

---

## Daily Usage

### What you do

Nothing special. Just use Claude Code normally. The hooks fire automatically. Claude reads and writes memory files based on the rules.

If you want Claude to remember something specific, tell it: "Save this to working memory" or "Note this decision in working memory." Claude knows the file formats from the rules file.

### What Claude does automatically

- **Session start**: Reads hot cache and working memory for context
- **First session of the day**: Runs heartbeat consolidation (takes ~30 seconds of Claude's response)
- **During work**: Saves notable observations when it encounters them
- **Before ending**: Writes episodic summary and updates hot cache
- **Before compaction**: Saves anything unsaved to working memory

### What you'll see over time

- **Week 1**: Working and episodic tiers fill up. Hot cache gives fast session resume.
- **Week 2+**: Semantic tier starts accumulating — Claude remembers your preferences, your project's quirks, recurring patterns.
- **Month 1+**: Procedural tier captures workflows — Claude executes multi-step processes it's learned from your habits.

### Reviewing your memory

All memory is plain markdown. Open the `_agent/memory/` directory in any editor or in Obsidian. You can:
- Read what Claude has learned about your project
- Edit or delete any memory file (Claude will adapt)
- Check `heartbeat-log.md` to see consolidation history
- Look at `semantic/` to see what facts Claude considers established

---

## File Tree (complete)

```
your-repo/
├── .claude/
│   ├── hooks/
│   │   ├── heartbeat.js             # SessionStart hook script
│   │   └── precompact.js            # PreCompact hook script
│   ├── rules/
│   │   └── memory-engine.md         # Memory protocol for Claude
│   └── settings.local.json          # Hook registration (GITIGNORED)
├── _agent/                          # ALL GITIGNORED
│   └── memory/
│       ├── working/                 # Tier 1: current observations (48hr)
│       ├── episodic/                # Tier 2: session summaries
│       ├── semantic/                # Tier 3: established facts
│       ├── procedural/             # Tier 4: learned workflows
│       ├── .last_heartbeat          # Heartbeat date tracker
│       ├── heartbeat-log.md         # Consolidation run history
│       └── hot.md                   # Fast-resume cache
├── .gitignore                       # Must include _agent/ and settings.local.json
└── CLAUDE.md                        # Your project's own instructions (separate)
```

---

## Opting Out

To temporarily disable without deleting anything:

```bash
touch _agent/.no-memory
```

Both hooks check for this file and exit silently when it exists. Remove it to re-enable:

```bash
rm _agent/.no-memory
```

To fully remove:

```bash
rm -rf _agent/ .claude/hooks/heartbeat.js .claude/hooks/precompact.js .claude/rules/memory-engine.md .claude/settings.local.json
```

---

## Troubleshooting

**Hooks don't fire**: Verify `.claude/settings.local.json` exists and is valid JSON. Run `node .claude/hooks/heartbeat.js` manually to check for errors. Make sure Node.js is installed.

**Claude doesn't follow memory protocol**: Check that `.claude/rules/memory-engine.md` exists. Run `/memory` in Claude Code to see what instruction files are loaded — the rules file should appear.

**Heartbeat runs every session (not just first of day)**: Check `_agent/memory/.last_heartbeat` — it should contain today's date after the first run. If empty, the hook's write might be failing (permissions issue).

**Memory files accumulate but never consolidate**: The heartbeat only runs on the first session of each day. If you only use Claude Code once per day, consolidation happens at the start of that session. To force a heartbeat, clear the date: `echo "" > _agent/memory/.last_heartbeat`
