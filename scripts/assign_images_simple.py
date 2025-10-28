"""
Assign profile images to users from users.json file.
"""

import json
import random
import csv
import shutil
import os
from pathlib import Path

# Configuration
IMAGE_SOURCE_DIR = Path(r"C:\Users\lobra\Documents\Notebooks\UCB\Capstone\sav\ucb_ml_capstone\data\raw")
WORKSPACE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = WORKSPACE_DIR / "profile_images"
MAPPING_FILE = OUTPUT_DIR / "profile_image_mapping.csv"
USERS_FILE = OUTPUT_DIR / "users.json"

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
    
    search_path = base_dir / subdir
    if not search_path.exists():
        print(f"Warning: Directory {search_path} does not exist")
        return images
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                images.append(os.path.join(root, file))
    
    print(f"Found {len(images)} images in {subdir}")
    return images


def load_users():
    """Load users from JSON file."""
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    return [(u['id'], u['displayName'], u.get('userPrincipalName', '')) for u in users]


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
    
    print(f"\n📊 Distribution for {user_count} users:")
    for category, count in counts.items():
        percentage = (count / user_count) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    # Get available images for each category
    available_images = {}
    for img_type, dir_name in IMAGE_DIRS.items():
        available_images[img_type] = get_all_images(IMAGE_SOURCE_DIR, dir_name)
    
    # Create assignment list
    assignments = []
    
    # Add human images
    if available_images['human']:
        if len(available_images['human']) >= counts['human']:
            selected = random.sample(available_images['human'], counts['human'])
        else:
            selected = random.choices(available_images['human'], k=counts['human'])
        assignments.extend([('human', img) for img in selected])
    
    # Add avatar images
    if available_images['avatar']:
        if len(available_images['avatar']) >= counts['avatar']:
            selected = random.sample(available_images['avatar'], counts['avatar'])
        else:
            selected = random.choices(available_images['avatar'], k=counts['avatar'])
        assignments.extend([('avatar', img) for img in selected])
    
    # Add animal images
    if available_images['animal']:
        if len(available_images['animal']) >= counts['animal']:
            selected = random.sample(available_images['animal'], counts['animal'])
        else:
            selected = random.choices(available_images['animal'], k=counts['animal'])
        assignments.extend([('animal', img) for img in selected])
    
    # Add no picture assignments
    assignments.extend([('no_pic', None) for _ in range(counts['no_pic'])])
    
    # Shuffle to randomize order
    random.shuffle(assignments)
    
    return assignments


def copy_images(assignments):
    """Copy selected images to output directory with standardized names."""
    
    # Create images directory
    images_dir = OUTPUT_DIR / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for idx, (img_type, source_path) in enumerate(assignments):
        if img_type == 'no_pic' or source_path is None:
            results.append((img_type, None, None))
        else:
            # Create standardized filename
            ext = Path(source_path).suffix
            new_filename = f"profile_{idx:04d}_{img_type}{ext}"
            dest_path = images_dir / new_filename
            
            # Copy file
            try:
                shutil.copy2(source_path, dest_path)
                relative_path = f"images/{new_filename}"
                results.append((img_type, relative_path, source_path))
                
                if (idx + 1) % 20 == 0:
                    print(f"  Copied {idx + 1}/{len(assignments)} images...")
                    
            except Exception as e:
                print(f"  ⚠️  Error copying {source_path}: {e}")
                results.append((img_type, None, source_path))
    
    print(f"  ✅ Copied {sum(1 for r in results if r[1] is not None)} images")
    return results


def create_csv(users, image_assignments):
    """Create CSV mapping file."""
    
    with open(MAPPING_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['userId', 'displayName', 'userPrincipalName', 'imageType', 'imagePath', 'sourceImage'])
        
        for idx, (user_id, display_name, upn) in enumerate(users):
            if idx < len(image_assignments):
                img_type, image_path, source_path = image_assignments[idx]
                writer.writerow([
                    user_id,
                    display_name,
                    upn,
                    img_type,
                    image_path if image_path else '',
                    source_path if source_path else ''
                ])
    
    print(f"\n✅ Created mapping CSV: {MAPPING_FILE}")


def main():
    """Main execution."""
    
    print("=" * 70)
    print("🎨 Profile Image Assignment for Azure AD Users")
    print("=" * 70)
    
    # Load users
    print(f"\n📂 Loading users from {USERS_FILE}...")
    users = load_users()
    print(f"✅ Loaded {len(users)} users")
    
    # Assign images
    print(f"\n🎲 Assigning images...")
    assignments = assign_images_to_users(len(users))
    
    # Copy images
    print(f"\n📋 Copying images to {OUTPUT_DIR / 'images'}...")
    image_results = copy_images(assignments)
    
    # Create CSV
    create_csv(users, image_results)
    
    # Summary statistics
    type_counts = {}
    for img_type, _, _ in image_results:
        type_counts[img_type] = type_counts.get(img_type, 0) + 1
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Final Distribution:")
    for img_type in sorted(type_counts.keys()):
        count = type_counts[img_type]
        percentage = (count / len(image_results)) * 100
        print(f"  {img_type:10s}: {count:3d} ({percentage:5.1f}%)")
    
    print(f"\n📁 Output Files:")
    print(f"  Mapping CSV: {MAPPING_FILE}")
    print(f"  Images Dir:  {OUTPUT_DIR / 'images'}")
    print(f"  Total Files: {len(list((OUTPUT_DIR / 'images').glob('*')))}")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Review {MAPPING_FILE}")
    print(f"  2. Update Terraform to create Azure Storage")
    print(f"  3. Upload images and CSV to Azure Storage")
    print(f"  4. Update frontend to load from Azure Storage")


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()
