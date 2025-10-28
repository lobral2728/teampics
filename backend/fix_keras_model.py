"""
Fix the .keras model by removing the problematic data_format parameter
from RandomFlip layer in the config.json, then rebuild the .keras file.
"""
import zipfile
import json
import shutil
import os
import tempfile

keras_file = 'model/resnet50_profilepic_classifier.keras'
output_file = 'model/resnet50_profilepic_classifier_fixed.keras'

print("=" * 60)
print("Fixing .keras model config...")
print("=" * 60)

# Create temporary directory
temp_dir = tempfile.mkdtemp()
print(f"\nWorking in: {temp_dir}")

try:
    # Extract .keras (ZIP) file
    print("\n1. Extracting .keras file...")
    with zipfile.ZipFile(keras_file, 'r') as zf:
        zf.extractall(temp_dir)
        print(f"   Extracted: {', '.join(zf.namelist())}")
    
    # Load config.json
    config_path = os.path.join(temp_dir, 'config.json')
    print("\n2. Loading config.json...")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Find and fix RandomFlip layers
    print("\n3. Searching for RandomFlip layers...")
    fixed_count = 0
    
    def fix_random_flip(layer_config):
        """Recursively fix RandomFlip layers in config"""
        global fixed_count
        
        if isinstance(layer_config, dict):
            # Check if this is a RandomFlip layer
            if layer_config.get('class_name') == 'RandomFlip':
                config_dict = layer_config.get('config', {})
                if 'data_format' in config_dict:
                    print(f"   Found RandomFlip with data_format: {config_dict['data_format']}")
                    del config_dict['data_format']
                    fixed_count += 1
                    print(f"   ✓ Removed data_format parameter")
            
            # Check if this is a Sequential with layers
            if layer_config.get('class_name') == 'Sequential':
                layers = layer_config.get('config', {}).get('layers', [])
                for layer in layers:
                    fix_random_flip(layer)
            
            # Recursively check nested structures
            for key, value in layer_config.items():
                if isinstance(value, (dict, list)):
                    fix_random_flip(value)
        
        elif isinstance(layer_config, list):
            for item in layer_config:
                fix_random_flip(item)
    
    # Fix the config
    fix_random_flip(config)
    
    if fixed_count == 0:
        print("   ✗ No RandomFlip layers found with data_format parameter")
        print("   The config might already be fixed or structured differently")
    else:
        print(f"\n   ✓ Fixed {fixed_count} RandomFlip layer(s)")
    
    # Save modified config
    print("\n4. Saving modified config.json...")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("   ✓ Config saved")
    
    # Create new .keras (ZIP) file
    print("\n5. Creating fixed .keras file...")
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            zf.write(filepath, filename)
            print(f"   Added: {filename}")
    
    print("\n" + "=" * 60)
    print(f"✓ SUCCESS!")
    print(f"✓ Fixed model saved to: {output_file}")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test loading with: docker run --rm -v ${PWD}/model:/app/model backend-test python -c \"import tensorflow as tf; model = tf.keras.models.load_model('/app/model/resnet50_profilepic_classifier_fixed.keras'); print('SUCCESS')\"")
    print("2. If successful, update app.py to use the fixed model")
    print("3. Rebuild and redeploy Docker image")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    print(f"\n6. Cleaning up temporary files...")
    shutil.rmtree(temp_dir)
    print("   ✓ Done")
