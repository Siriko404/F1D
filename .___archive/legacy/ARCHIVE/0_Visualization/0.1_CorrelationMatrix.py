#!/usr/bin/env python3
"""
==============================================================================
0.1: Linguistic Variables Correlation Matrix
==============================================================================
ID: 0.1_CorrelationMatrix
Description: Generates a correlation matrix heatmap for linguistic variables.
             Uses black/monster-green theme to match presentation.

Inputs:
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet

Outputs:
    - 4_Outputs/0_Visualizations/correlation_matrix.png
==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
from datetime import datetime

# ==============================================================================
# Configuration
# ==============================================================================

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / '4_Outputs' / '0_Visualizations'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Theme colors
BG_COLOR = '#0a0a0a'
MONSTER_GREEN = '#39ff14'
DIM_GREEN = '#1a5c0a'
TEXT_COLOR = '#e0e0e0'

# ==============================================================================
# Data Loading
# ==============================================================================

def load_linguistic_variables():
    """Load all linguistic variables from 2.2 output."""
    var_dir = ROOT / '4_Outputs' / '2_Textual_Analysis' / '2.2_Variables' / 'latest'
    
    dfs = []
    for f in sorted(var_dir.glob('linguistic_variables_*.parquet')):
        df = pd.read_parquet(f)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(combined):,} rows from {len(dfs)} files")
    return combined


def get_linguistic_cols(df):
    """Extract only linguistic percentage columns (exclude metadata)."""
    meta_cols = ['file_name', 'start_date', 'gvkey', 'conm', 'sic', 'year']
    ling_cols = [c for c in df.columns if c not in meta_cols and '_pct' in c]
    return ling_cols


# ==============================================================================
# Visualization
# ==============================================================================

def create_correlation_heatmap(df, output_path):
    """Generate themed correlation matrix heatmap."""
    ling_cols = get_linguistic_cols(df)
    print(f"Computing correlation for {len(ling_cols)} variables...")
    
    # Compute correlation matrix
    corr = df[ling_cols].corr()
    
    # Create custom colormap: DIM_GREEN -> BLACK -> MONSTER_GREEN
    colors = [DIM_GREEN, BG_COLOR, MONSTER_GREEN]
    n_bins = 256
    cmap = mcolors.LinearSegmentedColormap.from_list('monster', colors, N=n_bins)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 14), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # Heatmap
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect='auto')
    
    # Simplify labels (just show category)
    short_labels = []
    for c in ling_cols:
        parts = c.replace('_pct', '').split('_')
        if len(parts) >= 3:
            # Format: Sample_Context_Category -> S_C_Cat
            sample = parts[0][0]  # First letter
            context = parts[1][0]  # First letter
            cat = parts[2][:4]  # First 4 letters
            short_labels.append(f"{sample}{context}_{cat}")
        else:
            short_labels.append(c[:8])
    
    # Set ticks
    tick_positions = np.arange(0, len(ling_cols), max(1, len(ling_cols)//15))
    ax.set_xticks(tick_positions)
    ax.set_yticks(tick_positions)
    ax.set_xticklabels([short_labels[i] for i in tick_positions], rotation=45, ha='right', 
                       fontsize=8, color=TEXT_COLOR, fontfamily='monospace')
    ax.set_yticklabels([short_labels[i] for i in tick_positions], 
                       fontsize=8, color=TEXT_COLOR, fontfamily='monospace')
    
    # Title
    ax.set_title('Linguistic Variables Correlation Matrix\n(105 variables: 5 Samples × 3 Contexts × 7 Categories)', 
                 fontsize=14, color=MONSTER_GREEN, fontweight='bold', fontfamily='monospace', pad=20)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
    cbar.ax.set_ylabel('Correlation', color=TEXT_COLOR, fontsize=10, fontfamily='monospace')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TEXT_COLOR, fontfamily='monospace')
    cbar.outline.set_edgecolor(DIM_GREEN)
    
    # Border
    for spine in ax.spines.values():
        spine.set_color(DIM_GREEN)
        spine.set_linewidth(1)
    
    # Add annotation
    ax.text(0.02, -0.08, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | N = {len(df):,} calls',
            transform=ax.transAxes, fontsize=8, color=DIM_GREEN, fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG_COLOR, edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")
    return corr


def print_summary_stats(corr, ling_cols):
    """Print correlation summary statistics."""
    # Get upper triangle (excluding diagonal)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    upper = corr.values[mask]
    
    print(f"\n{'='*60}")
    print("CORRELATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Variables: {len(ling_cols)}")
    print(f"  Correlation pairs: {len(upper):,}")
    print(f"  Mean: {np.mean(upper):.4f}")
    print(f"  Std: {np.std(upper):.4f}")
    print(f"  Min: {np.min(upper):.4f}")
    print(f"  Max: {np.max(upper):.4f}")
    print(f"  |r| > 0.7: {np.sum(np.abs(upper) > 0.7):,} pairs")
    print(f"  |r| > 0.5: {np.sum(np.abs(upper) > 0.5):,} pairs")


# ==============================================================================
# Main
# ==============================================================================

def main():
    print("=" * 60)
    print("0.1: Linguistic Variables Correlation Matrix")
    print("=" * 60)
    
    df = load_linguistic_variables()
    
    output_path = OUTPUT_DIR / 'correlation_matrix.png'
    corr = create_correlation_heatmap(df, output_path)
    
    ling_cols = get_linguistic_cols(df)
    print_summary_stats(corr, ling_cols)
    
    print("\n=== Complete ===")
    return 0


if __name__ == '__main__':
    exit(main())
