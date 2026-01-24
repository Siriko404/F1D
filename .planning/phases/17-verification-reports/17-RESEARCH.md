# Phase 17: Verification Reports - Research

**Researched:** 2026-01-23
**Domain:** Verification Documentation & Quality Assurance
**Confidence:** HIGH

## Summary

Phase 17 is a documentation gap-closure phase that creates VERIFICATION.md reports for 13 unverified phases (Phases 2, 3, 4, 5, 6, 8, 10, 11, 12, plus documentation of verified phases 1, 7, 9, 14, 15). The phase follows the GSD goal-backward verification methodology which verifies that phase goals are achieved by checking observable truths, required artifacts, and key link wiring.

The standard verification approach uses a three-level artifact verification (existence, substantive, wired) and produces structured reports that either pass, fail, or require human verification. Verification reports document gaps with specific statuses (critical vs non-critical) and provide evidence for all findings.

**Primary recommendation:** Follow the established VERIFICATION.md template from Phase 01 and use the gsd-verifier agent to automate verification checks. Each verification report must derive must-haves from PLAN.md frontmatter or from phase goals using goal-backward derivation.

## Standard Stack

The verification process uses established GSD tooling and patterns:

### Core
| Tool | Purpose | Why Standard |
|------|---------|--------------|
| GSD Verification Workflow | Goal-backward verification methodology | Defined in `~/.config/opencode/get-shit-done/workflows/verify-phase.md` |
| gsd-verifier Agent | Automated verification subagent | Executes verification following established patterns |
| VERIFICATION.md Template | Standard report structure | Defined in `~/.config/opencode/get-shit-done/templates/verification-report.md` |

### Reference Materials
| Document | Purpose | Location |
|-----------|---------|----------|
| Verification Patterns | How to detect stubs, verify artifacts, check wiring | `~/.config/opencode/get-shit-done/references/verification-patterns.md` |
| Phase Template | Example verification report with all sections | `.planning/phases/01-template-pilot/01-TEMPLATE-VERIFICATION.md` |
| Existing Reports | Working examples from phases 1, 7, 9, 13, 14, 15, 16 | Phase directories |

### Verification Tools (Bash)
| Tool | Purpose | Example |
|------|---------|---------|
| grep | Pattern matching for stubs, imports, wiring | `grep -E "TODO|FIXME|placeholder"` |
| wc -l | Line count verification (substantive check) | `wc -l < script.py` |
| find | File existence checks | `find . -name "VERIFICATION.md"` |

## Architecture Patterns

### Verification Report Structure

```markdown
---
phase: XX-name
verified: YYYY-MM-DDTHH:MM:SSZ
status: passed | gaps_found | human_needed
score: N/M must-haves verified
gaps: []
human_verification: []
---

# Phase X: {Name} Verification Report

**Phase Goal:** {goal from ROADMAP.md}
**Verified:** {timestamp}
**Status:** {status}

## Goal Achievement
### Observable Truths
### Required Artifacts
### Key Link Verification
### Requirements Coverage
### Anti-Patterns Found
### Human Verification Required
### Gaps Summary
## Detailed Plan Verification (if multi-plan phase)
## Conclusion
---
```

### Pattern 1: Goal-Backward Verification
**What:** Start from phase goal, derive what must be TRUE, verify what must EXIST and be WIRED
**When to use:** For all phase verifications
**Example:**
```yaml
# From phase goal: "Working chat interface"
Derived Truths:
  - "User can see existing messages"
  - "User can send a message"
  - "Messages persist across refresh"

Supporting Artifacts:
  - Chat.tsx (renders messages)
  - /api/chat (provides messages)
  - Database model (stores messages)

Key Links:
  - Chat.tsx → /api/chat via fetch
  - /api/chat → database via prisma
```

### Pattern 2: Three-Level Artifact Verification
**What:** Check existence (file exists), substantive (real implementation, not stub), wired (connected to system)
**When to use:** For every artifact in must_haves
**Example:**
```bash
# Level 1: Existence
[ -f "src/components/Chat.tsx" ] && echo "EXISTS" || echo "MISSING"

# Level 2: Substantive (no stubs, adequate length)
lines=$(wc -l < "src/components/Chat.tsx")
stubs=$(grep -c "TODO|FIXME|placeholder" "src/components/Chat.tsx")
[ "$lines" -gt 15 ] && [ "$stubs" -eq 0 ] && echo "SUBSTANTIVE"

# Level 3: Wired (imported and used)
imports=$(grep -r "import.*Chat" src/ | wc -l)
uses=$(grep -r "Chat" src/ | grep -v import | wc -l)
[ "$imports" -gt 0 ] && [ "$uses" -gt 0 ] && echo "WIRED"
```

