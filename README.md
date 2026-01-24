# F1D Data Processing Pipeline

Research data processing pipeline that constructs panel datasets for empirical finance research. Processes earnings call transcripts, links entities across databases, computes text-based measures, merges financial controls, and runs econometric analyses. Built for academic replication and thesis work.

## Installation

### Prerequisites

- Python >= 3.8 (tested on Python 3.8-3.13)
- Git (for cloning the repository)

### Core Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

This installs all core dependencies (pandas, numpy, scipy, statsmodels, etc.) needed for pipeline execution.

### Optional Dependencies

**RapidFuzz** (recommended for improved entity matching):
```bash
pip install rapidfuzz>=3.14.0
```

RapidFuzz enables Tier 3 fuzzy name matching in entity linking, which significantly improves match rates for company names with spelling variations or abbreviations. The pipeline runs without RapidFuzz (graceful degradation), but match rates will be lower.

See DEPENDENCIES.md for details on optional dependencies and their impact.

## Scaling and Performance

The F1D pipeline is designed for academic replication with current dataset sizes (~50K transcripts). For larger datasets or performance optimization, see [2_Scripts/SCALING.md](2_Scripts/SCALING.md).

**Quick Tips:**
- **Memory**: Minimum 8GB RAM, recommended 16GB RAM
- **Parallelization**: Set `thread_count: 4` in config for multi-core systems
- **Chunked Processing**: Enable throttling via `config/project.yaml > chunk_processing`
- **Monitoring**: Check `stats.json > memory_mb` for operation-level memory usage

**For 2x-10x datasets**: See [SCALING.md](2_Scripts/SCALING.md) for configuration recommendations.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd F1D
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install rapidfuzz>=3.14.0  # Optional but recommended
   ```

3. **Configure the pipeline:**
   Edit `config/project.yaml` to set paths, seeds, and processing parameters.

4. **Run a sample script:**
   ```bash
   python 2_Scripts/1_Sample/1.1_CleanMetadata.py
   ```

Output files are created in timestamped directories under `4_Outputs/`, with `latest/` symlinks pointing to the most recent run.

## Pipeline Structure

The pipeline follows a 4-stage structure:

1. **Sample** (1_Sample): Build sample manifest, clean metadata, link entities, build tenure map
2. **Text** (2_Text): Tokenize transcripts, construct text variables, verify outputs
3. **Financial** (3_Financial): Build financial features, firm controls, market variables, event flags
4. **Econometric** (4_Econometric): Run regressions for CEO clarity, tone, liquidity effects

See ROADMAP.md for detailed phase-by-phase documentation.

## Documentation

- **DEPENDENCIES.md**: Complete dependency documentation, version pinning rationale, and upgrade procedures
- **UPGRADE_GUIDE.md**: Instructions for upgrading dependencies with compatibility validation
- **ROADMAP.md**: Project phases, plans, and progress tracking
- **.planning/STATE.md**: Current project position and accumulated decisions

## Output Reproducibility

Every script produces:
- **Console output**: Progress statistics (row counts, timing, missing values)
- **Stats files**: `stats.json` in output directories with detailed metrics
- **Checksums**: SHA-256 file checksums for output verification

All outputs are deterministic for a given input and configuration (see `config/project.yaml` for seed settings).

## License

[Specify your license here]

## Contact

For questions or issues, please contact [your contact information].
