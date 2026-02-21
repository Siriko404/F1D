# Dependencies

This document tracks all dependencies in the F1D data processing pipeline, including version pinning rationale, compatibility constraints, and upgrade procedures.

## Core Dependencies

### pandas
- **Version**: 2.2.3 (pinned)
- **Purpose**: Primary data manipulation library
- **Compatibility**: Python 3.8+ (supports target range 3.8-3.13)
- **Usage**: All scripts use pandas for DataFrame operations
- **Rationale**: Stable release with good performance for typical dataset sizes

### numpy
- **Version**: 2.3.2 (pinned)
- **Purpose**: Numerical computing foundation
- **Compatibility**: Python 3.9+ (supports target range 3.8-3.13 with numpy<2 for Python 3.8)
- **Usage**: Used by pandas and statistical libraries

### scipy
- **Version**: 1.16.1 (pinned)
- **Purpose**: Scientific computing and statistical functions
- **Compatibility**: Python 3.9+
- **Usage**: Statistical tests, distributions

### statsmodels
- **Version**: 0.14.6 (pinned)
- **Purpose**: Statistical modeling and econometrics
- **Compatibility**: Python 3.8+
- **Usage**: Fixed effects OLS regression, model diagnostics
- **Rationale**:
  - 0.14.x series provides stable API for regression models
  - 0.14.0 introduced breaking changes (deprecated GLM link names)
  - Pinned to 0.14.6 for reproducible regression analysis
  - Future upgrades require API compatibility validation (see UPGRADE_GUIDE.md)

### scikit-learn
- **Version**: 1.7.2 (pinned)
- **Purpose**: Machine learning utilities
- **Compatibility**: Python 3.8+
- **Usage**: Not directly used in pipeline but available for future work

### lifelines
- **Version**: 0.30.0 (pinned)
- **Purpose**: Survival analysis (hazard models)
- **Compatibility**: Python 3.8+
- **Usage**: Cox proportional hazards regression for takeover risk models

### PyYAML
- **Version**: 6.0.2 (pinned)
- **Purpose**: YAML configuration file parsing
- **Compatibility**: Python 3.6+
- **Usage**: Reading config/project.yaml

### PyArrow
- **Version**: 21.0.0 (pinned)
- **Purpose**: Parquet file read/write engine (used by pandas)
- **Compatibility**: Python 3.8+ (supports target range 3.8-3.13)
- **Rationale**:
  - 23.0.0+ requires Python >= 3.10 (incompatible with target range)
  - 21.0.0 provides stable performance and compatibility
- **Performance**:
  - Current version: Performs well for typical dataset sizes
  - Future upgrades: Require benchmarking before deployment
  - See UPGRADE_GUIDE.md for performance testing procedure
- **Usage**: All scripts use pandas.read_parquet() which leverages PyArrow engine
- **Scripts affected**: All scripts reading/writing Parquet files

### openpyxl
- **Version**: 3.1.5 (pinned)
- **Purpose**: Excel file I/O
- **Compatibility**: Python 3.8+
- **Usage**: Not directly used in pipeline but available for future work

### psutil
- **Version**: 7.2.1 (pinned)
- **Purpose**: System and process monitoring
- **Compatibility**: Python 3.6+ (cross-platform)
- **Usage**: Memory tracking, CPU monitoring, disk space checking
- **Rationale**: Added in Phase 12 for observability features

### python-dateutil
- **Version**: 2.9.0.post0 (pinned)
- **Purpose**: Date parsing and manipulation
- **Compatibility**: Python 3.7+
- **Usage**: Date parsing in data processing scripts

### rapidfuzz
- **Version**: >=3.14.0 (minimum)
- **Purpose**: Fast fuzzy string matching
- **Compatibility**: Python 3.8+
- **Usage**: Fuzzy entity linking (CUSIP, ticker, company names)
- **Rationale**: MIT-licensed, 10x faster than fuzzywuzzy
- **Status**: Optional dependency - pipeline works without it (falls back to exact matching)
- **Scripts affected**: 1.2_LinkEntities.py

