"""
Build inference model by loading only the trainable top layers.
Data augmentation and preprocessing layers are skipped (appropriate for production inference).
"""
import tensorflow as tf
import h5py
import numpy as np

print(f"TensorFlow: {tf.__version__}")
print(f"Keras: {tf.keras.__version__}")

from tensorflow.keras import layers, models
from tensorflow.keras.applications import ResNet50

# Create inference model architecture
print("\nBuilding inference model architecture...")

# Input
inputs = layers.Input(shape=(224, 224, 3), name='input')

# Preprocessing for ResNet50 (replaces the manual RGB reordering in original model)
x = tf.keras.applications.resnet50.preprocess_input(inputs)

# Load ResNet50 base with ImageNet weights (frozen)
base_model = ResNet50(
    include_top=False,
    weights='imagenet',  # Use pretrained weights
    input_tensor=x,
    pooling=None
)
base_model.trainable = False

# Get features from base model
features = base_model.output

# Top layers (these are the ones we trained)
x = layers.GlobalAveragePooling2D(name='global_average_pooling2d')(features)
x = layers.Dropout(0.25, name='dropout_1')(x, training=False)
x = layers.Dense(256, activation='relu', name='dense_1')(x)
x = layers.Dropout(0.25, name='dropout_2')(x, training=False)
outputs = layers.Dense(3, activation='softmax', name='output')(x)

# Create model
model = models.Model(inputs=inputs, outputs=outputs, name='resnet50_profilepic_classifier_inference')

print("✓ Model architecture created")
print(f"\nModel has {len(model.layers)} layers")
print(f"Trainable variables: {len(model.trainable_variables)}")

# Now load the trained weights for the top layers
weights_file = 'model/resnet50_profilepic_classifier_weights.h5'

print(f"\nLoading trained weights from {weights_file}...")
try:
    with h5py.File(weights_file, 'r') as f:
        print(f"\nAvailable weight groups in file:")
        for key in f.keys():
            print(f"  {key}")
            if isinstance(f[key], h5py.Group):
                for subkey in f[key].keys():
                    print(f"    {subkey}")
                    
        # Try to load weights for the dense layers we care about
        # dense_4 -> dense_1 (256 units)
        # dense_5 -> output (3 units)
        
        if 'dense_4' in f:
            print("\nLoading dense_4 weights...")
            dense_4_group = f['dense_4']['dense_4']
            kernel = np.array(dense_4_group['kernel:0'])
            bias = np.array(dense_4_group['bias:0'])
            print(f"  kernel shape: {kernel.shape}, bias shape: {bias.shape}")
            model.get_layer('dense_1').set_weights([kernel, bias])
            print("  ✓ Loaded dense_4 -> dense_1")
            
        if 'dense_5' in f:
            print("\nLoading dense_5 weights...")
            dense_5_group = f['dense_5']['dense_5']
            kernel = np.array(dense_5_group['kernel:0'])
            bias = np.array(dense_5_group['bias:0'])
            print(f"  kernel shape: {kernel.shape}, bias shape: {bias.shape}")
            model.get_layer('output').set_weights([kernel, bias])
            print("  ✓ Loaded dense_5 -> output")
            
    print("\n✓ Weights loaded successfully!")
    
    # Save the new model
    output_path = 'model/resnet50_profilepic_classifier_inference.keras'
    model.save(output_path)
    print(f"\n✓ Saved inference model to {output_path}")
    
    # Test the model with a dummy input
    print("\nTesting model with dummy input...")
    dummy_input = tf.random.normal((1, 224, 224, 3))
    predictions = model.predict(dummy_input, verbose=0)
    print(f"Output shape: {predictions.shape}")
    print(f"Predictions sum to: {predictions.sum():.6f} (should be ~1.0)")
    print(f"Prediction probabilities: {predictions[0]}")
    
    # Show model summary
    print("\nModel Summary:")
    model.summary()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

