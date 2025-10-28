"""
Script to assign random profile images to users based on specified percentages.
- 50% human faces (fairface directory)
- 20% avatar faces (avatars directory)  
- 20% animal faces (animal_faces directory)
- 10% no picture

Creates a CSV mapping file with userId to image path mappings.
"""

import os
import random
import csv
import shutil
from pathlib import Path

# Configuration
IMAGE_SOURCE_DIR = r"C:\Users\lobra\Documents\Notebooks\UCB\Capstone\sav\ucb_ml_capstone\data\raw"
OUTPUT_DIR = Path(__file__).parent.parent / "profile_images"
MAPPING_FILE = OUTPUT_DIR / "profile_image_mapping.csv"

# Image type percentages
IMAGE_DISTRIBUTION = {
    'human': 0.50,      # 50%
    'avatar': 0.20,     # 20%
    'animal': 0.20,     # 20%
    'no_pic': 0.10      # 10%
}

# Directory mappings
IMAGE_DIRS = {
    'human': 'fairface',
    'avatar': 'avatars',
    'animal': 'animal_faces'
}


def get_all_images(base_dir, subdir):
    """Recursively get all image files from a directory and its subdirectories."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    images = []
    
    search_path = Path(base_dir) / subdir
    if not search_path.exists():
        print(f"Warning: Directory {search_path} does not exist")
        return images
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                images.append(os.path.join(root, file))
    
    print(f"Found {len(images)} images in {subdir}")
    return images


def assign_images_to_users(user_count):
    """Assign images to users based on the distribution percentages."""
    
    # Calculate counts for each category
    counts = {
        'human': int(user_count * IMAGE_DISTRIBUTION['human']),
        'avatar': int(user_count * IMAGE_DISTRIBUTION['avatar']),
        'animal': int(user_count * IMAGE_DISTRIBUTION['animal']),
        'no_pic': int(user_count * IMAGE_DISTRIBUTION['no_pic'])
    }
    
    # Adjust for rounding errors
    total_assigned = sum(counts.values())
    if total_assigned < user_count:
        counts['human'] += (user_count - total_assigned)
    
    print(f"\nDistribution for {user_count} users:")
    for category, count in counts.items():
        percentage = (count / user_count) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    # Get available images for each category
    available_images = {}
    for img_type, dir_name in IMAGE_DIRS.items():
        available_images[img_type] = get_all_images(IMAGE_SOURCE_DIR, dir_name)
    
    # Create assignment list with shuffling for randomness
    assignments = []
    
    # Add human images
    if available_images['human']:
        selected = random.sample(available_images['human'], 
                                min(counts['human'], len(available_images['human'])))
        assignments.extend([('human', img) for img in selected])
    
    # Add avatar images
    if available_images['avatar']:
        selected = random.sample(available_images['avatar'],
                                min(counts['avatar'], len(available_images['avatar'])))
        assignments.extend([('avatar', img) for img in selected])
    
    # Add animal images
    if available_images['animal']:
        selected = random.sample(available_images['animal'],
                                min(counts['animal'], len(available_images['animal'])))
        assignments.extend([('animal', img) for img in selected])
    
    # Add no picture assignments
    assignments.extend([('no_pic', None) for _ in range(counts['no_pic'])])
    
    # Shuffle to randomize order
    random.shuffle(assignments)
    
    return assignments


def copy_and_rename_images(assignments, output_dir):
    """Copy selected images to output directory with standardized names."""
    
    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'images').mkdir(exist_ok=True)
    
    copied_assignments = []
    
    for idx, (img_type, source_path) in enumerate(assignments):
        if img_type == 'no_pic' or source_path is None:
            copied_assignments.append((idx, img_type, None, None))
        else:
            # Create standardized filename
            ext = Path(source_path).suffix
            new_filename = f"profile_{idx:04d}_{img_type}{ext}"
            dest_path = output_dir / 'images' / new_filename
            
            # Copy file
            try:
                shutil.copy2(source_path, dest_path)
                relative_path = f"images/{new_filename}"
                copied_assignments.append((idx, img_type, relative_path, source_path))
                
                if (idx + 1) % 10 == 0:
                    print(f"Copied {idx + 1} images...")
                    
            except Exception as e:
                print(f"Error copying {source_path}: {e}")
                copied_assignments.append((idx, img_type, None, source_path))
    
    return copied_assignments


def create_mapping_csv(user_ids, assignments, output_file):
    """Create CSV mapping file with userId, imageType, and imagePath."""
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['userId', 'displayName', 'imageType', 'imagePath', 'sourceImage'])
        
        for idx, (user_id, display_name) in enumerate(user_ids):
            if idx < len(assignments):
                profile_idx, img_type, image_path, source_path = assignments[idx]
                writer.writerow([
                    user_id,
                    display_name,
                    img_type,
                    image_path if image_path else '',
                    source_path if source_path else ''
                ])
    
    print(f"\nMapping CSV created: {output_file}")
    print(f"Total mappings: {len(user_ids)}")


def main():
    """Main execution function."""
    
    print("=" * 60)
    print("Profile Image Assignment Script")
    print("=" * 60)
    
    # For testing, we'll use 121 users (the actual count from your tenant)
    # In production, this would fetch from Microsoft Graph API
    user_count = 121
    
    # Generate sample user data (in production, fetch from Graph API)
    print(f"\nGenerating assignments for {user_count} users...")
    user_ids = [(f"user-{i:03d}", f"User {i:03d}") for i in range(user_count)]
    
    # Assign images
    assignments = assign_images_to_users(user_count)
    
    # Copy images and create mappings
    print(f"\nCopying images to {OUTPUT_DIR}...")
    copied_assignments = copy_and_rename_images(assignments, OUTPUT_DIR)
    
    # Create CSV mapping
    create_mapping_csv(user_ids, copied_assignments, MAPPING_FILE)
    
    # Summary
    print("\n" + "=" * 60)
    print("Assignment Complete!")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Mapping file: {MAPPING_FILE}")
    print(f"Images directory: {OUTPUT_DIR / 'images'}")
    
    # Statistics
    type_counts = {}
    for _, img_type, _, _ in copied_assignments:
        type_counts[img_type] = type_counts.get(img_type, 0) + 1
    
    print("\nFinal distribution:")
    for img_type, count in sorted(type_counts.items()):
        percentage = (count / len(copied_assignments)) * 100
        print(f"  {img_type}: {count} ({percentage:.1f}%)")


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()
