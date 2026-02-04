from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np

PRECISE_W_LORA = 'lora=1-base-groups=80-pods=8'
PRECISE_WO_LORA = 'lora=0-groups=160-pods=8'
RANDOM_W_LORA = f'{PRECISE_W_LORA}-random'
RANDOM_WO_LORA = f'{PRECISE_WO_LORA}-random'

ALL_EXPERIMENTS = [
    PRECISE_W_LORA,
    PRECISE_WO_LORA,
    RANDOM_W_LORA,
    RANDOM_WO_LORA,
]

RESULTS_DIR = '/Users/sagi/repos/llmd/forks/llm-d/results'
PLOTS_DIR = '/Users/sagi/repos/llmd/forks/llm-d/plots'

def load_throughput_metrics(experiment_name, metrics_filename='summary_lifecycle_metrics.json'):
    """Load all throughput metrics for a given experiment."""
    summary_path = Path(RESULTS_DIR) / experiment_name / metrics_filename
    data = json.loads(summary_path.read_text())
    return data['successes']['throughput']


def plot_lora_impact(precise_w_lora, random_w_lora, precise_wo_lora, random_wo_lora, plot_fname_prefix):
    """Plot the LoRA impact comparison showing RANDOM is more affected than PRECISE."""
    
    metrics = [
        ('total_tokens_per_sec', 'Total Tokens/sec', 'Total Throughput'),
        ('input_tokens_per_sec', 'Input Tokens/sec', 'Input Throughput'),
        ('output_tokens_per_sec', 'Output Tokens/sec', 'Output Throughput'),
        ('requests_per_sec', 'Requests/sec', 'Request Rate')
    ]
    
    print(f"\n{'='*80}")
    print("LoRA IMPACT ANALYSIS - Throughput Metrics")
    print(f"{'='*80}\n")
    
    # Create 2x2 subplot grid
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('LoRA Impact on Throughput Metrics\nRANDOM Scheduler Shows GREATER Degradation', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    axes = axes.flatten()
    
    for idx, (metric_key, ylabel, title) in enumerate(metrics):
        ax = axes[idx]
        
        # Get values for this metric
        precise_wo = precise_wo_lora[metric_key]
        precise_w = precise_w_lora[metric_key]
        random_wo = random_wo_lora[metric_key]
        random_w = random_w_lora[metric_key]
        
        # Calculate impacts (gap between RANDOM and PRECISE)
        wo_lora_gap = random_wo - precise_wo
        w_lora_gap = random_w - precise_w
        
        # Calculate percentages
        wo_lora_pct = (wo_lora_gap / precise_wo) * 100
        w_lora_pct = (w_lora_gap / precise_w) * 100
        
        # Impact difference (how much MORE the gap increased with LoRA)
        gap_increase = w_lora_gap - wo_lora_gap
        
        # Print analysis
        print(f"{title}:")
        print(f"  W/O LoRA - PRECISE: {precise_wo:.2f} | RANDOM: {random_wo:.2f} | Gap: {wo_lora_gap:+.2f} ({wo_lora_pct:+.2f}%)")
        print(f"  WITH LoRA - PRECISE: {precise_w:.2f} | RANDOM: {random_w:.2f} | Gap: {w_lora_gap:+.2f} ({w_lora_pct:+.2f}%)")
        print(f"  → Gap increased by {gap_increase:+.2f} {ylabel} with LoRA\n")
        
        # Create bar chart
        scenarios = ['WITH LoRA', 'W/O LoRA']
        x = np.arange(len(scenarios))
        width = 0.35
        
        precise_vals = [precise_w, precise_wo]
        random_vals = [random_w, random_wo]
        
        bars1 = ax.bar(x - width/2, precise_vals, width, 
                      label='PRECISE', color='#2ecc71', alpha=0.85, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, random_vals, width, 
                      label='ROUND ROBIN', color='#e74c3c', alpha=0.85, edgecolor='black', linewidth=1.5)
        
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios, fontsize=10)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Add impact annotations (gap between PRECISE and RANDOM)
        gaps = [w_lora_gap, wo_lora_gap]
        percentages = [w_lora_pct, wo_lora_pct]
        
        for i in range(len(scenarios)):
            gap = gaps[i]
            pct = percentages[i]
            precise_val = precise_vals[i]
            random_val = random_vals[i]
            
            # Draw arrow showing gap
            arrow_color = 'red' if gap < 0 else 'green'
            ax.annotate('', xy=(x[i], random_val), xytext=(x[i], precise_val),
                       arrowprops=dict(arrowstyle='<->', color=arrow_color, lw=2))
            
            # Add label
            mid_point = (precise_val + random_val) / 2
            ax.text(x[i] + 0.15, mid_point, f'{gap:+.1f}\n({pct:+.1f}%)',
                   fontsize=8, fontweight='bold', color='darkred' if gap < 0 else 'darkgreen',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    print(f"{'='*80}")
    print("RANDOM scheduling is MORE impacted by LoRA adapters across all metrics")
    print(f"{'='*80}\n")
    
    plt.tight_layout()
    
    # Save the plot
    output_path = Path(PLOTS_DIR) / f'{plot_fname_prefix}_lora_impact_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_path}\n")
    
    # plt.show()


if __name__ == "__main__":
    print("Loading experiment data...")
    
    summary_fnames = ['summary_lifecycle_metrics.json']
    summary_fnames += [f'stage_{i}_lifecycle_metrics.json' for i in range(17)]

    # Load metrics for all experiments
    for fname in summary_fnames:
        precise_w_lora = load_throughput_metrics(PRECISE_W_LORA, metrics_filename=fname)
        random_w_lora = load_throughput_metrics(RANDOM_W_LORA, metrics_filename=fname)
        precise_wo_lora = load_throughput_metrics(PRECISE_WO_LORA, metrics_filename=fname)
        random_wo_lora = load_throughput_metrics(RANDOM_WO_LORA, metrics_filename=fname)
    
        # Analyze and plot LoRA impact
        plot_fname_prefix = fname.removesuffix('_lifecycle_metrics.json')
        plot_lora_impact(precise_w_lora, random_w_lora, precise_wo_lora, random_wo_lora, plot_fname_prefix=plot_fname_prefix)
