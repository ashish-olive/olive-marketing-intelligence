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

# Create instance directory for database
RUN mkdir -p instance

# Set PYTHONPATH to include all necessary directories
ENV PYTHONPATH=/app:/app/data-pipeline

# Expose the port that Railway will use
EXPOSE $PORT

# Make startup script executable
RUN chmod +x startup.sh

# Set the start command
CMD ["./startup.sh"]
