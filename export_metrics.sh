#!/usr/bin/env bash

# Configuration
NS="sageac"
TARGET_DIR="./benchmarking_data"
TOKEN=$(oc whoami -t)
PROM_URL="https://localhost:9092"

# Create target directory
mkdir -p "$TARGET_DIR"

# Get currently active pods
echo "Getting currently active pods in namespace $NS..."
ACTIVE_PODS=($(oc get pods -n $NS -o custom-columns='NAME:.metadata.name' --no-headers))
echo "Found ${#ACTIVE_PODS[@]} active pods"

# Save active pods list for plotting script
printf "NAME\n" > "$TARGET_DIR/pods.txt"
for pod in "${ACTIVE_PODS[@]}"; do
    printf "%s\n" "$pod" >> "$TARGET_DIR/pods.txt"
done

# List of metrics to fetch (Format: "filename|query_template")
METRIC_LIST=(
  "memory_gib|sum(container_memory_working_set_bytes{namespace='$NS',pod='POD_NAME'}) by (pod) / 1024 / 1024 / 1024"
  "cpu_cores|sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{namespace='$NS',pod='POD_NAME'}) by (pod)"
  "fs_gib|sum(container_fs_usage_bytes{namespace='$NS',pod='POD_NAME'}) by (pod) / 1024 / 1024 / 1024"
  "net_in_mib|sum(irate(container_network_receive_bytes_total{namespace='$NS',pod='POD_NAME'}[5m])) by (pod) / 1024 / 1024"
  "net_out_mib|sum(irate(container_network_transmit_bytes_total{namespace='$NS',pod='POD_NAME'}[5m])) by (pod) / 1024 / 1024"
)

# Initialize CSV files with headers
for item in "${METRIC_LIST[@]}"; do
    NAME="${item%%|*}"
    echo "pod,timestamp,$NAME" > "$TARGET_DIR/${NAME}.csv"
done

# Process each active pod individually
for pod in "${ACTIVE_PODS[@]}"; do
    echo "Processing pod: $pod"
    
    # Get this pod's creation time
    POD_START=$(kubectl get pod "$pod" -n $NS -o json | jq '.metadata.creationTimestamp | fromdateiso8601')
    END=$(date +%s)
    
    if [ -z "$POD_START" ] || [ "$POD_START" = "null" ]; then
        echo "Warning: Could not get creation time for pod $pod, skipping..."
        continue
    fi
    
    echo "  Pod created at: $(date -r $POD_START)"
    
    # Fetch metrics for this specific pod
    for item in "${METRIC_LIST[@]}"; do
        NAME="${item%%|*}"
        QUERY_TEMPLATE="${item#*|}"
        QUERY="${QUERY_TEMPLATE//POD_NAME/$pod}"
        
        echo "  Fetching $NAME for $pod..."
        curl -k -H "Authorization: Bearer $TOKEN" -G "$PROM_URL/api/v1/query_range" \
            --data-urlencode "query=$QUERY" \
            --data-urlencode "start=$POD_START" \
            --data-urlencode "end=$END" \
            --data-urlencode "step=1m" \
            -o "$TARGET_DIR/${NAME}_${pod}_raw.json"
        
        # Append to the respective CSV file
        cat "$TARGET_DIR/${NAME}_${pod}_raw.json" | jq -r '.data.result[] | .metric.pod as $p | .values[] | [$p, (.[0] | strftime("%Y-%m-%dT%H:%M:%SZ")), .[1]] | @csv' >> "$TARGET_DIR/${NAME}.csv"
        
        # Clean up individual raw file
        rm "$TARGET_DIR/${NAME}_${pod}_raw.json"
    done
done

# 2. Merge them using Python
echo "Merging all metrics into $TARGET_DIR/master_metrics.csv..."
python3 - <<EOF
import csv
import os
from collections import defaultdict

target_dir = "$TARGET_DIR"
data = defaultdict(dict)
metrics = ['memory_gib', 'cpu_cores', 'fs_gib', 'net_in_mib', 'net_out_mib']

for m in metrics:
    file_path = os.path.join(target_dir, f"{m}.csv")
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['pod'], row['timestamp'])
                data[key][m] = row[m]
    except FileNotFoundError:
        print(f"Warning: {file_path} not found, skipping...")

output_path = os.path.join(target_dir, 'master_metrics.csv')
with open(output_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['pod', 'timestamp'] + metrics)
    writer.writeheader()
    for (pod, ts) in sorted(data.keys(), key=lambda x: (x[1], x[0])):
        row = {'pod': pod, 'timestamp': ts}
        row.update({m: data[(pod, ts)].get(m, "0") for m in metrics})
        writer.writerow(row)
EOF

echo "Done! All files are in $TARGET_DIR"