#!/usr/bin/env python3
"""
Generate visualization figures for the pipeline comparison slides:
1. Timeseries Heatmaps: Industry uncertainty % by year (FF12) - pink=uncertain, green=clear
2. Timeseries Line Chart: Uncertainty trends by industry
3. Distribution Plots: Uncertainty measures + CEO Clarity
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from pathlib import Path
from scipy import stats

# Setup paths
ROOT = Path(__file__).parent.parent
ENRICHED_DIR = ROOT / '4_Outputs' / '2.5_LinkCcmAndIndustries' / 'latest'
CLARITY_DIR = ROOT / '4_Outputs' / '2.8_EstimateCeoClarity' / '2025-12-08_130720'
OUTPUT_DIR = ROOT / '4_Outputs' / '2.11_Replication_Reports' / 'paper_comparison' / 'figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Dark theme styling
plt.style.use('dark_background')
COLORS = {
    'green': '#00ff88',
    'pink': '#ff6b9d', 
    'dim': '#888888',
    'bg': '#0a0a0a',
    'card': '#111111'
}

# Custom colormap: green (low uncertainty) to pink (high uncertainty)
def create_green_pink_cmap():
    """Create colormap from green (clear) to pink (uncertain)."""
    colors = ['#00ff88', '#88ff88', '#ffff88', '#ff8888', '#ff6b9d']
    return mcolors.LinearSegmentedColormap.from_list('green_pink', colors)


def load_enriched_data():
    """Load all enriched parquet files with FF12 classification."""
    dfs = []
    for year in range(2002, 2019):
        path = ENRICHED_DIR / f'f1d_enriched_{year}.parquet'
        if path.exists():
            df = pd.read_parquet(path)
            df['year'] = year
            dfs.append(df)
            print(f"Loaded enriched {year}: {len(df):,} rows")
    
    full_df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal enriched: {len(full_df):,} rows")
    return full_df


def load_clarity_data():
    """Load CEO clarity scores."""
    path = CLARITY_DIR / 'ceo_clarity_scores.parquet'
    df = pd.read_parquet(path)
    print(f"Loaded {len(df):,} CEO clarity scores")
    return df


def load_calls_with_clarity():
    """Load all calls_with_clarity parquet files (contains ClarityCEO + ff12_name + year)."""
    dfs = []
    for year in range(2002, 2019):
        path = CLARITY_DIR / f'calls_with_clarity_{year}.parquet'
        if path.exists():
            df = pd.read_parquet(path)
            dfs.append(df)
            print(f"Loaded calls_with_clarity {year}: {len(df):,} rows")
    
    full_df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal calls with clarity: {len(full_df):,} rows")
    return full_df


def create_timeseries_heatmap(df, measure_col, title, output_name):
    """Create a timeseries heatmap: years (x) vs industries (y), pink=uncertain, green=clear."""
    
    # Filter valid FF12
    df_valid = df[df['ff12_name'].notna() & (df['ff12_name'] != 'Other')].copy()
    
    # Compute mean uncertainty by year and industry
    pivot = df_valid.groupby(['year', 'ff12_name'])[measure_col].mean().reset_index()
    heatmap_data = pivot.pivot(index='ff12_name', columns='year', values=measure_col)
    
    # Sort industries by overall mean (most uncertain at top)
    industry_order = heatmap_data.mean(axis=1).sort_values(ascending=False).index
    heatmap_data = heatmap_data.loc[industry_order]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['card'])
    
    # Create heatmap with green-to-pink colormap
    cmap = create_green_pink_cmap()
    sns.heatmap(heatmap_data, ax=ax, cmap=cmap, annot=True, fmt='.2f', 
                annot_kws={'size': 8, 'color': 'white'},
                cbar_kws={'label': 'Uncertainty %'},
                linewidths=0.5, linecolor='#333')
    
    ax.set_xlabel('Year', color='white', fontsize=12)
    ax.set_ylabel('Industry (FF12)', color='white', fontsize=12)
    ax.set_title(title, color=COLORS['green'], fontsize=16, fontweight='bold')
    ax.tick_params(colors='white')
    
    # Style colorbar
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color('white')
    cbar.ax.tick_params(colors='white')
    
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / output_name
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'], edgecolor='none')
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def create_all_heatmaps(df):
    """Create heatmaps for all three uncertainty measures."""
    
    measures = [
        ('MaPresUnc_pct', 'Manager Presentation Uncertainty by Industry & Year', 'heatmap_mapres.png'),
        ('MaQaUnc_pct', 'Manager Q&A Uncertainty by Industry & Year', 'heatmap_maqa.png'),
        ('AnaQaUnc_pct', 'Analyst Q&A Uncertainty by Industry & Year', 'heatmap_anaqa.png')
    ]
    
    paths = []
    for col, title, filename in measures:
        path = create_timeseries_heatmap(df, col, title, filename)
        paths.append(path)
    
    return paths


def create_clarity_heatmap(calls_clarity_df):
    """Create CEO Clarity timeseries heatmap by industry and year.
    Note: For Clarity, high values = clearer CEOs (green), low = less clear (pink).
    So we reverse the colormap.
    """
    
    # Filter valid FF12
    df_valid = calls_clarity_df[calls_clarity_df['ff12_name'].notna() & (calls_clarity_df['ff12_name'] != 'Other')].copy()
    
    # Compute mean clarity by year and industry
    pivot = df_valid.groupby(['year', 'ff12_name'])['ClarityCEO'].mean().reset_index()
    heatmap_data = pivot.pivot(index='ff12_name', columns='year', values='ClarityCEO')
    
    # Sort industries by overall mean (highest clarity at top)
    industry_order = heatmap_data.mean(axis=1).sort_values(ascending=False).index
    heatmap_data = heatmap_data.loc[industry_order]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['card'])
    
    # For Clarity: REVERSE colormap - green = high clarity, pink = low clarity
    # Create reversed colormap (pink to green)
    colors_reversed = ['#ff6b9d', '#ff8888', '#ffff88', '#88ff88', '#00ff88']
    cmap = mcolors.LinearSegmentedColormap.from_list('pink_green', colors_reversed)
    
    sns.heatmap(heatmap_data, ax=ax, cmap=cmap, annot=True, fmt='.3f', 
                annot_kws={'size': 7, 'color': 'white'},
                cbar_kws={'label': 'CEO Clarity Score'},
                linewidths=0.5, linecolor='#333')
    
    ax.set_xlabel('Year', color='white', fontsize=12)
    ax.set_ylabel('Industry (FF12)', color='white', fontsize=12)
    ax.set_title('CEO Clarity by Industry & Year (Green = Clearer, Pink = Less Clear)', 
                 color=COLORS['green'], fontsize=16, fontweight='bold')
    ax.tick_params(colors='white')
    
    # Style colorbar
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color('white')
    cbar.ax.tick_params(colors='white')
    
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / 'heatmap_ceo_clarity.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'], edgecolor='none')
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def create_timeseries_chart(df):
    """Create timeseries line chart of uncertainty by industry over time."""
    
    # Filter to valid FF12
    df_valid = df[df['ff12_name'].notna() & (df['ff12_name'] != 'Other')].copy()
    
    # Use MaPresUnc_pct as the primary uncertainty measure
    yearly_industry = df_valid.groupby(['year', 'ff12_name'])['MaPresUnc_pct'].mean().reset_index()
    pivot = yearly_industry.pivot(index='year', columns='ff12_name', values='MaPresUnc_pct')
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['card'])
    
    # Create color palette
    n_industries = len(pivot.columns)
    colors = plt.cm.tab20(np.linspace(0, 1, n_industries))
    
    for i, industry in enumerate(pivot.columns):
        ax.plot(pivot.index, pivot[industry], label=industry, linewidth=2, 
                color=colors[i], marker='o', markersize=4, alpha=0.8)
    
    ax.set_xlabel('Year', color='white', fontsize=12)
    ax.set_ylabel('Uncertainty % (Manager Presentation)', color='white', fontsize=12)
    ax.set_title('Uncertainty Trends by Industry (2002-2018)', 
                 color=COLORS['green'], fontsize=16, fontweight='bold')
    
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['dim'])
    ax.spines['left'].set_color(COLORS['dim'])
    ax.grid(True, alpha=0.2, color=COLORS['dim'])
    
    # Legend outside plot
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9, 
              frameon=True, facecolor=COLORS['card'], edgecolor=COLORS['dim'])
    
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / 'industry_uncertainty_timeseries.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'], edgecolor='none')
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def create_distribution_plots(df):
    """Create distribution plots for uncertainty measures."""
    
    measures = [
        ('MaPresUnc_pct', 'Manager Presentation', COLORS['pink']),
        ('MaQaUnc_pct', 'Manager Q&A', COLORS['green']),
        ('AnaQaUnc_pct', 'Analyst Q&A', '#00bfff')
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor(COLORS['bg'])
    
    for idx, (col, title, color) in enumerate(measures):
        ax = axes[idx]
        ax.set_facecolor(COLORS['card'])
        
        data = df[col].dropna()
        
        # Histogram with KDE
        ax.hist(data, bins=50, density=True, alpha=0.7, color=color, edgecolor='none')
        
        # Add KDE line
        kde = stats.gaussian_kde(data)
        x_range = np.linspace(data.min(), data.max(), 200)
        ax.plot(x_range, kde(x_range), color='white', linewidth=2)
        
        # Stats
        mean_val = data.mean()
        median_val = data.median()
        ax.axvline(mean_val, color='yellow', linestyle='--', linewidth=1.5, label=f'Mean: {mean_val:.2f}%')
        ax.axvline(median_val, color='cyan', linestyle=':', linewidth=1.5, label=f'Median: {median_val:.2f}%')
        
        ax.set_xlabel('Uncertainty %', color='white', fontsize=10)
        ax.set_ylabel('Density', color='white', fontsize=10)
        ax.set_title(title, color=color, fontsize=14, fontweight='bold')
        ax.tick_params(colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(COLORS['dim'])
        ax.spines['left'].set_color(COLORS['dim'])
        ax.legend(fontsize=8, facecolor=COLORS['card'], edgecolor=COLORS['dim'])
    
    plt.suptitle('Distribution of Uncertainty Measures', 
                 color='white', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / 'uncertainty_distributions.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'], edgecolor='none')
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def create_clarity_distribution(clarity_df):
    """Create distribution plot for CEO Clarity scores."""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['card'])
    
    data = clarity_df['ClarityCEO'].dropna()
    
    # Histogram with KDE
    ax.hist(data, bins=50, density=True, alpha=0.7, color=COLORS['green'], edgecolor='none')
    
    # Add KDE line
    kde = stats.gaussian_kde(data)
    x_range = np.linspace(data.min(), data.max(), 200)
    ax.plot(x_range, kde(x_range), color='white', linewidth=2)
    
    # Stats
    mean_val = data.mean()
    median_val = data.median()
    ax.axvline(mean_val, color='yellow', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.3f}')
    ax.axvline(median_val, color='cyan', linestyle=':', linewidth=2, label=f'Median: {median_val:.3f}')
    ax.axvline(0, color=COLORS['pink'], linestyle='-', linewidth=1, alpha=0.5, label='Zero (Avg CEO)')
    
    ax.set_xlabel('CEO Clarity Score (higher = clearer communication)', color='white', fontsize=12)
    ax.set_ylabel('Density', color='white', fontsize=12)
    ax.set_title('Distribution of CEO Clarity Scores', color=COLORS['green'], fontsize=16, fontweight='bold')
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['dim'])
    ax.spines['left'].set_color(COLORS['dim'])
    ax.legend(fontsize=10, facecolor=COLORS['card'], edgecolor=COLORS['dim'])
    ax.grid(True, alpha=0.2, color=COLORS['dim'])
    
    # Add annotation
    n_ceos = len(data)
    ax.text(0.02, 0.98, f'N = {n_ceos:,} CEOs', transform=ax.transAxes, 
            fontsize=11, color='white', verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor=COLORS['card'], edgecolor=COLORS['dim']))
    
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / 'ceo_clarity_distribution.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'], edgecolor='none')
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def main():
    print("=" * 60)
    print("Generating Pipeline Visualization Figures")
    print("=" * 60)
    
    # Load data
    print("\n[1/7] Loading enriched data...")
    df = load_enriched_data()
    
    print("\n[2/7] Loading CEO clarity scores...")
    clarity_df = load_clarity_data()
    
    print("\n[3/7] Loading calls with clarity (for industry heatmap)...")
    calls_clarity_df = load_calls_with_clarity()
    
    # Generate figures
    print("\n[4/7] Creating uncertainty timeseries heatmaps (green=clear, pink=uncertain)...")
    heatmap_paths = create_all_heatmaps(df)
    
    print("\n[5/7] Creating CEO Clarity timeseries heatmap by industry...")
    clarity_heatmap_path = create_clarity_heatmap(calls_clarity_df)
    
    print("\n[6/7] Creating uncertainty & clarity distribution plots...")
    distribution_path = create_distribution_plots(df)
    clarity_dist_path = create_clarity_distribution(clarity_df)
    
    print("\n[7/7] Creating timeseries line chart...")
    timeseries_path = create_timeseries_chart(df)
    
    print("\n" + "=" * 60)
    print("DONE! Generated figures:")
    for p in heatmap_paths:
        print(f"  - {p}")
    print(f"  - {clarity_heatmap_path}")
    print(f"  - {timeseries_path}")
    print(f"  - {distribution_path}")
    print(f"  - {clarity_dist_path}")
    print("=" * 60)


if __name__ == '__main__':
    main()
