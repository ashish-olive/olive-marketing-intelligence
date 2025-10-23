# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary files for database generation
COPY backend/ .
COPY shared/ ./shared/
COPY data-pipeline/ ./data-pipeline/
COPY ml-models/ ./ml-models/

# Create instance directory for database
RUN mkdir -p instance

# Generate the full database during build
RUN python init_railway_db.py

# Expose the port that Railway will use
EXPOSE $PORT

# Set the start command
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]
