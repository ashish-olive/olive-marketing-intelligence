# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ .

# Copy shared modules (needed for database models)
COPY shared/ ./shared/

# Copy data-pipeline (needed for database generation at runtime)
COPY data-pipeline/ ./data-pipeline/

# Copy ml-models (needed for ML inference)
COPY ml-models/ ./ml-models/

# Create data directory for persistent volume
RUN mkdir -p /data

# Create instance directory for database (fallback)
RUN mkdir -p instance

# Set proper permissions for database directory
RUN chmod 777 instance

# Set PYTHONPATH to include all necessary directories
ENV PYTHONPATH=/app:/app/data-pipeline

# Expose port 5000 for Fly.io
EXPOSE 5000

# Set the start command for Fly.io
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120"]
