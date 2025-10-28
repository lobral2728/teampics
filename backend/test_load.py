import tensorflow as tf
import numpy as np

print(f'TF: {tf.__version__}')
print(f'NumPy: {np.__version__}')

try:
    model = tf.keras.models.load_model('model/resnet50_profilepic_classifier.keras', compile=False, safe_mode=False)
    print('✓ Model loaded successfully!')
    print(f'Input shape: {model.input_shape}')
    print(f'Output shape: {model.output_shape}')
    print(f'Model has {len(model.layers)} layers')
except Exception as e:
    print(f'✗ Error loading model: {e}')
    import traceback
    traceback.print_exc()