### Pattern 3: Gap Documentation Structure
**What:** Document gaps with truth, status, reason, artifacts, missing items
**When to use:** In frontmatter gaps array and Gaps Summary section
**Example:**
```yaml
gaps:
  - truth: "Large scripts broken into smaller modules"
    status: failed
    reason: "11 scripts still >800 lines after refactoring"
    artifacts:
      - path: "2_Scripts/1_Sample/1.2_LinkEntities.py"
        issue: "1090 lines (exceeds 800 limit)"
    missing:
      - "Further refactoring to extract inline functions"
      - "Consider splitting large scripts into sub-modules"
```

### Anti-Patterns to Avoid
- **Template-only verification:** Don't just copy the template without verifying actual artifacts
- **File existence ≠ implementation:** A file existing doesn't mean the feature works
- **Ignoring wiring:** Stubs can hide in components that exist but aren't connected
- **Vague evidence:** Always provide specific file paths, line numbers, or grep patterns
- **Missing status values:** Frontmatter must have status (passed/gaps_found/human_needed)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Verification automation | Manual grep commands | gsd-verifier agent | Handles must-haves extraction, multi-level checks, wiring verification |
| Stub detection patterns | Custom regex | verification-patterns.md reference | Covers TODO/FIXME, placeholder text, empty returns for all artifact types |
| Report structure | Manual markdown | verification-report.md template | Standard sections, status values, evidence formatting |
| Gap categorization | Ad-hoc severity | Defined severity levels (blocker/warning/info) | Consistent gap classification across all phases |

**Key insight:** Verification requires systematic, pattern-based checking. Manual verification misses subtle stubs and wiring issues. The GSD framework provides all necessary patterns and templates - use them.

## Common Pitfalls

### Pitfall 1: Confusing Task Completion with Goal Achievement
**What goes wrong:** Reporting "all tasks completed" when artifacts are stubs or unwired
**Why it happens:** Tasks can be marked done (file created) without functionality working
**How to avoid:** Use goal-backward verification - start from phase goal, derive truths, verify enabling artifacts
**Warning signs:** Verification report says "all tasks done" but no observable truths verified

### Pitfall 2: Ignoring Wiring Verification
**What goes wrong:** Verifying artifacts exist but not checking if they're connected
**Why it happens:** Easy to check file existence, harder to trace wiring
**How to avoid:** Always verify key links - imports, API calls, database queries, state-to-render
**Warning signs:** All artifacts "EXISTS + SUBSTANTIVE" but no key links "WIRED"

### Pitfall 3: Missing Stub Patterns
**What goes wrong:** Not detecting TODO/FIXME comments, placeholder text, empty returns
**Why it happens:** File looks substantial at line count but has stub content
**How to avoid:** Run anti-pattern scans using grep patterns from verification-patterns.md
**Warning signs:** Files with 50+ lines but still marked "TODO: implement" inside

### Pitfall 4: Vague Evidence
**What goes wrong:** Reporting "file exists" without specifying path or what it provides
**Why it happens:** Quick verification doesn't capture specifics
**How to avoid:** Always include file paths, line numbers, grep patterns, or specific evidence
**Warning signs:** Evidence column contains "exists" or "working" without details

### Pitfall 5: Incorrect Must-Haves Derivation
**What goes wrong:** Verifying wrong truths not tied to phase goal
**Why it happens:** Not reading ROADMAP.md goal or PLAN.md frontmatter
**How to avoid:** Always derive must-haves from phase goal first (or use PLAN.md frontmatter if provided)
**Warning signs:** Truths don't relate to stated phase goal

## Code Examples

Verified patterns from GSD verification workflow:

### Extract Must-Haves from PLAN.md Frontmatter
```bash
# Source: ~/.config/opencode/get-shit-done/workflows/verify-phase.md
grep -l "must_haves:" "$PHASE_DIR"/*-PLAN.md

# Extract truths
grep -A 10 "must_haves:" "$PLAN_FILE" | grep -A 5 "truths:"

# Extract artifacts
grep -A 10 "must_haves:" "$PLAN_FILE" | grep -A 5 "artifacts:"

# Extract key links
grep -A 10 "must_haves:" "$PLAN_FILE" | grep -A 5 "key_links:"
```

### Check File Existence
```bash
# Source: ~/.config/opencode/get-shit-done/workflows/verify-phase.md
check_exists() {
  local path="$1"
  if [ -f "$path" ]; then
    echo "EXISTS"
  elif [ -d "$path" ]; then
    echo "EXISTS (directory)"
  else
    echo "MISSING"
  fi
}
```

