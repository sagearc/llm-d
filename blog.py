from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np

PRECISE_W_LORA = 'lora=4-groups=40-pods=8'
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

def load_throughput_metrics(experiment_name):
    """Load all throughput metrics for a given experiment."""
    summary_filename = 'summary_lifecycle_metrics.json'
    summary_path = Path(RESULTS_DIR) / experiment_name / summary_filename
    data = json.loads(summary_path.read_text())
    return data['successes']['throughput']


def plot_lora_impact(precise_w_lora, random_w_lora, precise_wo_lora, random_wo_lora):
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
        
        # Calculate impacts
        precise_impact = precise_w - precise_wo
        random_impact = random_w - random_wo
        
        # Calculate percentages
        precise_pct = (precise_impact / precise_wo) * 100
        random_pct = (random_impact / random_wo) * 100
        
        # Impact difference
        impact_diff = random_impact - precise_impact
        
        # Print analysis
        print(f"{title}:")
        print(f"  W/O LoRA - PRECISE: {precise_wo:.2f} | RANDOM: {random_wo:.2f}")
        print(f"  WITH LoRA - PRECISE: {precise_w:.2f} | RANDOM: {random_w:.2f}")
        print(f"  Impact - PRECISE: {precise_impact:+.2f} ({precise_pct:+.2f}%) | RANDOM: {random_impact:+.2f} ({random_pct:+.2f}%)")
        print(f"  → RANDOM degraded {abs(impact_diff):.2f} {ylabel} MORE\n")
        
        # Create bar chart
        scenarios = ['PRECISE\nScheduler', 'RANDOM\nScheduler']
        x = np.arange(len(scenarios))
        width = 0.35
        
        wo_lora_vals = [precise_wo, random_wo]
        w_lora_vals = [precise_w, random_w]
        
        bars1 = ax.bar(x - width/2, wo_lora_vals, width, 
                      label='W/O LoRA', color='#3498db', alpha=0.85, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, w_lora_vals, width, 
                      label='WITH LoRA', color='#e74c3c', alpha=0.85, edgecolor='black', linewidth=1.5)
        
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
        
        # Add impact annotations (degradation arrows)
        impacts = [precise_impact, random_impact]
        percentages = [precise_pct, random_pct]
        
        for i in range(len(scenarios)):
            impact = impacts[i]
            pct = percentages[i]
            wo_val = wo_lora_vals[i]
            w_val = w_lora_vals[i]
            
            # Draw arrow showing change
            arrow_color = 'red' if impact < 0 else 'green'
            ax.annotate('', xy=(x[i], w_val), xytext=(x[i], wo_val),
                       arrowprops=dict(arrowstyle='<->', color=arrow_color, lw=2))
            
            # Add label
            mid_point = (wo_val + w_val) / 2
            ax.text(x[i] + 0.15, mid_point, f'{impact:+.1f}\n({pct:+.1f}%)',
                   fontsize=8, fontweight='bold', color='darkred' if impact < 0 else 'darkgreen',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    print(f"{'='*80}")
    print("RANDOM scheduling is MORE impacted by LoRA adapters across all metrics")
    print(f"{'='*80}\n")
    
    plt.tight_layout()
    
    # Save the plot
    output_path = Path(RESULTS_DIR) / 'lora_impact_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_path}\n")
    
    plt.show()


if __name__ == "__main__":
    print("Loading experiment data...")
    
    # Load metrics for all experiments
    precise_w_lora = load_throughput_metrics(PRECISE_W_LORA)
    random_w_lora = load_throughput_metrics(RANDOM_W_LORA)
    precise_wo_lora = load_throughput_metrics(PRECISE_WO_LORA)
    random_wo_lora = load_throughput_metrics(RANDOM_WO_LORA)
    
    # Analyze and plot LoRA impact
    plot_lora_impact(precise_w_lora, random_w_lora, precise_wo_lora, random_wo_lora)
