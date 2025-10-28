"""
Reconstruct the model architecture manually to avoid Keras version incompatibilities.
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import h5py
import numpy as np

# Recreate the exact model architecture
def create_model():
    """Recreate the ResNet50 profile picture classifier architecture."""
    
    # Input layer
    inputs = layers.Input(shape=(224, 224, 3), name='image')
    
    # Data augmentation (without deprecated parameters)
    x = layers.RandomFlip('horizontal')(inputs)
    x = layers.RandomRotation(0.05, fill_mode='reflect')(x)
    x = layers.RandomZoom(0.1, fill_mode='reflect')(x)
    x = layers.RandomContrast([0, 0.2])(x)
    x = layers.RandomBrightness([-0.2, 0.2])(x)
    
    # Preprocessing (skip for now - try simple approach first)
    # The original preprocessing might not be critical for loading weights
    pass
    
    # ResNet50 base
    base_model = keras.applications.ResNet50(
        include_top=False,
        weights=None,
        input_shape=(224, 224, 3),
        pooling=None
    )
    base_model.trainable = False
    
    x = base_model(x, training=False)
    
    # Custom top layers
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.25)(x, training=False)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.25)(x, training=False)
    outputs = layers.Dense(3, activation='softmax')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs, name='resnet50_profilepic_classifier')
    
    return model

if __name__ == '__main__':
    print(f"TF: {tf.__version__}")
    print(f"Keras: {keras.__version__}")
    
    # Create the model architecture
    print("\nCreating model architecture...")
    model = create_model()
    print("Model architecture created successfully!")
    print(f"Model has {len(model.weights)} weight tensors")
    
    # Try to load weights from .keras file using h5py
    print("\nAttempting to extract weights from .keras file...")
    try:
        with h5py.File('model/resnet50_profilepic_classifier.keras', 'r') as f:
            print("Successfully opened .keras file as HDF5")
            
            # .keras format stores weights under 'model_weights' group
            if 'model_weights' in f:
                print("Found 'model_weights' group")
                def explore_group(g, prefix=''):
                    for key in g.keys():
                        item = g[key]
                        if isinstance(item, h5py.Group):
                            print(f"{prefix}{key}/ (group)")
                            explore_group(item, prefix + '  ')
                        elif isinstance(item, h5py.Dataset):
                            print(f"{prefix}{key} (dataset: {item.shape}, {item.dtype})")
                
                explore_group(f['model_weights'])
            else:
                print("Available top-level keys:", list(f.keys()))
                
    except Exception as e:
        print(f"Error: {e}")
        print("\nAlternative: Try to load just the config and create weights manually")
