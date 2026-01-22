# Coding Conventions

**Analysis Date:** 2026-01-22

## Naming Patterns

**Files:**
- Pattern: `<Stage>.<Step>[.<Substep>]_<PascalCaseName>.<ext>`
- Example: `1.0_BuildSampleManifest.py`, `2.1_TokenizeAndCount.py`
- Stages: `1_Inputs`, `2_Scripts`, `3_Logs`, `4_Outputs`

**Functions:**
- Python: `snake_case` (e.g., `load_config`, `setup_paths`)
- Classes: `PascalCase` (e.g., `DualWriter`)

**Variables:**
- `snake_case` (e.g., `config_path`, `output_base`)
- Constants (implied): `UPPER_CASE` (though not heavily used in sample)

**Directories:**
- Root: Numbered stages (`1_Inputs`, `2_Scripts`)
- Scripts: Numbered steps or categories (`1_Sample`, `2_Text`)
- Outputs: `Stage.Step_Name` mirroring the script name

## Code Style

**Formatting:**
- Pythonic (PEP 8 style observed but no explicit config found)
- Indentation: 4 spaces
- No explicit formatter config (`black`, `ruff`) found at root

**Linting:**
- No linter config (`flake8`, `pylintrc`) found at root
- Reliance on "Contract Header" structure

**Structure:**
- **Contract Header**: Every script starts with a comment block defining ID, Description, Inputs, Outputs, and Determinism.
- **Dual-Writer**: Custom `DualWriter` class captures `sys.stdout` to write to both terminal and a log file simultaneously.
- **Config-Driven**: Hardcoded paths are avoided; `config/project.yaml` is the source of truth.

## Import Organization

**Order:**
1. Standard Library (`sys`, `os`, `pathlib`, `datetime`)
2. Third-party (`yaml`, `shutil`)
3. Local (None observed in sample, as logic is self-contained or orchestrated via subprocess)

**Path Handling:**
- Use `pathlib.Path` over `os.path`
- Resolve paths relative to `__file__` or `config/project.yaml`

## Error Handling

**Patterns:**
- **Fail Fast**: Scripts validate inputs and paths early.
- **Subprocess Checks**: Orchestrators check `returncode` of subprocesses.
- **Exit Codes**: Return `0` for success, `1` for failure.
- **Logging**: Errors are caught and logged via the DualWriter before exit.

## Logging

**Framework:** Custom `DualWriter` class (no `logging` module configuration in script, though config defines levels).

**Patterns:**
- **Location**: `3_Logs/<Script_Name>/<Timestamp>.log`
- **Mirroring**: Everything printed to stdout must go to the log file.
- **Start/End**: Scripts log start time, configuration snapshot, and completion status.

## Comments

**Header**:
- Mandatory "Contract Header" at the top of the file.

**Inline**:
- Used for major sections ("Configuration and setup", "Orchestration").
- Explains "why" for complex logic (e.g., "Directory junction on Windows").

## Function Design

**Orchestrators:**
- `main()` function handles high-level flow.
- Delegates work to substeps via `subprocess.run`.

**Scope:**
- Scripts are designed to be "Direct-run", meaning they are self-contained executable units rather than importable libraries.

## Module Design

**Configuration:**
- Single `config/project.yaml` handles all constants, paths, and toggles.
- Scripts load this config immediately upon execution.

**Output Management:**
- Scripts create their own timestamped output directories.
- Scripts manage a `latest` symlink (or copy) to the most recent run.