### Detect Stub Patterns
```bash
# Source: ~/.config/opencode/get-shit-done/references/verification-patterns.md
check_stubs() {
  local path="$1"

  # Universal stub patterns
  local stubs=$(grep -c -E "TODO|FIXME|placeholder|not implemented|coming soon" "$path" 2>/dev/null || echo 0)

  # Empty returns
  local empty=$(grep -c -E "return null|return undefined|return \{\}|return \[\]" "$path" 2>/dev/null || echo 0)

  # Placeholder content
  local placeholder=$(grep -c -E "will be here|placeholder|lorem ipsum" "$path" 2>/dev/null || echo 0)

  local total=$((stubs + empty + placeholder))
  [ "$total" -gt 0 ] && echo "STUB_PATTERNS ($total found)" || echo "NO_STUBS"
}
```

### Verify Wiring (Import and Usage)
```bash
# Source: ~/.config/opencode/get-shit-done/workflows/verify-phase.md
check_imported() {
  local artifact_name="$1"
  local search_path="${2:-src/}"

  # Find imports of this artifact
  local imports=$(grep -r "import.*$artifact_name" "$search_path" --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l)

  [ "$imports" -gt 0 ] && echo "IMPORTED ($imports times)" || echo "NOT_IMPORTED"
}

check_used() {
  local artifact_name="$1"
  local search_path="${2:-src/}"

  # Find usages (function calls, component renders, etc.)
  local uses=$(grep -r "$artifact_name" "$search_path" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "import" | wc -l)

  [ "$uses" -gt 0 ] && echo "USED ($uses times)" || echo "NOT_USED"
}
```

### Calculate Verification Status
```bash
# Source: ~/.config/opencode/get-shit-done/workflows/verify-phase.md
determine_status() {
  local verified_truths=$1
  local total_truths=$2
  local blocker_gaps=$3

  if [ $blocker_gaps -gt 0 ]; then
    echo "gaps_found"
  elif [ $verified_truths -eq $total_truths ]; then
    echo "passed"
  else
    echo "gaps_found"
  fi
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual verification without templates | Structured VERIFICATION.md with template | GSD framework initial release | Consistent report format across all phases |
| Task-based verification (tasks done = phase done) | Goal-backward verification (truths verified = goal achieved) | GSD framework initial release | Detects stubs and unwired artifacts |
| No gap documentation | Structured gap documentation with status/artifacts/missing | GSD framework initial release | Clear gap tracking and fix planning |
| Ad-hoc stub detection | Pattern-based stub detection (verification-patterns.md) | GSD framework initial release | Systematic stub identification across artifact types |

**Current best practices:**
- Use gsd-verifier agent for automated verification
- Follow VERIFICATION.md template from Phase 01
- Derive must-haves from PLAN.md frontmatter or phase goals
- Document all gaps with specific evidence
- Provide fix plan recommendations when gaps_found

**Not deprecated:**
- Manual verification for phases without PLAN.md must-haves (derive from goal)
- Human verification for UI/UX, performance, external integrations

## Open Questions

None. The verification methodology, templates, and patterns are well-documented in the GSD framework. All 13 phases needing verification have PLAN.md files with must_haves defined, enabling straightforward automated verification.

## Sources

### Primary (HIGH confidence)
- `~/.config/opencode/get-shit-done/workflows/verify-phase.md` - Complete verification workflow with all steps
- `~/.config/opencode/get-shit-done/templates/verification-report.md` - Standard report template with all sections
- `~/.config/opencode/get-shit-done/references/verification-patterns.md` - Stub detection and wiring verification patterns
- `.planning/phases/01-template-pilot/01-TEMPLATE-VERIFICATION.md` - Working example from Phase 1
- `.planning/phases/01-template-pilot/01-01-PLAN.md` - Example must_haves in frontmatter

### Secondary (MEDIUM confidence)
- `.planning/phases/07-critical-bug-fixes/07-VERIFICATION.md` - Example of passed verification with all must-haves
- `.planning/phases/13-script-refactoring/13-VERIFICATION.md` - Example of gaps_found verification with structured gap documentation
- `.planning/phases/15-scaling-preparation/15-scaling-preparation-VERIFICATION.md` - Example of multi-plan verification with detailed findings

### Tertiary (LOW confidence)
- Phase PLAN.md files (2, 3, 4, 5, 6, 8, 10, 11, 12) - Must_haves extracted during verification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All GSD verification tools and patterns documented
- Architecture: HIGH - Verification workflow and templates are well-defined
- Pitfalls: HIGH - Common verification mistakes documented with prevention strategies
- Code examples: HIGH - All examples copied from GSD documentation

**Research date:** 2026-01-23
**Valid until:** 90 days (GSD framework is stable, verification patterns are well-established)
