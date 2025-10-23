#!/bin/bash
# Railway startup script with runtime database generation

echo "Starting Olive Marketing Intelligence Backend..."

# Generate database at runtime (if not exists)
echo "Checking database status..."
python startup_with_db.py

# Start the Flask application
echo "Starting Flask application..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
