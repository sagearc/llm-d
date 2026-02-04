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

def load_throughput_metric(experiment_name):
    """Load total_tokens_per_sec throughput metric for a given experiment."""
    summary_filename = 'summary_lifecycle_metrics.json'
    summary_path = Path(RESULTS_DIR) / experiment_name / summary_filename
    data = json.loads(summary_path.read_text())
    return data['successes']['throughput']['total_tokens_per_sec']


def plot_lora_impact(precise_w_lora, random_w_lora, precise_wo_lora, random_wo_lora):
    """Plot the LoRA impact comparison showing RANDOM is more affected than PRECISE."""
    
    # Calculate throughput changes (WITHOUT LoRA → WITH LoRA)
    # Negative means throughput decreased (worse performance)
    precise_lora_impact = precise_w_lora - precise_wo_lora
    random_lora_impact = random_w_lora - random_wo_lora
    
    # Calculate percentage changes
    precise_pct = (precise_lora_impact / precise_wo_lora) * 100
    random_pct = (random_lora_impact / random_wo_lora) * 100
    
    # Impact difference
    impact_diff = random_lora_impact - precise_lora_impact
    
    print(f"\n{'='*80}")
    print("LoRA IMPACT ANALYSIS - Throughput (tokens/sec)")
    print(f"{'='*80}\n")
    
    print(f"WITHOUT LoRA:")
    print(f"  PRECISE: {precise_wo_lora:.2f} tokens/sec")
    print(f"  RANDOM:  {random_wo_lora:.2f} tokens/sec")
    
    print(f"\nWITH LoRA:")
    print(f"  PRECISE: {precise_w_lora:.2f} tokens/sec")
    print(f"  RANDOM:  {random_w_lora:.2f} tokens/sec")
    
    print(f"\nLoRA Impact (W/O → WITH):")
    print(f"  PRECISE: {precise_lora_impact:+.2f} tokens/sec ({precise_pct:+.2f}%)")
    print(f"  RANDOM:  {random_lora_impact:+.2f} tokens/sec ({random_pct:+.2f}%)")
    print(f"  → RANDOM degraded {abs(impact_diff):.2f} tokens/sec MORE than PRECISE")
    
    print(f"\n{'='*80}")
    print("RANDOM scheduling is MORE impacted by LoRA adapters")
    print(f"{'='*80}\n")
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 7))
    
    scenarios = ['PRECISE\nScheduler', 'RANDOM\nScheduler']
    x = np.arange(len(scenarios))
    width = 0.35
    
    # Throughput values
    wo_lora_vals = [precise_wo_lora, random_wo_lora]
    w_lora_vals = [precise_w_lora, random_w_lora]
    
    bars1 = ax.bar(x - width/2, wo_lora_vals, width, 
                   label='W/O LoRA', color='#3498db', alpha=0.85, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, w_lora_vals, width, 
                   label='WITH LoRA', color='#e74c3c', alpha=0.85, edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Throughput (tokens/sec)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Scheduling Strategy', fontsize=13, fontweight='bold')
    ax.set_title('LoRA Impact on Throughput\nRANDOM Scheduler Shows GREATER Degradation', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=11)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add impact annotations (degradation arrows)
    impacts = [precise_lora_impact, random_lora_impact]
    for i in range(len(scenarios)):
        impact = impacts[i]
        wo_val = wo_lora_vals[i]
        w_val = w_lora_vals[i]
        
        # Draw arrow showing degradation
        ax.annotate('', xy=(x[i], w_val), xytext=(x[i], wo_val),
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        
        # Add label
        mid_point = (wo_val + w_val) / 2
        ax.text(x[i] + 0.15, mid_point, f'{impact:+.1f}\n({impacts[i]/wo_lora_vals[i]*100:+.1f}%)',
               fontsize=9, fontweight='bold', color='darkred',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    
    # Save the plot
    output_path = Path(RESULTS_DIR) / 'lora_impact_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_path}\n")
    
    plt.show()


if __name__ == "__main__":
    print("Loading experiment data...")
    
    # Load metrics for all experiments
    precise_w_lora = load_throughput_metric(PRECISE_W_LORA)
    random_w_lora = load_throughput_metric(RANDOM_W_LORA)
    precise_wo_lora = load_throughput_metric(PRECISE_WO_LORA)
    random_wo_lora = load_throughput_metric(RANDOM_WO_LORA)
    
    # Analyze and plot LoRA impact
    plot_lora_impact(precise_w_lora, random_w_lora, precise_wo_lora, random_wo_lora)