## Version Pinning Rationale

### Strict Pinning (==)
These versions are pinned to ensure reproducibility and prevent unexpected changes:
- **All dependencies** are pinned to exact versions for reproducibility
- PyArrow pinned to 21.0.0 for maximum Python version compatibility
  - Future upgrades require Python 3.10+ support validation
  - Performance benchmarking required for upgrades (see UPGRADE_GUIDE.md)

### Minimum Version (>=)
Only used for optional dependencies:
- rapidfuzz: >=3.14.0 (optional dependency for fuzzy matching)

## Python Compatibility

**Supported Versions**: Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

**Minimum Version**: Python 3.8
**Latest Tested**: Python 3.13

**Rationale**:
- Broad compatibility ensures pipeline works on various environments
- Python 3.8 is oldest stable version still receiving security updates
- All dependencies support Python 3.8-3.13 range

**Dependency Constraints**:
- PyArrow 21.0.0 supports Python 3.8+ (compatible)
- PyArrow 23.0.0+ requires Python 3.10+ (not compatible with 3.8-3.9)
- NumPy 2.x and Pandas 2.x support Python 3.9+
- Current pinned versions: PyArrow 21.0.0, NumPy 2.3.2, Pandas 2.2.3 (all compatible)

**Testing**:
- GitHub Actions tests all supported versions on every push/PR
- Matrix: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- See `.github/workflows/test.yml` for CI/CD configuration

**Version Pinning in requirements.txt**:
- Python version range specified as comment: `# Python >= 3.8`
- Actual version controlled by user environment

**For Users**:
- Recommended: Python 3.10 or 3.11 for best performance
- Minimum: Python 3.8 (fully supported)
- See UPGRADE_GUIDE.md for Python upgrade procedures

## Python Version Support (Legacy)

### Target Range: 3.8 - 3.13

All dependencies selected to support this range:
- Python 3.8: Minimum required by the pipeline
- Python 3.9-3.11: Fully supported
- Python 3.12-3.13: Fully supported

**Known constraints:**
- PyArrow 23.0.0+ requires Python >= 3.10
- numpy 2.0+ requires Python >= 3.9 (use numpy<2 for Python 3.8)

## Dependency Constraints

### Transitive Dependencies
These are managed automatically by pip:
- All transitive dependencies resolved during installation
- No explicit pinning of transitive dependencies
- Review pip freeze output for full dependency tree

### Platform-Specific Considerations
- Windows: Symlink operations use junctions (handled by symlink_utils.py)
- Unix: Standard symlink operations
- Cross-platform: pathlib.Path used throughout for path operations

## Upgrade Strategy

See UPGRADE_GUIDE.md for detailed upgrade procedures including:
- PyArrow upgrade with performance benchmarking
- statsmodels upgrade with API compatibility checks
- Python version upgrade with dependency compatibility validation
- Minimum risk upgrade process

## Dependency Security

### Current Status
All dependencies are from trusted sources (PyPI) with stable maintainers:
- Regular updates checked for security patches
- No known vulnerabilities in current versions

### Security Updates
When security patches are released:
1. Review changelog for breaking changes
2. Test in isolated environment
3. Run full pipeline with test data
4. Verify outputs match baseline (checksum validation)
5. Update pinned version and commit

## Optional Dependencies

### RapidFuzz
- **Version**: >=3.14.0 (optional, not pinned)
- **Purpose**: Fuzzy string matching for entity linking (Tier 3 matching)
- **Required**: No (graceful degradation)
- **Impact if Missing**:
  - Tier 3 fuzzy name matching disabled
  - Lower entity match rate (Tier 1 and Tier 2 still work)
  - Pipeline completes successfully but with fewer matches
- **Performance**:
  - Without: Tier 3 matching returns no matches (fast but incomplete)
  - With: Fuzzy matching with configurable thresholds (slower but more matches)
  - Typical speedup: 10-50x for large company name datasets vs. manual implementation
