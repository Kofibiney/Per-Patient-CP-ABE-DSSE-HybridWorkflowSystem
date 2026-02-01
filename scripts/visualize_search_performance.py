#!/usr/bin/env python3
"""
SEARCH PERFORMANCE VISUALIZATION
=================================
Generates graphs from the search performance comparison CSV data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

def load_data():
    """Load the CSV data."""
    pp_data = pd.read_csv('per_patient_raw_data.csv')
    gl_data = pd.read_csv('global_index_raw_data.csv')
    return pp_data, gl_data

def plot_latency_comparison(pp_data, gl_data):
    """Box plot comparing latency distributions."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data_to_plot = [pp_data['latency_us'], gl_data['latency_us']]
    labels = ['Per-Patient Index', 'Global Index']
    
    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                    showmeans=True, meanline=True)
    
    # Color the boxes
    colors = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax.set_ylabel('Search Latency (μs)', fontsize=12, fontweight='bold')
    ax.set_title('Search Latency Comparison: Per-Patient vs Global Index', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add statistics text
    pp_mean = pp_data['latency_us'].mean()
    gl_mean = gl_data['latency_us'].mean()
    speedup = gl_mean / pp_mean
    
    stats_text = f'Per-Patient Mean: {pp_mean:.2f} μs\n'
    stats_text += f'Global Mean: {gl_mean:.2f} μs\n'
    stats_text += f'Speedup: {speedup:.2f}x'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('latency_comparison_boxplot.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: latency_comparison_boxplot.png")
    plt.close()

def plot_latency_histogram(pp_data, gl_data):
    """Histogram showing latency distributions."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Per-Patient histogram
    ax1.hist(pp_data['latency_us'], bins=50, color='#3498db', 
             alpha=0.7, edgecolor='black')
    ax1.axvline(pp_data['latency_us'].mean(), color='red', 
                linestyle='--', linewidth=2, label=f'Mean: {pp_data["latency_us"].mean():.2f} μs')
    ax1.axvline(pp_data['latency_us'].median(), color='green', 
                linestyle='--', linewidth=2, label=f'Median: {pp_data["latency_us"].median():.2f} μs')
    ax1.set_xlabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax1.set_title('Per-Patient Index - Latency Distribution', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Global histogram
    ax2.hist(gl_data['latency_us'], bins=50, color='#e74c3c', 
             alpha=0.7, edgecolor='black')
    ax2.axvline(gl_data['latency_us'].mean(), color='red', 
                linestyle='--', linewidth=2, label=f'Mean: {gl_data["latency_us"].mean():.2f} μs')
    ax2.axvline(gl_data['latency_us'].median(), color='green', 
                linestyle='--', linewidth=2, label=f'Median: {gl_data["latency_us"].median():.2f} μs')
    ax2.set_xlabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax2.set_title('Global Index - Latency Distribution', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('latency_histogram.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: latency_histogram.png")
    plt.close()

def plot_cdf_comparison(pp_data, gl_data):
    """Cumulative Distribution Function comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Sort data
    pp_sorted = np.sort(pp_data['latency_us'])
    gl_sorted = np.sort(gl_data['latency_us'])
    
    # Calculate CDF
    pp_cdf = np.arange(1, len(pp_sorted) + 1) / len(pp_sorted)
    gl_cdf = np.arange(1, len(gl_sorted) + 1) / len(gl_sorted)
    
    # Plot
    ax.plot(pp_sorted, pp_cdf * 100, label='Per-Patient Index', 
            linewidth=2, color='#3498db')
    ax.plot(gl_sorted, gl_cdf * 100, label='Global Index', 
            linewidth=2, color='#e74c3c')
    
    # Add percentile lines
    for percentile in [50, 95, 99]:
        pp_val = np.percentile(pp_data['latency_us'], percentile)
        gl_val = np.percentile(gl_data['latency_us'], percentile)
        ax.axhline(y=percentile, color='gray', linestyle=':', alpha=0.5)
        ax.text(ax.get_xlim()[1] * 0.7, percentile + 2, f'P{percentile}', 
                fontsize=9, alpha=0.7)
    
    ax.set_xlabel('Latency (μs)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cumulative Probability (%)', fontsize=12, fontweight='bold')
    ax.set_title('Cumulative Distribution Function (CDF) - Search Latency', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    
    plt.tight_layout()
    plt.savefig('latency_cdf.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: latency_cdf.png")
    plt.close()

def plot_statistics_bar(pp_data, gl_data):
    """Bar chart comparing key statistics."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    metrics = ['Mean', 'Median', 'P95', 'P99']
    pp_values = [
        pp_data['latency_us'].mean(),
        pp_data['latency_us'].median(),
        np.percentile(pp_data['latency_us'], 95),
        np.percentile(pp_data['latency_us'], 99)
    ]
    gl_values = [
        gl_data['latency_us'].mean(),
        gl_data['latency_us'].median(),
        np.percentile(gl_data['latency_us'], 95),
        np.percentile(gl_data['latency_us'], 99)
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pp_values, width, label='Per-Patient Index',
                   color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, gl_values, width, label='Global Index',
                   color='#e74c3c', alpha=0.8)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)
    
    ax.set_ylabel('Latency (μs)', fontsize=12, fontweight='bold')
    ax.set_title('Statistical Comparison of Search Latency', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('statistics_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: statistics_comparison.png")
    plt.close()

def plot_time_series(pp_data, gl_data):
    """Time series showing latency over iterations."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot every 10th point to avoid clutter
    step = 10
    ax.plot(pp_data['iteration'][::step], pp_data['latency_us'][::step], 
            'o-', label='Per-Patient Index', alpha=0.6, markersize=3, color='#3498db')
    ax.plot(gl_data['iteration'][::step], gl_data['latency_us'][::step], 
            'o-', label='Global Index', alpha=0.6, markersize=3, color='#e74c3c')
    
    # Add mean lines
    ax.axhline(y=pp_data['latency_us'].mean(), color='#3498db', 
               linestyle='--', linewidth=2, alpha=0.7, label='Per-Patient Mean')
    ax.axhline(y=gl_data['latency_us'].mean(), color='#e74c3c', 
               linestyle='--', linewidth=2, alpha=0.7, label='Global Mean')
    
    ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latency (μs)', fontsize=12, fontweight='bold')
    ax.set_title('Search Latency Over Time (Every 10th Iteration)', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('latency_timeseries.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: latency_timeseries.png")
    plt.close()

def plot_combined_summary(pp_data, gl_data):
    """Combined summary figure with multiple subplots."""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # 1. Box plot
    ax1 = fig.add_subplot(gs[0, 0])
    data_to_plot = [pp_data['latency_us'], gl_data['latency_us']]
    bp = ax1.boxplot(data_to_plot, labels=['Per-Patient', 'Global'], 
                     patch_artist=True, showmeans=True)
    for patch, color in zip(bp['boxes'], ['#3498db', '#e74c3c']):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax1.set_ylabel('Latency (μs)', fontweight='bold')
    ax1.set_title('Latency Distribution', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. CDF
    ax2 = fig.add_subplot(gs[0, 1])
    pp_sorted = np.sort(pp_data['latency_us'])
    gl_sorted = np.sort(gl_data['latency_us'])
    pp_cdf = np.arange(1, len(pp_sorted) + 1) / len(pp_sorted)
    gl_cdf = np.arange(1, len(gl_sorted) + 1) / len(gl_sorted)
    ax2.plot(pp_sorted, pp_cdf * 100, label='Per-Patient', linewidth=2, color='#3498db')
    ax2.plot(gl_sorted, gl_cdf * 100, label='Global', linewidth=2, color='#e74c3c')
    ax2.set_xlabel('Latency (μs)', fontweight='bold')
    ax2.set_ylabel('Cumulative %', fontweight='bold')
    ax2.set_title('Cumulative Distribution', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Statistics bar chart
    ax3 = fig.add_subplot(gs[1, 0])
    metrics = ['Mean', 'Median', 'P95', 'P99']
    pp_values = [pp_data['latency_us'].mean(), pp_data['latency_us'].median(),
                 np.percentile(pp_data['latency_us'], 95), 
                 np.percentile(pp_data['latency_us'], 99)]
    gl_values = [gl_data['latency_us'].mean(), gl_data['latency_us'].median(),
                 np.percentile(gl_data['latency_us'], 95), 
                 np.percentile(gl_data['latency_us'], 99)]
    x = np.arange(len(metrics))
    width = 0.35
    ax3.bar(x - width/2, pp_values, width, label='Per-Patient', color='#3498db', alpha=0.8)
    ax3.bar(x + width/2, gl_values, width, label='Global', color='#e74c3c', alpha=0.8)
    ax3.set_ylabel('Latency (μs)', fontweight='bold')
    ax3.set_title('Statistical Metrics', fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(metrics)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Speedup comparison
    ax4 = fig.add_subplot(gs[1, 1])
    speedups = [gl_values[i] / pp_values[i] for i in range(len(metrics))]
    bars = ax4.bar(metrics, speedups, color='#2ecc71', alpha=0.8)
    ax4.axhline(y=1, color='red', linestyle='--', linewidth=2, label='No speedup')
    for bar, speedup in zip(bars, speedups):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{speedup:.2f}x', ha='center', va='bottom', fontweight='bold')
    ax4.set_ylabel('Speedup Factor', fontweight='bold')
    ax4.set_title('Per-Patient Speedup vs Global', fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    fig.suptitle('Search Performance Analysis: Per-Patient vs Global Index', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    plt.savefig('combined_summary.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: combined_summary.png")
    plt.close()

def main():
    print("=" * 60)
    print("  SEARCH PERFORMANCE VISUALIZATION")
    print("=" * 60)
    
    print("\nLoading CSV data...")
    pp_data, gl_data = load_data()
    print(f"✓ Loaded {len(pp_data)} per-patient measurements")
    print(f"✓ Loaded {len(gl_data)} global index measurements")
    
    print("\nGenerating visualizations...")
    plot_latency_comparison(pp_data, gl_data)
    plot_latency_histogram(pp_data, gl_data)
    plot_cdf_comparison(pp_data, gl_data)
    plot_statistics_bar(pp_data, gl_data)
    plot_time_series(pp_data, gl_data)
    plot_combined_summary(pp_data, gl_data)
    
    print("\n" + "=" * 60)
    print("  ✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. latency_comparison_boxplot.png - Box plot comparison")
    print("  2. latency_histogram.png - Distribution histograms")
    print("  3. latency_cdf.png - Cumulative distribution")
    print("  4. statistics_comparison.png - Statistical metrics")
    print("  5. latency_timeseries.png - Time series plot")
    print("  6. combined_summary.png - All-in-one summary")

if __name__ == "__main__":
    main()
