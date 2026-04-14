"""Pydantic schema for suite_spec.json — canonical per-suite metadata.

Every field in a suite_spec.json file must trace back to a single runtime
source in the runner that computed the regression. The schema enforces
drift-prevention via strict validation: renderers refuse malformed input,
and extra fields are forbidden at every level.

Schema version: 1.0
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

TailDirection = Literal["positive", "negative", "none"]
TailAppliesTo = Literal["ivs_only", "all"]
IVTail = Literal["one_pos", "one_neg", "two"]
FEEntity = Literal["industry", "firm", "none"]
FETime = Literal["year", "year_quarter", "calendar_year", "calendar_year_quarter", "none"]
SuiteType = Literal["standard", "moderation", "logit", "firm_year"]
ModelFamily = Literal["PanelOLS", "Logit", "LPM", "OLS"]


# ---------------------------------------------------------------------------
# Leaf models
# ---------------------------------------------------------------------------


class Coef(BaseModel):
    """Per-column coefficient for a single variable (IV or control)."""

    model_config = ConfigDict(extra="forbid")

    beta: float
    se: float
    p_two: float
    p_one: Optional[float] = None  # None for non-directional / controls under one-tailed


class HeaderCell(BaseModel):
    """A multicolumn header cell (one per group in a header row)."""

    model_config = ConfigDict(extra="forbid")

    label: str
    span: int = Field(ge=1)


class Clustering(BaseModel):
    """Clustering specification + derived footer-note prose."""

    model_config = ConfigDict(extra="forbid")

    entity: bool
    time: bool
    footer_note: str  # Derived by write_suite_spec from entity/time booleans.


class TailSpec(BaseModel):
    """Hypothesis tail direction + derived footer-note prose."""

    model_config = ConfigDict(extra="forbid")

    direction: TailDirection
    applies_to: TailAppliesTo = "ivs_only"
    footer_note: str  # Derived by write_suite_spec from direction/applies_to.


class IV(BaseModel):
    """Top-of-table variable (standard IV, moderator, or interaction term)."""

    model_config = ConfigDict(extra="forbid")

    name: str
    label: str
    tail: IVTail


class Controls(BaseModel):
    """Control variable lists + display labels."""

    model_config = ConfigDict(extra="forbid")

    base: list[str]
    extended_only: list[str] = Field(default_factory=list)
    labels: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Column
# ---------------------------------------------------------------------------


class Column(BaseModel):
    """Per-column metadata + coefficients (one entry per table column)."""

    model_config = ConfigDict(extra="forbid")

    col: int = Field(ge=1)
    dv: str
    fe_entity: FEEntity
    fe_time: FETime
    control_vars: list[str]
    n_obs: int = Field(ge=0)
    n_firms: Optional[int] = Field(default=None, ge=0)
    r2: float
    adj_r2: Optional[float] = None
    dv_mean: Optional[float] = None
    cluster_fallback: bool = False
    indicator_rows: dict[str, str] = Field(default_factory=dict)
    coefs: dict[str, Coef] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Render hints
# ---------------------------------------------------------------------------


class RenderHints(BaseModel):
    """Per-suite rendering overrides."""

    model_config = ConfigDict(extra="forbid")

    decimal_places: int = 4
    skip_adj_r2: bool = False
    r2_label: str = "R^2"
    scaling_note: Optional[str] = None
    time_fe_label: str = "Year FE"
    row_order: list[str] = Field(
        default_factory=lambda: [
            "ivs",
            "midrule",
            "controls",
            "midrule",
            "indicators",
            "midrule",
            "summary",
        ]
    )


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


class SuiteSpec(BaseModel):
    """Canonical per-suite (or per-sub-table) metadata for table rendering.

    Every field must come from a single runtime source in the runner that
    executed the regression. No fallbacks, no hardcoded overrides, no defaults
    for per-suite-varying fields.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"

    # Identity
    suite_id: str
    dir_name: str
    title: str
    caption: str
    label: str
    sample_label: str
    model_family: ModelFamily
    suite_type: SuiteType

    # Spec
    clustering: Clustering
    tail: TailSpec
    ivs: list[IV]
    controls: Controls
    header_rows: list[list[HeaderCell]]
    columns: list[Column]

    # Render
    render_hints: RenderHints = Field(default_factory=RenderHints)

    # --- Cross-field validation ---

    @model_validator(mode="after")
    def _columns_sum_to_header_span(self) -> "SuiteSpec":
        if not self.header_rows:
            raise ValueError("header_rows must not be empty")
        top_row_span = sum(cell.span for cell in self.header_rows[0])
        if top_row_span != len(self.columns):
            raise ValueError(
                f"Top header row spans sum to {top_row_span} but "
                f"{len(self.columns)} columns are defined"
            )
        return self

    @model_validator(mode="after")
    def _col_numbers_contiguous(self) -> "SuiteSpec":
        expected = list(range(1, len(self.columns) + 1))
        actual = [c.col for c in self.columns]
        if actual != expected:
            raise ValueError(
                f"Column numbers must be contiguous 1..N, got {actual}"
            )
        return self

    @model_validator(mode="after")
    def _iv_coefs_have_p_one(self) -> "SuiteSpec":
        """If tail.direction is directional, every IV's per-col coef must have p_one set."""
        if self.tail.direction == "none":
            return self
        iv_names = {iv.name for iv in self.ivs}
        for col in self.columns:
            for var_name, coef in col.coefs.items():
                if var_name in iv_names and coef.p_one is None:
                    raise ValueError(
                        f"Column {col.col}: IV '{var_name}' has p_one=None "
                        f"but tail.direction is '{self.tail.direction}'"
                    )
        return self

    @model_validator(mode="after")
    def _header_rows_equal_width(self) -> "SuiteSpec":
        """All header rows must span the same total width."""
        top_width = sum(cell.span for cell in self.header_rows[0])
        for i, row in enumerate(self.header_rows[1:], start=2):
            row_width = sum(cell.span for cell in row)
            if row_width != top_width:
                raise ValueError(
                    f"Header row {i} has width {row_width}, top row has {top_width}"
                )
        return self


__all__ = [
    "Clustering",
    "Coef",
    "Column",
    "Controls",
    "FEEntity",
    "FETime",
    "HeaderCell",
    "IV",
    "IVTail",
    "ModelFamily",
    "RenderHints",
    "SuiteSpec",
    "SuiteType",
    "TailAppliesTo",
    "TailDirection",
    "TailSpec",
]
