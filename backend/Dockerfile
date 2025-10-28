# Use TensorFlow 2.17.0 (latest with Keras 3.x)
FROM tensorflow/tensorflow:2.17.0

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install NumPy 1.26.4 first to ensure compatibility
# Then install additional Flask dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'numpy==1.26.4' && \
    pip install --no-cache-dir --ignore-installed blinker Flask flask-cors gunicorn Pillow

# Copy application code
COPY app.py .

# Copy trained model
COPY model/ /app/model/

# Expose port
EXPOSE 5000

# Run with gunicorn for production with increased timeout for model loading
# Use single worker to avoid race conditions with .keras format model loading
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
