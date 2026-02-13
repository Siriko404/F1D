# Requirements: F1D Data Pipeline v6.0

**Defined:** 2026-02-13
**Core Value:** Every script must produce verifiable, reproducible results with complete audit trails

## v6.0 Requirements

Requirements for Architecture Standard Implementation. Each maps to roadmap phases.

### Architecture (ARCH)

- [ ] **ARCH-01**: Migrate codebase to src-layout structure (src/f1d/ package)
- [ ] **ARCH-02**: Establish Tier 1/2/3 module classification per ARCHITECTURE_STANDARD.md
- [ ] **ARCH-03**: Organize data directories by lifecycle (raw/interim/processed/external)

### Type Hints (TYPE)

- [ ] **TYPE-01**: Add type hints to all Tier 1 modules (100% coverage required)
- [ ] **TYPE-02**: Add type hints to Tier 2 modules (80% coverage required)
- [ ] **TYPE-03**: Configure mypy with tier-based strictness levels

### Configuration (CONF)

- [ ] **CONF-01**: Implement pydantic-settings base configuration class
- [ ] **CONF-02**: Migrate config/project.yaml settings to typed settings classes
- [ ] **CONF-03**: Add environment variable integration for secrets/overrides

### Logging (LOGG)

- [ ] **LOGG-01**: Integrate structlog for structured JSON logging
- [ ] **LOGG-02**: Implement context binding for request/operation tracking
- [ ] **LOGG-03**: Configure dual output (console human-readable, file JSON)

### CI/CD (CICD)

- [ ] **CICD-01**: Create pyproject.toml with all tool configurations consolidated
- [ ] **CICD-02**: Set up GitHub Actions workflow for lint/test/build
- [ ] **CICD-03**: Configure pre-commit hooks matching CI configuration

### Testing (TEST)

- [ ] **TEST-01**: Establish pytest infrastructure with conftest.py structure
- [ ] **TEST-02**: Add Tier 1 unit tests (90% coverage target)
- [ ] **TEST-03**: Add Tier 2 integration tests (80% coverage target)
- [ ] **TEST-04**: Implement factory fixtures for test data generation

## v7.0 Requirements

Deferred to future release. Tracked but not in current roadmap.

(None identified yet)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time chat/LLM-based uncertainty | Dictionary-based approach per methodology |
| Cross-country analysis | U.S. firms only for thesis scope |
| Video/audio analysis | Text transcripts only |
| Interactive dashboards | Batch processing for replication |
| Adding new features or hypotheses | Thesis research complete, focused on code quality |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 69 | Pending |
| ARCH-02 | Phase 69 | Pending |
| ARCH-03 | Phase 69 | Pending |
| TYPE-01 | Phase 70 | Pending |
| TYPE-02 | Phase 70 | Pending |
| TYPE-03 | Phase 70 | Pending |
| CONF-01 | Phase 71 | Pending |
| CONF-02 | Phase 71 | Pending |
| CONF-03 | Phase 71 | Pending |
| LOGG-01 | Phase 72 | Pending |
| LOGG-02 | Phase 72 | Pending |
| LOGG-03 | Phase 72 | Pending |
| CICD-01 | Phase 73 | Pending |
| CICD-02 | Phase 73 | Pending |
| CICD-03 | Phase 73 | Pending |
| TEST-01 | Phase 74 | Pending |
| TEST-02 | Phase 74 | Pending |
| TEST-03 | Phase 74 | Pending |
| TEST-04 | Phase 74 | Pending |

**Coverage:**
- v6.0 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-13*
*Last updated: 2026-02-13 after initial definition*
