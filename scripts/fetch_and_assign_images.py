"""
Fetch users from Azure AD and assign profile images.
This script combines Graph API calls with image assignment.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add parent directory to path to import the assignment script
sys.path.insert(0, str(Path(__file__).parent))
from assign_profile_images import assign_images_to_users, copy_and_rename_images, create_mapping_csv, OUTPUT_DIR, MAPPING_FILE


def get_users_from_azure():
    """Fetch users from Azure AD using Azure CLI."""
    
    print("Fetching users from Azure AD...")
    
    try:
        # Run az cli command to get users
        result = subprocess.run(
            ['az', 'rest', '--method', 'GET', 
             '--url', 'https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName&$top=999'],
            capture_output=True,
            text=True,
            check=True
        )
        
        data = json.loads(result.stdout)
        users = data.get('value', [])
        
        print(f"Retrieved {len(users)} users from Azure AD")
        
        # Return list of (userId, displayName) tuples
        return [(user['id'], user['displayName']) for user in users]
        
    except subprocess.CalledProcessError as e:
        print(f"Error fetching users: {e}")
        print(f"Error output: {e.stderr}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []


def main():
    """Main execution function."""
    
    print("=" * 70)
    print("Azure AD Profile Image Assignment")
    print("=" * 70)
    
    # Fetch real users from Azure AD
    users = get_users_from_azure()
    
    if not users:
        print("\nError: No users retrieved from Azure AD")
        print("Make sure you're logged in: az login")
        return 1
    
    user_count = len(users)
    print(f"\nProcessing {user_count} users...")
    
    # Assign images based on percentages
    assignments = assign_images_to_users(user_count)
    
    # Copy images to output directory
    print(f"\nCopying images to {OUTPUT_DIR}...")
    copied_assignments = copy_and_rename_images(assignments, OUTPUT_DIR)
    
    # Create CSV mapping with real user data
    create_mapping_csv(users, copied_assignments, MAPPING_FILE)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Assignment Complete!")
    print("=" * 70)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Mapping file: {MAPPING_FILE}")
    print(f"Images directory: {OUTPUT_DIR / 'images'}")
    
    # Statistics
    type_counts = {}
    for _, img_type, _, _ in copied_assignments:
        type_counts[img_type] = type_counts.get(img_type, 0) + 1
    
    print("\n📊 Final distribution:")
    for img_type, count in sorted(type_counts.items()):
        percentage = (count / len(copied_assignments)) * 100
        print(f"  {img_type}: {count} ({percentage:.1f}%)")
    
    print(f"\n🎯 Next steps:")
    print(f"1. Review the mapping file: {MAPPING_FILE}")
    print(f"2. Check the images directory: {OUTPUT_DIR / 'images'}")
    print(f"3. Run Terraform to create Azure Storage and upload files")
    
    return 0


if __name__ == "__main__":
    import random
    random.seed(42)  # For reproducibility
    sys.exit(main())
