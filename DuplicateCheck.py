import os
from tqdm import tqdm
import json
import platform

# === CONFIGURABLE ===
cwd = os.getcwd()
image_exts = ('.jpg', '.jpeg', '.png')
n = 20  # Number of characters to compare
flagShowMatches = True
flagAutoShowLogs = False
# === GLOBALS ===
datasets = []
base_index = 0
base_dataset = None
base_img_path = ""
base_prefixes = set()
match_log = {}  # dataset_name -> list of dicts with image and label paths

# === FUNCTIONS ===
def find_datasets():
    """Returns all dataset folders with images and labels."""
    datasets = []
    for name in os.listdir(cwd):
        subdir = os.path.join(cwd, name)
        if os.path.isdir(subdir):
            if os.path.isdir(os.path.join(subdir, "images")) and os.path.isdir(os.path.join(subdir, "labels")):
                datasets.append(name)
    return datasets

def collect_image_prefixes(images_path):
    """Collects filename prefixes (first n chars) of images."""
    prefixes = set()
    for root, _, files in os.walk(images_path):
        for file in files:
            if file.lower().endswith(image_exts):
                prefixes.add(file[:n])
    return prefixes

def dataset_selection():
    global datasets, base_index, base_dataset, base_img_path, base_prefixes

    print("Scanning for datasets...\n")
    datasets = find_datasets()

    if not datasets:
        print("No valid datasets found.")
        exit()

    # === Dataset Selection ===
    print("Found datasets:")
    for i, name in enumerate(datasets):
        print(f"{i+1}. {name}")
    base_index = int(input("\nSelect the base dataset (number): ")) - 1

    if base_index < 0 or base_index >= len(datasets):
        print("Invalid selection.")
        exit()

    base_dataset = datasets[base_index]
    print(f"\nSelected base dataset: {base_dataset}")
    print(f"Matching based on first {n} characters of image filenames.")

    # === Collect base prefixes ===
    print("Collecting image prefixes from base dataset...")
    base_img_path = os.path.join(cwd, base_dataset, "images")
    base_prefixes = collect_image_prefixes(base_img_path)

def find_duplicates():
    global match_log
    match_log = {dataset: [] for dataset in datasets}

    print("Searching for duplicates in other datasets...\n")
    total_matches = 0

    # Step 1: Index full filenames from base dataset by prefix
    base_img_path = os.path.join(cwd, base_dataset, "images")
    base_file_map = {}  # prefix -> [full filenames]
    for root, _, files in os.walk(base_img_path):
        for file in files:
            if not file.lower().endswith(image_exts):
                continue
            prefix = file[:n]
            base_file_map.setdefault(prefix, []).append(file)

    # Step 2: Scan other datasets
    for dataset in tqdm(datasets, desc="Scanning datasets", unit="dataset"):
        if dataset == base_dataset:
            continue

        img_path = os.path.join(cwd, dataset, "images")
        lbl_path = os.path.join(cwd, dataset, "labels")

        for root, _, files in os.walk(img_path):
            for file in files:
                if not file.lower().endswith(image_exts):
                    continue

                prefix = file[:n]
                if prefix in base_prefixes:
                    # Log match from current dataset
                    match_log[dataset].append({
                        "image": os.path.join(dataset, "images", file),
                        "label": os.path.join(dataset, "labels", os.path.splitext(file)[0] + ".txt")
                    })

                    # Log *all* base dataset files that match prefix (with real full names)
                    for base_filename in base_file_map.get(prefix, []):
                        match_log[base_dataset].append({
                            "image": os.path.join(base_dataset, "images", base_filename),
                            "label": os.path.join(base_dataset, "labels", os.path.splitext(base_filename)[0] + ".txt")
                        })

                    total_matches += 1

    # Step 3: Deduplicate base dataset entries
    seen = set()
    deduped = []
    for entry in match_log[base_dataset]:
        key = (entry["image"], entry["label"])
        if key not in seen:
            deduped.append(entry)
            seen.add(key)
    match_log[base_dataset] = deduped

    # Step 4: Print summary
    print("\nDuplicate Match Summary (excluding base dataset):")
    for dataset, entries in match_log.items():
        if dataset != base_dataset and entries:
            print(f"- {dataset}: {len(entries)} matches")

    base_match_count = len(match_log.get(base_dataset, []))
    print(f"\nBase Dataset '{base_dataset}' has {base_match_count} matching files.")
    print(f"\nTotal duplicate matches (excluding base): {total_matches}")

