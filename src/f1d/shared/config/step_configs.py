"""Step-specific configuration classes for F1D pipeline.

This module provides type-safe configuration classes for each pipeline step.
Each step configuration inherits from BaseSettings and validates fields at load time.

Classes are designed to load from config/project.yaml step_XX sections.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StepOutputSettings(BaseSettings):
    """Common output pattern for step configurations.

    Attributes:
        output_subdir: Subdirectory name for step outputs.
        outputs: Dictionary mapping output names to file names/patterns.
    """

    model_config = SettingsConfigDict(extra="ignore")

    # Note: output_subdir is typically at step level, not nested in outputs
    # This class holds the outputs dictionary only
    pass


class BaseStepConfig(BaseSettings):
    """Base class for all step configurations.

    Provides common fields and configuration settings for pipeline steps.

    Attributes:
        enabled: Whether this step is enabled.
        output_subdir: Subdirectory name for step outputs.
    """

    model_config = SettingsConfigDict(extra="ignore")

    enabled: bool = Field(default=True, description="Whether this step is enabled")
    output_subdir: str = Field(description="Output subdirectory for this step")


class Step00Config(BaseStepConfig):
    """Configuration for Step 00: Unified Info Check.

    Attributes:
        outputs: Dictionary of output file names.
    """

    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step00bConfig(BaseStepConfig):
    """Configuration for Step 00b: Build Master Tenure Map.

    Attributes:
        outputs: Dictionary of output file names.
    """

    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step00cConfig(BaseStepConfig):
    """Configuration for Step 00c: Build Monthly Tenure Panel.

    Attributes:
        outputs: Dictionary of output file names.
    """

    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step01Config(BaseStepConfig):
    """Configuration for Step 01: Build LM Clarity Dictionary.

    Attributes:
        selection: Selection thresholds for dictionary terms.
        normalization: Text normalization settings.
        outputs: Dictionary of output file names.
    """

    selection: Dict[str, int] = Field(
        default_factory=lambda: {"uncertainty_threshold": 0, "weak_modal_threshold": 0},
        description="Selection thresholds",
    )
    normalization: Dict[str, str] = Field(
        default_factory=lambda: {"case": "upper", "pattern": "[A-Z]+"},
        description="Normalization settings",
    )
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step02Config(BaseStepConfig):
    """Configuration for Step 02: Extract Filtered Documents.

    Attributes:
        context_filter: Context filter for document extraction (qa, pres, etc.).
        managerial_roles: List of managerial role keywords.
        exclusion_keywords: Keywords to exclude from results.
        duplicate_selection: Settings for duplicate handling.
        outputs: Dictionary of output file names.
    """

    context_filter: str = Field(default="qa", description="Context filter")
    managerial_roles: List[str] = Field(
        default_factory=list, description="Managerial role keywords"
    )
    exclusion_keywords: List[str] = Field(
        default_factory=list, description="Keywords to exclude"
    )
    duplicate_selection: Dict[str, List[str]] = Field(
        default_factory=dict, description="Duplicate selection settings"
    )
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step02_5Config(BaseStepConfig):
    """Configuration for Step 02_5: Link CCM and Industries.

    Attributes:
        outputs: Dictionary of output file names/patterns.
    """

    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step02_5bConfig(BaseStepConfig):
    """Configuration for Step 02_5b: Link Calls to CEO.

    Attributes:
        outputs: Dictionary of output file names/patterns.
    """

    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step02_5cConfig(BaseStepConfig):
    """Configuration for Step 02_5c: Filter Calls and CEOs.

    Attributes:
        min_calls_threshold: Minimum number of calls for a CEO.
        event_type_filter: Event type filter string.
        outputs: Dictionary of output file names/patterns.
    """

    min_calls_threshold: int = Field(
        default=5, ge=1, description="Minimum calls per CEO"
    )
    event_type_filter: str = Field(default="1", description="Event type filter")
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step03Config(BaseStepConfig):
    """Configuration for Step 03: Tokenize and Count.

    Attributes:
        tokenization: Tokenization settings.
        top_matches_count: Number of top matches to return.
        compiler: Compiler settings for native code.
        outputs: Dictionary of output file names.
    """

    tokenization: Dict[str, Any] = Field(
        default_factory=lambda: {
            "normalization": "uppercase",
            "non_letter_replacement": " ",
            "collapse_spaces": True,
            "token_pattern": "[A-Z]+",
        },
        description="Tokenization settings",
    )
    top_matches_count: int = Field(
        default=5, ge=1, description="Number of top matches"
    )
    compiler: Dict[str, str] = Field(
        default_factory=lambda: {
            "executable": "g++",
            "standard": "c++17",
            "optimization": "-O2",
            "warnings": "-Wall -Wextra",
        },
        description="Compiler settings",
    )
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step04Config(BaseStepConfig):
    """Configuration for Step 04: Build F1D Panel.

    Attributes:
        measures: Dictionary of measure configurations.
        outputs: Dictionary of output file names.
    """

    measures: Dict[str, Dict[str, str]] = Field(
        default_factory=dict, description="Measure configurations"
    )
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step07Config(BaseStepConfig):
    """Configuration for Step 07: Build Financial Controls.

    Attributes:
        return_windows: Return window settings.
        eps_growth: EPS growth settings.
        surprise_deciles: Surprise decile bin settings.
        outputs: Dictionary of output file names.
    """

    return_windows: Dict[str, int] = Field(
        default_factory=lambda: {
            "days_after_prev_call": 5,
            "days_before_current_call": 5,
            "min_trading_days": 20,
        },
        description="Return window settings",
    )
    eps_growth: Dict[str, Any] = Field(
        default_factory=lambda: {
            "lag_quarters": 4,
            "winsorize_percentiles": [1, 99],
        },
        description="EPS growth settings",
    )
    surprise_deciles: Dict[str, List[List[int]]] = Field(
        default_factory=lambda: {"bins": [[-5], [-4], [-3], [-2], [-1], [0], [1], [2], [3], [4], [5]]},
        description="Surprise decile bins",
    )
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step08Config(BaseStepConfig):
    """Configuration for Step 08: Estimate CEO Clarity.

    Attributes:
        regression: Regression settings including controls and fixed effects.
        outputs: Dictionary of output file names.
    """

    regression: Dict[str, Any] = Field(
        default_factory=lambda: {
            "dependent_var": "MaQaUnc_pct",
            "linguistic_controls": ["MaPresUnc_pct", "AnaQaUnc_pct", "EntireCallNeg_pct"],
            "firm_controls": ["SurpDec", "EPS_Growth", "StockRet", "MarketRet"],
            "fixed_effects": ["CEO_ID", "year"],
            "min_calls_per_ceo": 5,
        },
        description="Regression settings",
    )
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class Step09Config(BaseStepConfig):
    """Configuration for Step 09: Liquidity Analysis.

    Attributes:
        liquidity_measures: Liquidity measure settings.
        inputs: Input file paths.
        outputs: Dictionary of output file names.
    """

    liquidity_measures: Dict[str, Any] = Field(
        default_factory=lambda: {
            "window_days": [[-5], [5]],
            "min_trading_days": 5,
            "winsorize_percentiles": [1, 99],
        },
        description="Liquidity measure settings",
    )
    inputs: Dict[str, str] = Field(
        default_factory=dict, description="Input file paths"
    )
    outputs: Dict[str, str] = Field(default_factory=dict, description="Output file names")


class StepsConfig(BaseSettings):
    """Container class for all step configurations.

    Provides a unified interface to access all step configurations.
    Uses extra="allow" to support dynamic step names.

    Attributes:
        step_00: Step 00 configuration.
        step_00b: Step 00b configuration.
        step_00c: Step 00c configuration.
        step_01: Step 01 configuration.
        step_02: Step 02 configuration.
        step_02_5: Step 02_5 configuration.
        step_02_5b: Step 02_5b configuration.
        step_02_5c: Step 02_5c configuration.
        step_03: Step 03 configuration.
        step_04: Step 04 configuration.
        step_07: Step 07 configuration.
        step_08: Step 08 configuration.
        step_09: Step 09 configuration.
    """

    model_config = SettingsConfigDict(extra="allow")

    step_00: Optional[Step00Config] = None
    step_00b: Optional[Step00bConfig] = None
    step_00c: Optional[Step00cConfig] = None
    step_01: Optional[Step01Config] = None
    step_02: Optional[Step02Config] = None
    step_02_5: Optional[Step02_5Config] = None
    step_02_5b: Optional[Step02_5bConfig] = None
    step_02_5c: Optional[Step02_5cConfig] = None
    step_03: Optional[Step03Config] = None
    step_04: Optional[Step04Config] = None
    step_07: Optional[Step07Config] = None
    step_08: Optional[Step08Config] = None
    step_09: Optional[Step09Config] = None

    def get_step(self, name: str) -> Optional[BaseStepConfig]:
        """Get a step configuration by name.

        Args:
            name: Step name (e.g., 'step_01', 'step_02_5').

        Returns:
            Step configuration if found, None otherwise.
        """
        return getattr(self, name, None)

    def get_enabled_steps(self) -> List[str]:
        """Get list of enabled step names.

        Returns:
            List of step names that are enabled.
        """
        enabled: List[str] = []
        for attr_name in dir(self):
            if attr_name.startswith("step_") and not attr_name.startswith("_"):
                step = getattr(self, attr_name, None)
                if step is not None and hasattr(step, "enabled") and step.enabled:
                    enabled.append(attr_name)
        return enabled
