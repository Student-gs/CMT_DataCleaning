import os
import json
from collections import defaultdict
from tqdm import tqdm

LOG_FILE = "label_scan_log.json"

log_path = "class_scan_log.json"

def scan(base_dir="."):
    class_counts = {}
    file_class_map = {}

    # Collect all label files first
    label_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt") and "labels" in root:
                label_files.append(os.path.join(root, file))

    # Scan with tqdm
    for label_path in tqdm(label_files, desc="Scanning label files", unit="file"):
        with open(label_path, "r") as f:
            lines = f.readlines()

        found_classes = []
        for line in lines:
            parts = line.strip().split()
            if parts:
                class_id = parts[0]
                found_classes.append(class_id)
                class_counts[class_id] = class_counts.get(class_id, 0) + 1

        if found_classes:
            file_class_map[label_path] = found_classes

    log_data = {
        "class_counts": class_counts,
        "file_class_map": file_class_map
    }

    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=4)

    print(f" Scan complete. Results saved to '{log_path}'.")

def fix():
    if not os.path.exists(log_path):
        print("No scan log found. Run scan() first.")
        return

    with open(log_path, "r") as f:
        log_data = json.load(f)

    file_class_map = log_data.get("file_class_map", {})

    for file_path in tqdm(file_class_map, desc="Fixing label files", unit="file"):
        new_lines = []
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    parts[0] = "0"  # Force class to 0
                    new_lines.append(" ".join(parts))

        with open(file_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")

    print("Fix complete. All labels set to class 0.")

# ---MAIN---
scan()
input("Press enter to fix class")
fix()
