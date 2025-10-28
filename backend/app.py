from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input
import numpy as np
from PIL import Image
import base64
import io
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the trained model
MODEL_PATH = os.environ.get('MODEL_PATH', '/app/model/resnet50_profilepic_no_aug.h5')
model = None
class_names = ['human', 'avatar', 'animal']  # Order from training data

def load_model():
    """Load the Keras model at startup"""
    global model
    import sys
    print("=" * 50, flush=True)
    print("Starting model loading...", flush=True)
    print(f"Looking for model at: {MODEL_PATH}", flush=True)
    sys.stdout.flush()
    
    try:
        if os.path.exists(MODEL_PATH):
            print(f"Model file found, loading...", flush=True)
            sys.stdout.flush()
            
            # Try direct load first
            try:
                model = tf.keras.models.load_model(MODEL_PATH, compile=False)
                print(f"✓ Model loaded successfully from {MODEL_PATH}", flush=True)
                print(f"✓ Model input shape: {model.input_shape}", flush=True)
                sys.stdout.flush()
            except (TypeError, ValueError, KeyError) as e:
                # If direct load fails, rebuild architecture and load weights
                print(f"⚠ Direct load failed ({type(e).__name__}), rebuilding architecture...", flush=True)
                sys.stdout.flush()
                
                from tensorflow.keras import layers, models
                from tensorflow.keras.applications import ResNet50
                
                # Rebuild model architecture
                inputs = layers.Input(shape=(224, 224, 3))
                x = preprocess_input(inputs)
                base_model = ResNet50(include_top=False, weights=None, input_tensor=x)
                x = layers.GlobalAveragePooling2D()(base_model.output)
                x = layers.Dropout(0.25)(x, training=False)
                x = layers.Dense(256, activation='relu')(x)
                x = layers.Dropout(0.25)(x, training=False)
                outputs = layers.Dense(3, activation='softmax')(x)
                model = models.Model(inputs=inputs, outputs=outputs)
                
                # Try loading weights
                weights_path = MODEL_PATH.replace('.h5', '_weights.h5') if '.h5' in MODEL_PATH else MODEL_PATH
                if os.path.exists(weights_path):
                    model.load_weights(weights_path)
                    print(f"✓ Rebuilt architecture and loaded weights from {weights_path}", flush=True)
                else:
                    # Try loading from the model file anyway
                    model.load_weights(MODEL_PATH)
                    print(f"✓ Rebuilt architecture and loaded weights from {MODEL_PATH}", flush=True)
                    
                print(f"✓ Model input shape: {model.input_shape}", flush=True)
                sys.stdout.flush()
                
        else:
            print(f"Warning: Model file not found at {MODEL_PATH}", flush=True)
            print("Classification will return 'human' as default", flush=True)
            sys.stdout.flush()
    except Exception as e:
        print(f"✗ Error loading model: {str(e)}", flush=True)
        print(f"✗ Error type: {type(e).__name__}", flush=True)
        import traceback
        traceback.print_exc()
        print("Classification will return 'human' as default", flush=True)
        sys.stdout.flush()
    
    print("=" * 50, flush=True)
    sys.stdout.flush()

# Load model at startup
print("=" * 50, flush=True)
print("Starting model loading...", flush=True)
print(f"Looking for model at: {MODEL_PATH}", flush=True)
load_model()
print("=" * 50, flush=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint that returns TensorFlow version"""
    model_status = 'loaded' if model is not None else 'not_loaded'
    return jsonify({
        'status': 'healthy',
        'message': 'Backend API is running',
        'tensorflow_version': tf.__version__,
        'model_status': model_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/tensorflow-version', methods=['GET'])
def tensorflow_version():
    """Get TensorFlow version endpoint"""
    try:
        keras_version = tf.keras.__version__ if hasattr(tf.keras, '__version__') else 'N/A'
    except:
        keras_version = 'N/A'
    
    return jsonify({
        'tensorflow_version': tf.__version__,
        'keras_version': keras_version,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/ping', methods=['GET'])
def ping():
    """Alternative ping endpoint"""
    return jsonify({
        'response': 'pong',
        'tensorflow_version': tf.__version__,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/classify', methods=['POST'])
def classify_image():
    """Classify an image as human, avatar, or animal"""
    try:
        # Get the image data from request
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'error': 'No image data provided',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        image_data = data['image']
        
        # Check if model is loaded
        if model is None:
            return jsonify({
                'error': 'Model not loaded',
                'classification': 'human',
                'confidence': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }), 500
        
        # Decode and process image
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to model input size (224x224)
            image = image.resize((224, 224))
            
            # Convert to numpy array
            img_array = np.array(image)
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
            
            # Apply ResNet50 preprocessing (CRITICAL - must match training)
            # This converts RGB [0,255] to the format ResNet50 expects
            img_array = preprocess_input(img_array)
            
            # Make prediction
            predictions = model.predict(img_array, verbose=0)[0]
            
            predicted_class_idx = np.argmax(predictions)
            confidence = float(predictions[predicted_class_idx])
            classification = class_names[predicted_class_idx]
            
            return jsonify({
                'classification': classification,
                'confidence': confidence,
                'all_predictions': {
                    class_names[i]: float(predictions[i]) 
                    for i in range(len(class_names))
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                'error': f'Error processing image: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to make it accessible from Docker containers
    app.run(host='0.0.0.0', port=5000, debug=True)
