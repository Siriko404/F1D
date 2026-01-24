# Phase 21: Fix Testing Infrastructure - Context

**Gathered:** 2026-01-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix environment configuration and test code issues preventing integration tests from running. Closes gaps from v1.2.0-MILESTONE-AUDIT.md: PYTHONPATH issues in subprocess calls, AST parsing bugs in observability tests.

This phase does NOT add new testing capabilities. It fixes existing test infrastructure so tests can run and pass.

</domain>

<decisions>
## Implementation Decisions

### PYTHONPATH Configuration Approach

**Decision:** Use module-level constant with absolute path (`SUBPROCESS_ENV`)

Add to each integration test file (test_full_pipeline.py, test_pipeline_step1.py, test_pipeline_step2.py, test_pipeline_step3.py, test_observability_integration.py):

```python
import os

SUBPROCESS_ENV = {
    "PYTHONPATH": str(REPO_ROOT / "2_Scripts"),
    **os.environ  # Preserve existing environment variables
}
```

Use in all `subprocess.run()` calls:

```python
result = subprocess.run(
    ["python", str(script_path)],
    env=SUBPROCESS_ENV,
    capture_output=True,
    text=True,
)
```

**Why this approach:**
- **DRY principle:** Single source of truth, no duplication across 5 integration test files
- **Explicit:** Clear intent to all readers
- **Absolute paths:** Works from any working directory (cross-platform compatibility)
- **Preserves environment:** `**os.environ` ensures PATH, HOME, and other variables remain intact
- **Follows existing pattern:** Phase 19 successfully used `REPO_ROOT` constant in same test files

**Alternatives considered and rejected:**
- Per-call inline env dict: Violates DRY, easy to miss one subprocess call
- Test fixture: Overkill, unnecessary complexity for simple environment variable
- Relative paths: Breaks when running tests from different directories

### AST Parsing Replacement Strategy

**Decision:** Use regex pattern matching with file read (replace fragile AST parsing)

Replace broken AST parsing in `test_observability_integration.py` with robust regex checks:

```python
import re

def check_script_observability(script_path):
    """Verify observability features via regex pattern matching."""
    with open(script_path) as f:
        content = f.read()

    # Check required imports
    assert re.search(r'^import psutil\b', content, re.MULTILINE), "Missing psutil import"
    assert re.search(r'^from shared\.path_utils import', content, re.MULTILINE), "Missing path_utils import"

    # Check required functions
    assert re.search(r'^def get_process_memory_mb\(', content, re.MULTILINE), "Missing memory tracking"
    assert re.search(r'^def calculate_throughput\(', content, re.MULTILINE), "Missing throughput calculation"
    assert re.search(r'^def detect_anomalies_zscore\(', content, re.MULTILINE), "Missing z-score anomaly detection"
    assert re.search(r'^def detect_anomalies_iqr\(', content, re.MULTILINE), "Missing IQR anomaly detection"
```

Completely remove broken AST parsing logic (lines 32-51 and 55-91).

**Why this approach:**
- **Simple and maintainable:** Easy to understand and debug
- **Resilient to formatting:** Works with different code styles and indentation
- **Fast:** No AST parsing overhead, just text matching
- **Explicit patterns:** Clear what observability features we're checking for
- **Proven in codebase:** Similar pattern already used successfully (e.g., `REPO_ROOT = Path(__file__).parent.parent.parent`)

**Alternatives considered and rejected:**
- Direct module imports with runtime checks: Requires scripts to be importable without execution, might fail on import-time code (dual writers, path validation, etc.)
- Inspect module approach: Same importability issue, more complex than regex for this simple use case
- Fix current AST parsing: Still brittle and over-engineered for checking if functions exist

### Verification Scope

**Decision:** Verify integration tests pass locally (Python 3.10) and confirm CI/CD workflow configuration

**What to verify:**
1. Run all integration tests locally: `pytest tests/integration/ -v -m integration --tb=short`
2. Confirm tests pass without `ModuleNotFoundError` (PYTHONPATH fix verified)
3. Confirm observability tests pass without AST parsing errors (regex fix verified)
4. Verify CI/CD workflow is unchanged (matrix testing already configured)

**What NOT to verify:**
- Don't test multiple Python versions locally (CI/CD already handles matrix testing)
- Don't run E2E tests in this phase (already tested in Phase 16, Phase 21 fixes only test code)
- Don't add new test cases (scope is fixing existing broken tests)

**Why this scope:**
- **CI/CD already handles version matrix:** `.github/workflows/test.yml` line 14 shows Python 3.8-3.13 matrix
- **E2E already singled out:** Line 72 shows E2E tests run only on 3.10 for speed
- **Focus on actual fixes:** Phase 21 goal is fixing PYTHONPATH and AST parsing, not expanding coverage
- **Efficient:** Don't duplicate what CI/CD already does

### OpenCode's Discretion

- Exact test command invocation and flags for verification step
- Whether to add additional logging in subprocess calls for debugging
- Organization of regex patterns (inline function vs. separate test utility module)

</decisions>

<specifics>
## Specific Ideas

**No specific implementation preferences** — use standard Python testing practices.

The phase fixes technical bugs, not a user-facing feature. Follow existing patterns from Phase 19 (REPO_ROOT constant usage, path construction) and maintain consistency with codebase style.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope (fixing test infrastructure, not adding capabilities).

</deferred>

---

*Phase: 21-fix-testing-infrastructure*
*Context gathered: 2026-01-24*
