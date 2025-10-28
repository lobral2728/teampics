"""
Convert problematic .keras model to H5 format that's more universally compatible.
This script uses Keras 3's file format to extract weights and saves in H5 format.
"""
import zipfile
import json
import h5py
import numpy as np

# The .keras format is actually a ZIP file
keras_file = 'model/resnet50_profilepic_classifier.keras'
output_h5 = 'model/resnet50_profilepic_classifier_weights.h5'

print("Extracting .keras file (it's a ZIP)...")
with zipfile.ZipFile(keras_file, 'r') as zf:
    # List contents
    print("\nContents of .keras file:")
    for name in zf.namelist():
        print(f"  {name}")
    
    # Extract config
    if 'config.json' in zf.namelist():
        with zf.open('config.json') as f:
            config = json.load(f)
            print("\nModel config extracted")
            print(f"Model name: {config.get('config', {}).get('name', 'unknown')}")
    
    # Extract model weights
    # Keras 3 .keras format stores weights as .weights.h5
    weights_file = 'model.weights.h5'
    if weights_file in zf.namelist():
        print(f"\nExtracting {weights_file}...")
        zf.extract(weights_file, 'temp/')
        print(f"Extracted to temp/{weights_file}")
        
        # Copy to output location
        import shutil
        shutil.copy(f'temp/{weights_file}', output_h5)
        print(f"Copied weights to {output_h5}")
        
        # Clean up
        import os
        os.remove(f'temp/{weights_file}')
        os.rmdir('temp')
        
        print(f"\n✓ Success! Weights saved to {output_h5}")
        print("You can now load these weights into a recreated model architecture.")
    else:
        print(f"\n✗ {weights_file} not found in .keras archive")
        print("Available files:", zf.namelist())
