# Model Accuracy Fix Plan

## Problem Summary
The deployed model has poor accuracy (<50%) because:
1. **Missing trained weights**: Using ImageNet weights instead of your fine-tuned weights
2. **Preprocessing mismatch**: Backend wasn't applying ResNet50-specific preprocessing (FIXED)

## Root Cause
Your original `.keras` model file has a Keras 3.x bug in the `RandomFlip` layer that prevents loading. We worked around it by rebuilding the model architecture, but couldn't extract your trained weights properly.

---

## Solution Options (Pick One)

### ⭐ **Option 1: Export from Google Colab (RECOMMENDED - 10 minutes)**

**Why**: Gets your actual trained model with all fine-tuned weights.

**Steps**:
1. Open your training notebook in Google Colab
2. Add this cell and run it:

```python
from tensorflow import keras

# Load your trained model
model = keras.models.load_model('resnet50_profilepic_classifier.keras')

# Save as H5 format (Keras 2.x compatible - no versioning bugs)
model.save('resnet50_profilepic_classifier_v2.h5', save_format='h5')

# Download the file
from google.colab import files
files.download('resnet50_profilepic_classifier_v2.h5')
```

3. Place the downloaded `.h5` file in `backend/model/`
4. Update `app.py` MODEL_PATH to use the new file
5. Rebuild and redeploy Docker image

**Expected Result**: Full accuracy restored (should match Colab performance)

---

### **Option 2: Fix the .keras File (30-60 minutes)**

**Why**: Repairs the broken config in your existing model file.

**Steps**:
1. Run the repair script:
```bash
cd backend
docker run --rm -v ${PWD}:/app/backend python backend/fix_keras_model.py
```

2. Test the fixed model:
```bash
docker run --rm -v ${PWD}/model:/app/model backend-test python -c "
import tensorflow as tf
model = tf.keras.models.load_model('/app/model/resnet50_profilepic_classifier_fixed.keras')
print('✓ Model loaded successfully')
print('✓ Input shape:', model.input_shape)
"
```

3. If successful:
   - Update `app.py` MODEL_PATH to `resnet50_profilepic_classifier_fixed.keras`
   - Rebuild and redeploy

**Expected Result**: Should restore accuracy if the fix works

---

### **Option 3: Manually Load Weights (Advanced - 1-2 hours)**

**Why**: Extract weights from `.keras` file and load them into the inference model.

**Steps**:
1. The weights are already extracted: `model/resnet50_profilepic_classifier_weights.h5`
2. Modify `build_inference_model.py` to properly map and load weights
3. Challenge: Weight names don't match (dense/dense_1 vs dense_4/dense_5)
4. Requires manual layer-by-layer weight copying

**Expected Result**: Partial accuracy improvement (top layers trained, base ImageNet)

---

## ✅ Already Fixed

**Preprocessing Issue**: Updated `app.py` to apply `preprocess_input()` which:
- Converts RGB [0,255] to ResNet50's expected format
- Subtracts ImageNet mean values per channel
- Matches the preprocessing used during training

This fix alone may provide some improvement, but **Option 1 is still critical** to get your trained weights back.

---

## Testing After Fix

1. **Build new Docker image**:
```bash
cd backend
docker build -t backend-test .
```

2. **Test locally with sample images**:
```bash
# Run container
docker run -d -p 5000:5000 --name backend-test backend-test

# Test with images from different classes
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_image_here"}'
```

3. **Deploy to Azure**:
```bash
# Tag and push
docker tag backend-test azuretest001acr.azurecr.io/healthcheck-backend:latest
docker push azuretest001acr.azurecr.io/healthcheck-backend:latest

# Update container app
az containerapp update \
  --name healthcheck-backend \
  --resource-group azuretest001 \
  --image azuretest001acr.azurecr.io/healthcheck-backend:latest
```

4. **Verify accuracy**:
   - Test with known animal, avatar, and human images
   - Check predictions match expected classes
   - Verify confidence scores are high (>0.7 for correct class)

---

## Other Considerations

### Do we need to build in Azure?
**No.** The model training should stay in Google Colab (free GPU). Azure is just for deployment/hosting.

### Preprocessing Requirements
**Yes, critical!** Your images must be preprocessed identically to training:
- ✅ Resize to 224x224 ✓ (already doing this)
- ✅ Convert to RGB ✓ (already doing this)
- ✅ Apply ResNet50 preprocess_input ✓ (just added)
- ❌ Data augmentation (RandomFlip, etc.) - should NOT be applied during inference

### Data Augmentation Layers
The RandomFlip/RandomRotation layers in your training model should **only run during training**, not inference. The inference model we built correctly excludes these (they cause the loading bug and shouldn't run in production anyway).

### Memory/Performance
Current setup (1 worker, 1Gi RAM) is fine for testing. If you need to handle more traffic:
- Increase workers (use `--preload` to avoid race condition)
- Convert to .h5 format (avoids temporary file extraction)
- Scale up container resources

---

## Expected Timeline

| Task | Time | Priority |
|------|------|----------|
| Export .h5 from Colab | 10 min | ⭐⭐⭐⭐⭐ |
| Update MODEL_PATH | 1 min | ⭐⭐⭐⭐⭐ |
| Rebuild Docker image | 5 min | ⭐⭐⭐⭐⭐ |
| Test locally | 5 min | ⭐⭐⭐⭐ |
| Deploy to Azure | 10 min | ⭐⭐⭐⭐ |
| Validate accuracy | 15 min | ⭐⭐⭐⭐⭐ |
| **Total** | **~45 min** | |

---

## Success Criteria

✅ Model loads without errors (already achieved)  
✅ Preprocessing matches training (just fixed)  
🎯 **Accuracy matches Colab performance (>90%?)** ← Main goal  
🎯 **Predictions vary correctly across animal/avatar/human**  
🎯 **Confidence scores are high for correct predictions**  

---

## Questions to Answer Tomorrow

1. **What was your accuracy in Google Colab?** (baseline to match)
2. **Do you have the Colab notebook accessible?** (for Option 1)
3. **Are you seeing any pattern to the misclassifications?** (all predicting same class? random?)
4. **What format was the training data?** (to verify preprocessing matches)

---

## Files Modified Today

- ✅ `app.py` - Added ResNet50 preprocessing
- ✅ `fix_keras_model.py` - Script to repair .keras config
- ✅ `build_inference_model.py` - Creates inference model (currently using ImageNet weights)
- ✅ Deployed to Azure with single-worker configuration

**Next Step**: Export your trained model from Google Colab in H5 format 🚀
