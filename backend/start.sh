#!/bin/bash
# Railway startup script for Flask backend

# Install dependencies
pip install -r requirements.txt

# Start the Flask app with gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
