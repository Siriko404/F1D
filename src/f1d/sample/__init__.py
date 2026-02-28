"""Sample construction module for F1D pipeline.

Tier 2: Stage-specific module - Stage 1 of the pipeline.

This module handles building the analyst-CEO manifest and applying
sample filters based on industry, size, and other criteria.

Modules:
    - build_sample_manifest: Orchestrator for 4-substep sample construction process
    - clean_metadata: Cleans Unified-info, deduplicates, and filters for earnings calls
    - link_entities: Entity resolution via 4-tier CCM linking strategy
    - build_tenure_map: Constructs monthly CEO tenure panel from Execucomp
    - assemble_manifest: Joins metadata with CEO panel, applies minimum call threshold
    - utils: Shared utilities for variable reference generation
"""

__all__: list[str] = []
