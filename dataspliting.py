import os
import random
import shutil
from collections import defaultdict

# Set random seed for reproducibility
random.seed(42)

# Paths
images_dir = 'images'
labels_dir = 'labels'

# Output folders
output_base = 'dataset_split'
splits = ['train', 'val', 'test']
for split in splits:
    os.makedirs(os.path.join(output_base, split, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_base, split, 'labels'), exist_ok=True)

# Read all label files and map them by class
class_to_files = defaultdict(list)
all_label_files = [f for f in os.listdir(labels_dir) if f.endswith('.txt')]

for label_file in all_label_files:
    file_path = os.path.join(labels_dir, label_file)
    with open(file_path, 'r') as f:
        lines = f.readlines()
    classes_in_file = set(line.strip().split()[0] for line in lines if line.strip())
    for cls in classes_in_file:
        class_to_files[cls].append(label_file)

# Create a unique list of files
all_files = list(set(all_label_files))

# Initialize splits
split_files = {'train': [], 'val': [], 'test': []}

# Strategy: shuffle and distribute keeping classes balanced
files_per_class = defaultdict(lambda: {'train': [], 'val': [], 'test': []})

for cls, files in class_to_files.items():
    random.shuffle(files)
    n = len(files)
    n_train = int(0.7 * n)
    n_val = int(0.15 * n)
    n_test = n - n_train - n_val

    files_per_class[cls]['train'] = files[:n_train]
    files_per_class[cls]['val'] = files[n_train:n_train+n_val]
    files_per_class[cls]['test'] = files[n_train+n_val:]

# Now merge them, avoiding duplicates
added_files = set()
for split in splits:
    for cls in files_per_class:
        for f in files_per_class[cls][split]:
            if f not in added_files:
                split_files[split].append(f)
                added_files.add(f)

# Final copy
def copy_files(file_list, split):
    for label_file in file_list:
        img_file = label_file.replace('.txt', '.jpg')  # Assuming jpg images
        src_img = os.path.join(images_dir, img_file)
        src_label = os.path.join(labels_dir, label_file)

        dst_img = os.path.join(output_base, split, 'images', img_file)
        dst_label = os.path.join(output_base, split, 'labels', label_file)

        if os.path.exists(src_img) and os.path.exists(src_label):
            shutil.copyfile(src_img, dst_img)
            shutil.copyfile(src_label, dst_label)
        else:
            print(f"Warning: {img_file} or {label_file} not found!")


# Copy for each split
for split in splits:
    copy_files(split_files[split], split)

print("Dataset split completed successfully!")