- **Graceful Degradation**:
  - Import warning logged if unavailable
  - Functions return (query, 0.0) instead of fuzzy matches
  - No errors or pipeline failures
- **Usage**:
  - f1d.sample.1.2_LinkEntities (Tier 3 fuzzy matching)
  - f1d.shared.string_matching (core matching utilities with RAPIDFUZZ_AVAILABLE flag)
- **Installation**: `pip install rapidfuzz>=3.14.0`

## Version Pinning Rationale

| Dependency | Pinning Strategy | Rationale |
|------------|-----------------|-----------|
| pandas | Pinned to 2.2.3 | Stable release with good performance for typical dataset sizes |
| numpy | Pinned to 2.3.2 | Stable release, supports target Python range |
| scipy | Pinned to 1.16.1 | Stable release for statistical functions |
| statsmodels | Pinned to 0.14.6 | Reproducible regression analysis, avoids breaking changes |
| scikit-learn | Pinned to 1.7.2 | Stable release, future use |
| lifelines | Pinned to 0.30.0 | Stable release for hazard models |
| PyYAML | Pinned to 6.0.2 | Stable configuration parsing |
| pyarrow | Pinned to 21.0.0 | Python 3.8-3.13 compatibility |
| openpyxl | Pinned to 3.1.5 | Excel read/write support |
| psutil | Pinned to 7.2.1 | Cross-platform system monitoring |
| python-dateutil | Pinned to 2.9.0.post0 | Stable date parsing |
| RapidFuzz | Optional, >=3.14.0 (not pinned) | Graceful degradation pattern allows pipeline to run without it; recommended for production use (higher match rates) |

## Performance Impact

### PyArrow Performance
- **Current version**: 21.0.0
- **Performance**: Good for typical dataset sizes (1GB - 10GB Parquet files)
- **Memory usage**: Efficient columnar format
- **Future upgrades**: Benchmark before deployment (see UPGRADE_GUIDE.md)

### psutil Impact
- **Current version**: 7.2.1
- **Performance**: Minimal overhead for memory/CPU monitoring
- **Usage**: Observability features in all scripts (Phase 12)

### RapidFuzz Impact
- **Current version**: >=3.14.0 (optional)
- **Performance**: 10-50x speedup for fuzzy matching vs. manual implementation
- **Graceful Degradation**: Pipeline runs without it (RAPIDFUZZ_AVAILABLE flag)
- **Match Rate Impact**:
  - Without RapidFuzz: Tier 3 fuzzy matching disabled (only Tier 1 exact and Tier 2 partial matching)
  - With RapidFuzz: Tier 3 fuzzy matching enabled (higher overall entity match rates)
- **Usage**: Entity linking (f1d.sample.1.2_LinkEntities) and string matching utilities (f1d.shared.string_matching)
- **Installation**: Optional but recommended for production use

## Dependency Matrix

| Dependency | Version | Min Python | Used By | Pinned |
|-----------|---------|------------|---------|--------|
| pandas | 2.2.3 | 3.8 | All scripts | Yes |
| numpy | 2.3.2 | 3.9 | All scripts | Yes |
| scipy | 1.16.1 | 3.9 | All scripts | Yes |
| statsmodels | 0.14.6 | 3.8 | Step 4 scripts | Yes |
| scikit-learn | 1.7.2 | 3.8 | Future use | Yes |
| lifelines | 0.30.0 | 3.8 | f1d.econometric.v1.4.3_TakeoverHazards | Yes |
| PyYAML | 6.0.2 | 3.6 | All scripts | Yes |
| PyArrow | 21.0.0 | 3.8 | All scripts | Yes |
| openpyxl | 3.1.5 | 3.8 | Future use | Yes |
| psutil | 7.2.1 | 3.6 | All scripts | Yes |
| python-dateutil | 2.9.0.post0 | 3.7 | All scripts | Yes |
| rapidfuzz | >=3.14.0 | 3.8 | f1d.sample.1.2_LinkEntities | No (minimum) |

---

*Last updated: 2026-02-20*
*See also: requirements.txt, UPGRADE_GUIDE.md*
