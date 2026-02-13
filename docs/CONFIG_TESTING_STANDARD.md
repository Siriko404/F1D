# F1D Configuration and Testing Standard

**Version:** 5.0
**Last Updated:** 2026-02-13
**Status:** DEFINITION - Implementation deferred to v6.0+
**Milestone:** v5.0 Architecture Standard Definition

---

## Purpose

This document defines the configuration management and testing infrastructure standards for the F1D (Financial Text Analysis) data processing pipeline. It builds on the foundation established in ARCHITECTURE_STANDARD.md (folder structure, module organization) and CODE_QUALITY_STANDARD.md (naming conventions, docstrings) and ensures:

- **Type Safety:** All configuration validated at load time with pydantic-settings
- **Reproducibility:** Outputs are deterministic, versioned, and verifiable
- **Testability:** Code designed for testing from the start
- **Security:** Secrets handled securely, never logged in plain text

This is a **DEFINITION document**. The standards described here represent the target configuration and testing patterns that will be implemented in v6.0+. Current code may not fully comply with all standards.

---

## Document Structure

This standard is organized into 10 main sections:

**Configuration Requirements (CONF-01 to CONF-05):**
1. **Configuration File Structure (CONF-01):** YAML schema with pydantic-settings validation
2. **Environment Variable Handling (CONF-02):** Secrets management with SecretStr
3. **Path Resolution Pattern (CONF-03):** Eliminating sys.path.insert with src-layout
4. **Output Directory Pattern (CONF-04):** Timestamped runs with checksums
5. **Logging Pattern (CONF-05):** Structured logging with structlog

**Testing Requirements (TEST-01 to TEST-05):**
6. **Test Structure (TEST-01):** Unit/integration/regression/e2e/performance tiers
7. **Coverage Targets (TEST-02):** Tier-based coverage requirements
8. **Test Naming Convention (TEST-03):** Descriptive test function names
9. **Fixture Organization (TEST-04):** Hierarchical conftest.py with factory fixtures
10. **Mocking and Test Data (TEST-05):** pytest-mock and test data patterns

Additionally:
- **Appendix A**: Quick Reference Card
- **Appendix B**: Related Standards
- **Appendix C**: Anti-Patterns Summary

---

## How to Use This Standard

### For New Development (v6.0+)

1. Use pydantic-settings for all configuration loading (CONF-01)
2. Handle secrets with SecretStr (CONF-02)
3. Use proper package imports, never sys.path.insert (CONF-03)
4. Create timestamped output directories with checksums (CONF-04)
5. Use structlog for structured logging (CONF-05)
6. Follow test structure conventions (TEST-01)
7. Meet tier-based coverage targets (TEST-02)
8. Use descriptive test names (TEST-03)
9. Organize fixtures hierarchically (TEST-04)
10. Use pytest-mock for test isolation (TEST-05)

### For Current Development (v5.0)

1. Use this standard as reference for understanding the target patterns
2. New code should align with these patterns where feasible
3. Document deviations from the standard
4. Plan for migration to the standard patterns

### For Code Review

1. Check configuration follows pydantic-settings pattern
2. Verify secrets are handled with SecretStr
3. Ensure no sys.path.insert patterns exist
4. Confirm output directories follow timestamped pattern
5. Verify test coverage meets tier requirements
6. Check test names follow naming convention

---

## Design Principles

### 1. Type Safety (Configuration Validation)

All configuration must be validated at load time, not at runtime:

- **Schema enforcement:** Pydantic models define configuration structure
- **Type coercion:** Automatic conversion with validation
- **Fail fast:** Configuration errors caught immediately on startup
- **IDE support:** Type hints enable autocomplete and static analysis

**Implementation:**
- Use pydantic-settings for all configuration
- Define nested settings classes for configuration sections
- Add field validators for business rules
- Never use raw dictionaries for configuration

### 2. Reproducibility (Deterministic Outputs)

Every output must be reproducible and verifiable:

- **Timestamped runs:** Each execution creates unique output directory
- **Checksums:** SHA-256 hashes verify file integrity
- **Configuration capture:** Full configuration saved with outputs
- **Random seeds:** All randomness controlled via configuration

**Implementation:**
- OutputManager creates timestamped directories
- Checksums computed for all output files
- Configuration serialized to output directory
- Random seeds set from configuration

### 3. Testability (Design for Testing)

Code must be designed for testing from the start:

- **Dependency injection:** External dependencies passed, not imported
- **Pure functions:** Prefer functions without side effects
- **Modular design:** Small, testable units
- **Mock-friendly:** External services easy to mock

**Implementation:**
- Use factory fixtures for test data
- Mock external APIs with pytest-mock
- Test edge cases and error paths
- Separate concerns for isolated testing

### 4. Security (Secrets Handling)

Secrets must never be exposed in logs or configuration files:

- **SecretStr:** Passwords and API keys use SecretStr type
- **Environment variables:** Secrets from .env files (gitignored)
- **No logging:** SecretStr values never logged in plain text
- **.env.example:** Template file documents required secrets

**Implementation:**
- Use SecretStr for sensitive configuration
- Access secrets via .get_secret_value() only when needed
- Never log configuration dictionaries directly
- Audit log output for sensitive data

---

## Relationship to Other Standards

This configuration and testing standard builds upon and references:

### ARCHITECTURE_STANDARD.md

**Cross-references:**
- Folder structure for config/ and tests/ directories
- Module tier system (Tier 1, 2, 3) for coverage targets
- src-layout pattern eliminates sys.path.insert
- Version management for configuration versioning

**Key alignment:**
- Configuration files in config/ directory
- Tests in tests/ directory mirroring src/ structure
- Coverage targets aligned with module tiers

### CODE_QUALITY_STANDARD.md

**Cross-references:**
- Naming conventions for test functions
- Type hint requirements per module tier
- Error handling patterns in configuration loading
- Docstring standards for configuration classes

**Key alignment:**
- Test naming follows descriptive pattern
- Configuration classes have Google-style docstrings
- Error handling uses custom exception hierarchy

---

## Scope and Exclusions

### In Scope

- Configuration file structure and validation
- Environment variable handling for secrets
- Path resolution and package imports
- Output directory management
- Structured logging patterns
- Test organization and structure
- Coverage targets and measurement
- Test naming conventions
- Fixture organization patterns
- Mocking and test data patterns

### Out of Scope

- CI/CD pipeline configuration (future phase)
- Deployment and environment provisioning
- Database configuration (not applicable)
- Performance testing specifics (benchmark definitions)

---

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 8.0+ | Testing framework | Industry standard, powerful fixtures, marker system |
| pydantic | 2.0+ | Configuration validation | Type-safe config parsing with validation |
| pydantic-settings | 2.0+ | Environment variable management | Integrates YAML + env vars with secrets handling |
| PyYAML | 6.0+ | YAML parsing | Standard YAML library, already in use |
| structlog | 25.0+ | Structured logging | JSON logs, context binding, performance |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-cov | 5.0+ | Coverage reporting | CI pipelines, local coverage checks |
| pytest-mock | 3.12+ | Mocking utilities | Unit tests requiring mocks |
| coverage.py | 7.0+ | Coverage measurement | Via pytest-cov integration |
| freezegun | 1.4+ | Time mocking | Tests involving timestamps |
| pytest-xdist | 3.5+ | Parallel test execution | Large test suites |

**Installation:**
```bash
pip install pytest>=8.0 pydantic>=2.0 pydantic-settings>=2.0 PyYAML>=6.0 structlog>=25.0 pytest-cov>=5.0
```

---

