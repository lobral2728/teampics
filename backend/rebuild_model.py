"""
Rebuild ResNet50 model compatible with TensorFlow 2.17.0
and load weights from .weights.h5 file
"""
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, Input
from tensorflow.keras.models import Model

print(f"TensorFlow version: {tf.__version__}")

# Build the model architecture (matching the original training setup)
inputs = Input(shape=(224, 224, 3), name='image')

# Load pre-trained ResNet50 (without top layers)
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_tensor=inputs
)

# Freeze the base model
base_model.trainable = False

# Add custom top layers
x = GlobalAveragePooling2D()(base_model.output)
x = Dropout(0.25)(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.25)(x)
outputs = Dense(3, activation='softmax')(x)  # 3 classes: animal, avatar, human

# Create the model
model = Model(inputs=inputs, outputs=outputs, name='resnet50_profilepic_classifier')

print(f"\nModel created successfully")
print(f"Input shape: {model.input_shape}")
print(f"Output shape: {model.output_shape}")

# Try to load weights
try:
    print("\nAttempting to load weights from resnet50_profilepic_classifier.weights.h5...")
    model.load_weights('model/resnet50_profilepic_classifier.weights.h5')
    print("Weights loaded successfully!")
except Exception as e:
    print(f"Could not load weights: {e}")
    print("Trying resnet50_best.weights.h5...")
    try:
        model.load_weights('model/resnet50_best.weights.h5')
        print("Weights loaded successfully from resnet50_best.weights.h5!")
    except Exception as e2:
        print(f"Could not load weights: {e2}")
        print("Model will use ImageNet pre-trained weights for base, random weights for top layers")

# Save in H5 format compatible with TensorFlow 2.17.0
output_path = 'model/resnet50_classifier_tf2.h5'
print(f"\nSaving model to {output_path}...")
model.save(output_path, save_format='h5')
print(f"Model saved successfully!")

# Test the model with a random image
print("\nTesting model with random input...")
import numpy as np
test_image = np.random.rand(1, 224, 224, 3).astype('float32')
predictions = model.predict(test_image, verbose=0)
print(f"Test predictions shape: {predictions.shape}")
print(f"Test predictions: {predictions[0]}")
print(f"Predicted class: {np.argmax(predictions[0])}")

print("\n✅ Model rebuild complete!")
print(f"📁 New model saved at: {output_path}")
print(f"📦 Model size: {round(sum([w.size for w in model.get_weights()]) * 4 / 1024 / 1024, 2)} MB")
