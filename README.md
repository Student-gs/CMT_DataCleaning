
---

## 🧹 YOLO Dataset Cleaning Scripts

This repository contains Python scripts for cleaning and preparing datasets for YOLO-based object detection training used in our thesis. These utilities helped streamline dataset management by removing duplicates, fixing mislabeled classes, and splitting dataset.

---

### 📂 **Included Scripts**

1. **`DuplicateCheck.py`**

   * Scans datasets for duplicate images.
   * Provides an option to automatically delete duplicates.

2. **`classfix.py`**

   * Ensures class labels match the defined scope (e.g., `Tricycle`).
   * Removes annotations belonging to classes outside the specified target class list.

3. **`Split.py`**

   * Consolidates multiple datasets into one unified structure.
   * Automatically splits data into **train**, **val**, and **test** sets (YOLO-compatible format).

---


### 🖇️ **Tech Stack**

* Python 3.8+
