"""Dataset configuration classes for F1D pipeline.

This module provides type-safe configuration classes for dataset definitions.
Dataset configurations support context and role filtering settings.

Classes are designed to load from config/project.yaml datasets section.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatasetConfig(BaseSettings):
    """Configuration for a single dataset.

    Datasets define subsets of the corpus based on context and role filters.

    Attributes:
        description: Human-readable description of the dataset.
        context_filter: Context filter (e.g., 'qa', 'pres', None for all).
        role_filter: Role filter (e.g., 'managerial', 'analyst', None for all).
        enabled: Whether this dataset is enabled for processing.

    Example:
        >>> config = DatasetConfig(
        ...     description="Managerial speech in Q&A sections",
        ...     context_filter="qa",
        ...     role_filter="managerial",
        ...     enabled=True
        ... )
        >>> config.context_filter
        'qa'
    """

    model_config = SettingsConfigDict(extra="ignore")

    description: str = Field(default="", description="Dataset description")
    context_filter: Optional[str] = Field(
        default=None, description="Context filter (qa, pres, or None for all)"
    )
    role_filter: Optional[str] = Field(
        default=None, description="Role filter (managerial, analyst, or None for all)"
    )
    enabled: bool = Field(default=True, description="Whether dataset is enabled")


class DatasetsConfig(BaseSettings):
    """Container class for all dataset configurations.

    Provides a unified interface to access dataset configurations.
    Uses extra="allow" to support dynamic dataset names.

    Attributes:
        manager_qa: Manager Q&A dataset configuration.
        manager_pres: Manager presentation dataset configuration.
        analyst_qa: Analyst Q&A dataset configuration.
        entire_call: Entire call dataset configuration.

    Example:
        >>> from pathlib import Path
        >>> config = DatasetsConfig(
        ...     manager_qa=DatasetConfig(description="Manager QA", enabled=True)
        ... )
        >>> config.get_dataset("manager_qa").enabled
        True
    """

    model_config = SettingsConfigDict(extra="allow")

    manager_qa: Optional[DatasetConfig] = None
    manager_pres: Optional[DatasetConfig] = None
    analyst_qa: Optional[DatasetConfig] = None
    entire_call: Optional[DatasetConfig] = None

    def get_dataset(self, name: str) -> Optional[DatasetConfig]:
        """Get a dataset configuration by name.

        Args:
            name: Dataset name (e.g., 'manager_qa', 'analyst_qa').

        Returns:
            Dataset configuration if found, None otherwise.

        Example:
            >>> config = DatasetsConfig()
            >>> ds = config.get_dataset("manager_qa")
            >>> ds is None or ds.enabled
            True
        """
        return getattr(self, name, None)

    def get_enabled_datasets(self) -> List[str]:
        """Get list of enabled dataset names.

        Returns:
            List of dataset names that are enabled.

        Example:
            >>> config = DatasetsConfig(
            ...     manager_qa=DatasetConfig(enabled=True),
            ...     analyst_qa=DatasetConfig(enabled=False)
            ... )
            >>> config.get_enabled_datasets()
            ['manager_qa']
        """
        enabled: List[str] = []
        # Check known dataset names
        known_datasets = [
            "manager_qa",
            "manager_pres",
            "analyst_qa",
            "entire_call",
        ]
        for name in known_datasets:
            dataset = getattr(self, name, None)
            if dataset is not None and dataset.enabled:
                enabled.append(name)

        # Check for any additional datasets added via extra="allow"
        for attr_name in self.model_dump(exclude_unset=True):
            if attr_name not in known_datasets:
                dataset = getattr(self, attr_name, None)
                if isinstance(dataset, DatasetConfig) and dataset.enabled:
                    enabled.append(attr_name)

        return enabled
