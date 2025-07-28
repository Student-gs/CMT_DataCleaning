import os
import sys
import shutil
import random
from tqdm import tqdm #make sure tdqm is installed in local system, dami tutorial install lang
'''
The dataset split is carried in steps;
1. Split the datasets to either train[] or test[]; this is to isolate 'test' dataset and ensure unseen data
2. With the train[] we split them to make the 'train' and 'val' dataset using a tempRatio calculated from the original 7:2:1 split; 7:2 = 9 is transmuted to 7.7:2.2 = 10
3. With the test[] we check whether the data is enough to fulfill the 'wishTest_images'; this wish was calculated based on the tempTestRatio of the train[]
4. If data is enough, we continue with test data split

++The split dataset will always have a 7:2:1 ratio, also ensured 'test' dataset is not tainted with seen data
'''

# Setup
parent_dir = os.getcwd()
base_dir = os.path.join(os.getcwd(), "Finaldata") #Output Dataset

# Supported image extensions
image_exts = ('.jpg', '.jpeg', '.png')

# === Fields ===
total_images = 0
wishTotal_images = 0
train_images = 0
test_images = 0
wishTest_images = 0

final_train = 0
final_val = 0
final_test = 0
final_total = 0
#TVT Split
trainRatio = 0.7
valRatio = 0.2
testRatio = 0.1
#TV Split
tempTrainRatio = 0.7778 #purpose of identifying if the remaining folders can fill a test dataset
tempValRatio = 0.2222 
tempTestRatio = 0.1111

#logger
flagDSManual = False
flagDSManual2 = False
flagCSW = False
flagFC = True #always true 

# === Manually specify datasets ===
train_folders = ["richard1", "richard2","richard3","richard4", "6k", "train_and_val"] #name of folders
test_folders = ["test", "test2", "test3", "test4"] 
'''
folder dir:
dataset
|->images
|->labels
'''
# === Functions ===
def countDataSets():
    # Find all datasets (folders containing images and labels)
    dataset_folders = []
    for name in os.listdir(parent_dir):
        subdir = os.path.join(parent_dir, name)
        if os.path.isdir(subdir):
            images_path = os.path.join(subdir, "images")
            labels_path = os.path.join(subdir, "labels")
            if os.path.isdir(images_path) and os.path.isdir(labels_path):
                dataset_folders.append((name, images_path))

    # Count images in each dataset
    print("Dataset Image Counts:")
    print("----------------------")
    for name, images_path in dataset_folders:
        image_count = len([f for f in os.listdir(images_path) if f.endswith(image_exts)])
        print(f"{name}: {image_count} images")
        total_images += image_count

    print("----------------------")
    print(f"Total Images Across All Datasets: {total_images}")

def countDataSetsManual():
    global train_images, test_images, total_images

    if(flagDSManual): 
        print("Train Dataset Image Counts:")
        print("---------------------------")
    for name in train_folders:
        images_path = os.path.join(parent_dir, name, "images")
        if os.path.exists(images_path):
            image_count = len([f for f in os.listdir(images_path) if f.endswith(image_exts)])
            if(flagDSManual): print(f"{name}: {image_count} images")
            train_images += image_count
        else:
            print(f"{name}: 'images' folder not found")

    if(flagDSManual):
        print("\nTest Dataset Image Counts:")
        print("--------------------------")
    for name in test_folders:
        images_path = os.path.join(parent_dir, name, "images")
        if os.path.exists(images_path):
            image_count = len([f for f in os.listdir(images_path) if f.endswith(image_exts)])
            if(flagDSManual): print(f"{name}: {image_count} images")
            test_images += image_count
        else:
            print(f"{name}: 'images' folder not found")

    total_images = test_images + train_images

    if(flagDSManual2):
        print("\n ========= Count Data Set Manually: ===========")
        print(f"Total Training Images: {train_images}")
        print(f"Total Test Images: {test_images}")
        print(f"Combined Total: {total_images}")

def countWishDataSet():
    global train_images, test_images, total_images, wishTest_images, test_images, wishTotal_images
    wishTest_images = int(train_images * tempTestRatio) # calculate wish test
    wishTotal_images = wishTest_images + train_images
    if(flagCSW):
        print("\n ========= Calculate Wish Dataset ===========")
        print(f"Wish Test Images: {wishTest_images}")
        print(f"Wish Total Images: {wishTotal_images}")
    if(wishTest_images > test_images):
        input(f"ERROR: Test Images cannot fulfill Wish Images: {wishTest_images}")
        sys.exit(1)  # Exit with error code 1

def countFinalDataSet():
    global train_images, test_images, total_images, wishTest_images, test_images, wishTotal_images

    if(flagFC):
        print("\n ========= Final Dataset Split Count: ===========")
        print(f"True Training Images: {train_images}")
        print(f"Wish Test Images: {wishTest_images}")
        print(f"Final Total Images: {wishTotal_images}")
    input("Press Enter to Split Dataset...")

