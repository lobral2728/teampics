import tensorflow as tf
from tensorflow import keras
import numpy as np
import sys

print(f"TensorFlow version: {tf.__version__}")
print(f"Python version: {sys.version}")

model_path = 'model/simple_classifier.h5'
print(f"\nAttempting to load model from: {model_path}")

try:
    # Try different loading methods
    print("\n1. Trying keras.models.load_model()...")
    model = keras.models.load_model(model_path, compile=False)
    print("✓ Model loaded successfully with compile=False!")
    
    # Test prediction
    print("\n2. Testing prediction...")
    test_image = np.random.rand(1, 224, 224, 3).astype('float32')
    predictions = model.predict(test_image, verbose=0)
    print(f"✓ Predictions: {predictions}")
    print(f"✓ Model is working!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
