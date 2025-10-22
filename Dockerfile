# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ .

# Expose the port that Railway will use
EXPOSE $PORT

# Set the start command
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120"]