def save_match_log():
    filename = f"log_{base_dataset}.json"
    filepath = os.path.join(os.getcwd(), filename)

    # Convert any sets (if used) to lists before saving to JSON
    serializable_log = {
        dataset: list(matches) for dataset, matches in match_log.items()
    }

    with open(filepath, "w") as f:
        json.dump(serializable_log, f, indent=4)

    print(f"\nMatch log saved as: {filepath}. View and confirm contents before continuing to data cleansing")

    if flagAutoShowLogs == True:
        # Auto-open the JSON file
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            os.system(f"open '{filepath}'")
        elif platform.system() == "Linux":
            os.system(f"xdg-open '{filepath}'")

def load_log(base_dataset_name):
    json_filename = f"log_{base_dataset_name}.json"
    json_path = os.path.join(cwd, json_filename)

    if not os.path.exists(json_path):
        print(f"Match log not found: {json_path}")
        return None

    with open(json_path, 'r') as f:
        match_log = json.load(f)

    print(f"Loaded match log from: {json_path}")
    return match_log

def delete_duplicates(base_dataset, match_log):
    datasets = list(match_log.keys())
    if base_dataset in datasets:
        datasets.remove(base_dataset)

    # Show deletion options
    print("\n---Deletion Options:---")
    print("1. Delete all duplicates (excluding base dataset)")
    print("2. Manually select datasets to delete from")
    print("3. Delete duplicates only from base dataset")
    print("4. Cancel deletion")

    choice = input("Select option (1-4): ")

    if choice == '1':
        to_delete = datasets
    elif choice == '2':
        print("Available datasets:")
        for i, name in enumerate(datasets):
            print(f"{i+1}. {name}")
        selected = input("Enter dataset numbers (comma separated): ")
        try:
            indices = [int(x.strip())-1 for x in selected.split(',')]
            to_delete = [datasets[i] for i in indices if 0 <= i < len(datasets)]
        except Exception as e:
            print("Invalid input.", e)
            return
    elif choice == '3':
        to_delete = [base_dataset]
    elif choice == '4':
        print("Deletion cancelled.")
        return
    else:
        print("Invalid choice.")
        return

    # Confirm
    print("\nYou are about to delete data from the following datasets:")
    for name in to_delete:
        print(f"- {name}")
    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm != 'y':
        print(" Deletion cancelled.")
        return

    # Perform deletion
    print("\nDeleting files...")

    # Count total files to delete
    total_files = sum(len(match_log.get(name, [])) * 2 for name in to_delete)  # 2 = image + label
    with tqdm(total=total_files, desc="Deleting files") as pbar:
        for name in to_delete:
            for item in match_log.get(name, []):
                for file_path in [item['image'], item['label']]:
                    abs_path = os.path.normpath(os.path.join(cwd, file_path))
                    if os.path.exists(abs_path):
                        try:
                            os.remove(abs_path)
                        except Exception as e:
                            print(f"Error deleting {abs_path}: {e}")
                    else:
                        print(f"File not found (skipped): {abs_path}")
                    pbar.update(1)

    print("\nDeletion completed.")

# === RUN ===
if __name__ == "__main__":
    dataset_selection()
    input("Press Enter to start scanning for duplicates...")
    find_duplicates()
    save_match_log()
    input("Press Enter to start duplicate deletion...")
    match_log = load_log(str(base_dataset))
    # Options 1. delete all matches (except basedataset), 2. manually delete from datasets (input of: 1,2,5,4 (index of dataset)), 3. delete only from base, 4. cancel deletion.
    if match_log:
        delete_duplicates(base_dataset, match_log)
    