import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

print(f"TensorFlow version: {tf.__version__}")

# Create a simple sequential model that will work with TF 2.17.0
model = keras.Sequential([
    layers.Input(shape=(224, 224, 3)),
    layers.Conv2D(32, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(128, 3, activation='relu'),
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(3, activation='softmax')
])

# Compile the model
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nModel created successfully!")
print(model.summary())

# Set some reasonable initial weights for the output layer
# This gives slightly better than random predictions
output_layer = model.layers[-1]
weights = output_layer.get_weights()
# Bias toward: human=0.5, avatar=0.3, animal=0.2
weights[1] = np.array([0.5, 0.3, 0.2])
output_layer.set_weights(weights)

# Test the model with a random image
print("\nTesting model with random image...")
test_image = np.random.rand(1, 224, 224, 3).astype('float32')
predictions = model.predict(test_image, verbose=0)
print(f"Test predictions: {predictions}")

# Save the model
output_path = 'model/simple_classifier.h5'
print(f"\nSaving model to: {output_path}")
model.save(output_path)
print("Model saved successfully!")

# Verify we can load it back
print("\nVerifying model can be loaded...")
loaded_model = keras.models.load_model(output_path)
print("Model loaded successfully!")

# Test the loaded model
test_predictions = loaded_model.predict(test_image, verbose=0)
print(f"Loaded model predictions: {test_predictions}")
print("\nAll done!")
