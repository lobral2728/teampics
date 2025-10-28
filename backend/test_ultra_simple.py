import tensorflow as tf
import numpy as np
import sys

print(f"TensorFlow version: {tf.__version__}")

# Create the simplest possible model and test loading
model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(3, activation='softmax')
])

# Test the model first
print("\nTesting model before saving...")
test_img = np.random.rand(1, 224, 224, 3).astype('float32')
pred = model.predict(test_img, verbose=0)
print(f"Pre-save predictions: {pred}")

# Save in different formats and test each
formats_to_test = [
    ('model/ultra_simple.h5', 'H5 format'),
    ('model/ultra_simple.keras', 'Keras 3 format'),
]

for path, desc in formats_to_test:
    print(f"\n{'='*60}")
    print(f"Testing {desc}: {path}")
    print('='*60)
    
    # Save
    try:
        model.save(path)
        print(f"✓ Saved successfully")
    except Exception as e:
        print(f"✗ Save failed: {e}")
        continue
    
    # Try loading with compile=False
    try:
        loaded = tf.keras.models.load_model(path, compile=False)
        print(f"✓ Loaded with compile=False")
        
        # Test prediction
        pred2 = loaded.predict(test_img, verbose=0)
        print(f"✓ Post-load predictions: {pred2}")
        
        if np.allclose(pred, pred2):
            print(f"✓ Predictions match!")
        else:
            print(f"⚠ Predictions differ")
            
    except Exception as e:
        print(f"✗ Load failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("Use whichever format loaded successfully above")
