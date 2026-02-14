"""Factory fixtures for test data generation.

Factories follow the Factory pattern to generate test data on demand,
preventing the "fixture pyramid" anti-pattern where fixtures depend on
other fixtures in complex chains.

Each factory is a function-scoped pytest fixture that returns a callable.
The callable accepts parameters to customize the generated test data.

Benefits:
- Fresh data per test (function-scoped)
- Customizable parameters for different test scenarios
- Consistent random seeds for reproducibility
- No complex fixture dependency chains

Usage:
    def test_compustat_processing(sample_compustat_factory):
        df = sample_compustat_factory(n_firms=10, n_years=5)
        assert len(df) == 50  # 10 firms * 5 years

    def test_config_loading(sample_project_config_factory):
        config = sample_project_config_factory(year_start=2010, year_end=2015)
        assert config.data.year_start == 2010

Available Factories:
    Financial:
        - sample_compustat_factory: Generate Compustat-style panel data
        - sample_panel_data_factory: Generate panel regression test data
        - sample_financial_row_factory: Generate single Compustat row (Series)

    Configuration:
        - sample_config_yaml_factory: Generate temporary YAML config files
        - sample_project_config_factory: Generate ProjectConfig instances
        - sample_env_vars_factory: Generate F1D_* environment variable dicts
        - invalid_config_yaml_factory: Generate intentionally invalid configs
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from pathlib import Path

# Re-export commonly used factories for convenience
__all__ = [
    # Financial factories
    "sample_compustat_factory",
    "sample_panel_data_factory",
    "sample_financial_row_factory",
    # Config factories
    "sample_config_yaml_factory",
    "sample_project_config_factory",
    "sample_env_vars_factory",
    "invalid_config_yaml_factory",
]


def __getattr__(name: str):
    """Lazy import factories to avoid circular imports."""
    if name in __all__:
        if name in ("sample_compustat_factory", "sample_panel_data_factory", "sample_financial_row_factory"):
            from tests.factories.financial import (
                sample_compustat_factory,
                sample_panel_data_factory,
                sample_financial_row_factory,
            )

            return locals()[name]
        elif name in ("sample_config_yaml_factory", "sample_project_config_factory", "sample_env_vars_factory", "invalid_config_yaml_factory"):
            from tests.factories.config import (
                sample_config_yaml_factory,
                sample_project_config_factory,
                sample_env_vars_factory,
                invalid_config_yaml_factory,
            )

            return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
