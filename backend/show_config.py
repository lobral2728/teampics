"""
Check config from .keras file to understand exact architecture.
"""
import zipfile
import json

keras_file = 'model/resnet50_profilepic_classifier.keras'

with zipfile.ZipFile(keras_file, 'r') as zf:
    # Extract and pretty-print config
    with zf.open('config.json') as f:
        config = json.load(f)
        
        print("Top-level model:")
        print(f"  Name: {config['config']['name']}")
        print(f"  Class: {config['class_name']}")
        print(f"  Number of layers: {len(config['config']['layers'])}")
        print("\nLayer summary:")
        for i, layer in enumerate(config['config']['layers']):
            layer_name = layer.get('config', {}).get('name', layer.get('name', 'unknown'))
            layer_class = layer.get('class_name', 'unknown')
            print(f"  {i+1}. {layer_name} ({layer_class})")
            
            # Show key config for certain layers
            if layer_class in ['Dense', 'Dropout']:
                cfg = layer.get('config', {})
                if 'units' in cfg:
                    print(f"      units={cfg['units']}, activation={cfg.get('activation', 'none')}")
                if 'rate' in cfg:
                    print(f"      rate={cfg['rate']}")
