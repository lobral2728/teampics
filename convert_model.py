"""
Convert Keras 3.x model to TensorFlow 2.x compatible format
"""
import keras

# Load the Keras 3.x model
print("Loading .keras model...")
model = keras.saving.load_model('backend/model/resnet50_profilepic_classifier.keras')

print(f"Model loaded successfully")
print(f"Input shape: {model.input_shape}")
print(f"Output shape: {model.output_shape}")

# Save in HDF5 format (TensorFlow 2.x compatible)
print("\nSaving as .h5 format...")
model.save('backend/model/resnet50_profilepic_classifier.h5', save_format='h5')

print("Model converted successfully!")
print("New file: backend/model/resnet50_profilepic_classifier.h5")
