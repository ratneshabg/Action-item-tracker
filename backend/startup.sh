#!/bin/bash
# Startup script for Azure App Service

# Install Python dependencies
pip install -r requirements.txt

# Run the application with Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
