import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set high-resolution plotting defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Set seaborn style
sns.set_style("white")
sns.set_palette("husl")

CSV_NAMES = [
    "cpu_cores.csv",
    "fs_gib.csv",
    "memory_gib.csv",
    "net_in_mib.csv",
    "net_out_mib.csv"
]

if __name__ == "__main__":
    output_dir = "benchmarking_data"
    plots_dir = Path(output_dir) / "plots"
    plots_dir.mkdir()

    for csv_name in CSV_NAMES:
        df = pd.read_csv(Path(output_dir) / csv_name)

        # Filter to relevant pods only
        df = df[df["pod"].str.startswith("ms")]

        print(f"Plotting {csv_name}...")

        assert df.columns[:2].tolist() == ["pod", "timestamp"]
        assert len(df.columns) == 3

        value_name = df.columns[2]

        # Create high-resolution figure
        plt.figure(figsize=(14, 8))
        
        # cols are pod,timestamp,<value-name>
        # plot lines where x is timestamp, y is value-name, group by pod
        for i, (pod, pod_df) in enumerate(df.groupby("pod")):
            sns.lineplot(data=pod_df, x="timestamp", y=value_name, 
                        label=pod, linewidth=2, alpha=0.8)
        
        plt.xlabel("Timestamp", fontsize=14, fontweight='bold')
        plt.ylabel(value_name.replace('_', ' ').title(), fontsize=14, fontweight='bold')
        plt.title(f"{value_name.replace('_', ' ').title()} Over Time", 
                 fontsize=16, fontweight='bold', pad=20)
        
        # Improve legend
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                  frameon=True, fancybox=True, shadow=True)
        
        # Hide x-axis tick labels
        plt.xticks([])
        
        # Tight layout to prevent clipping
        plt.tight_layout()
        
        # Save with high quality
        plt.savefig(Path(plots_dir) / f"{csv_name[:-4]}.png", 
                   dpi=300, bbox_inches='tight', facecolor='white', 
                   edgecolor='none')
        plt.clf()
