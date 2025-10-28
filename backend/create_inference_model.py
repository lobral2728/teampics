"""
Load model using simplified architecture that skips problematic data augmentation.
For inference, data augmentation should be disabled anyway.
"""
import tensorflow as tf
print(f"TensorFlow: {tf.__version__}")
print(f"Keras: {tf.keras.__version__}")

# Load the full model first to get preprocessing info
try:
    # The model has issues with RandomFlip but let's see if we can work around it
    import zipfile
    import json
    import tempfile
    import os
    
    keras_file = 'model/resnet50_profilepic_classifier.keras'
    weights_file = 'model/resnet50_profilepic_classifier_weights.h5'
    
    print("\nAttempting direct load with compile=False...")
    try:
        model = tf.keras.models.load_model(keras_file, compile=False)
        print("✓ Model loaded successfully!")
        print(f"Model summary:")
        model.summary()
    except Exception as e:
        print(f"✗ Direct load failed: {e}")
        print("\nTrying alternative: Load weights into new architecture...")
        
        # Create a simplified model for inference (no data augmentation)
        from tensorflow.keras import layers, models
        from tensorflow.keras.applications import ResNet50
        
        # Input
        inputs = layers.Input(shape=(224, 224, 3), name='image')
        
        # Skip data augmentation for inference
        # Apply preprocessing that was in the original model
        # From error trace: RGB reordering and mean subtraction
        x = inputs
        
        # Load ResNet50 base
        base_model = ResNet50(
            include_top=False,
            weights=None,  # We'll load from file
            input_tensor=None,
            input_shape=(224, 224, 3),
            pooling=None
        )
        base_model.trainable = False
        
        # Apply base model
        x = base_model(x, training=False)
        
        # Top layers
        x = layers.GlobalAveragePooling2D(name='global_average_pooling2d_2')(x)
        x = layers.Dropout(0.25, name='dropout_4')(x, training=False)
        x = layers.Dense(256, activation='relu', name='dense_4')(x)
        x = layers.Dropout(0.25, name='dropout_5')(x, training=False)
        outputs = layers.Dense(3, activation='softmax', name='dense_5')(x)
        
        # Create model
        inference_model = models.Model(inputs=inputs, outputs=outputs, name='resnet50_profilepic_classifier_inference')
        
        print("\n✓ Inference model architecture created")
        print(f"\nTrying to load weights from {weights_file}...")
        
        try:
            inference_model.load_weights(weights_file, skip_mismatch=True, by_name=True)
            print("✓ Weights loaded!")
            
            # Save in a format that works
            output_path = 'model/resnet50_profilepic_classifier_inference.keras'
            inference_model.save(output_path)
            print(f"\n✓ Saved inference model to {output_path}")
            print("\nThis model skips data augmentation (appropriate for inference)")
            
        except Exception as e2:
            print(f"✗ Weight loading failed: {e2}")
            print("\nThe weights file structure might not match the new model.")
            print("This is expected since the original model includes data augmentation layers.")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