def calculateTempRatio():
    print("----------------------")
    print(f"True Data Split Ratio {trainRatio}/ {valRatio}/ {testRatio}")
    print(f"Train and Val Data Split Ratio {tempTrainRatio}/ {tempValRatio}")

def splitTrainAndVal():
    print("----SPLITTING TRAIN AND VAL DATASETS ----")

    # Config
    global base_dir, train_images, test_images, total_images, wishTest_images, test_images, wishTotal_images, final_train, final_val, final_test, final_total
    image_exts = ('.jpg', '.jpeg', '.png')

    # Output structure
    output_dirs = {
        "train_images": os.path.join(base_dir, "images/train"),
        "val_images": os.path.join(base_dir, "images/val"),
        "train_labels": os.path.join(base_dir, "labels/train"),
        "val_labels": os.path.join(base_dir, "labels/val"),
    }

    # Create output folders
    for path in output_dirs.values():
        os.makedirs(path, exist_ok=True)

    # Gather all image-label pairs from train_folders
    all_image_paths = []
    for folder in train_folders:
        images_path = os.path.join(folder, "images")
        labels_path = os.path.join(folder, "labels")
        if os.path.exists(images_path) and os.path.exists(labels_path):
            for fname in os.listdir(images_path):
                if fname.endswith(image_exts):
                    image_file = os.path.join(images_path, fname)
                    label_file = os.path.join(labels_path, os.path.splitext(fname)[0] + ".txt")
                    all_image_paths.append((image_file, label_file))
        else:
            print(f"Warning: Skipping folder '{folder}' due to missing 'images' or 'labels'.")

    # Shuffle and split
    random.shuffle(all_image_paths)
    total = len(all_image_paths)
    train_count = int(total * tempTrainRatio)

    train_data = all_image_paths[:train_count]
    val_data = all_image_paths[train_count:]

    # Copy to new structure with progress bar
    def copy_to_split(pairs, img_dest, lbl_dest, desc):
        for img_src, lbl_src in tqdm(pairs, desc=desc):
            shutil.copy2(img_src, os.path.join(img_dest, os.path.basename(img_src)))
            if os.path.exists(lbl_src):
                shutil.copy2(lbl_src, os.path.join(lbl_dest, os.path.basename(lbl_src)))
            else:
                print(f"Missing label for {img_src}")

    copy_to_split(train_data, output_dirs["train_images"], output_dirs["train_labels"], "Copying Train")
    copy_to_split(val_data, output_dirs["val_images"], output_dirs["val_labels"], "Copying Val")

    # save to final
    final_total += total
    final_train = len(train_data)
    final_val = len(val_data)

def splitTest():
    print("----SPLITTING TEST DATASET----")

    global base_dir, train_images, test_images, total_images, wishTest_images, test_images, wishTotal_images, final_train, final_val, final_test, final_total

    # Output directories
    dest_img_test = os.path.join(base_dir, "images", "test")
    dest_lbl_test = os.path.join(base_dir, "labels", "test")
    os.makedirs(dest_img_test, exist_ok=True)
    os.makedirs(dest_lbl_test, exist_ok=True)

    # Collect all available image paths from test folders
    all_image_paths = []
    for folder in test_folders:
        img_dir = os.path.join(parent_dir, folder, "images")
        if os.path.exists(img_dir):
            image_files = [f for f in os.listdir(img_dir) if f.endswith(image_exts)]
            all_image_paths.extend([(folder, f) for f in image_files])
        else:
            print(f"Warning: {folder}/images not found.")

    # Shuffle and select desired number
    random.shuffle(all_image_paths)
    selected = all_image_paths[:min(wishTest_images, len(all_image_paths))]

    # Copy files
    for folder, img_file in tqdm(selected, desc="Copying test data"):
        src_img_path = os.path.join(parent_dir, folder, "images", img_file)
        src_lbl_path = os.path.join(parent_dir, folder, "labels", os.path.splitext(img_file)[0] + ".txt")

        # Copy image
        shutil.copy2(src_img_path, os.path.join(dest_img_test, img_file))

        # Copy label if exists
        if os.path.exists(src_lbl_path):
            shutil.copy2(src_lbl_path, os.path.join(dest_lbl_test, os.path.basename(src_lbl_path)))
        else:
            print(f"⚠️ Label not found for image {img_file} in {folder}")

    input("Press Enter to continue...")
    final_test = len(selected)
    final_total += final_test

def showResults():
    print("----FINAL DATASET SPLIT----")
    print(f"Train Set:{final_train}")
    print(f"Val Set:{final_val}")
    print(f"Test Set:{final_test}")
    print(f"Total:{final_total}")


countDataSetsManual()
countWishDataSet()
countFinalDataSet()
splitTrainAndVal()
splitTest()
showResults()