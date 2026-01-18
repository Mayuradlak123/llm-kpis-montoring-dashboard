#!/bin/bash

echo "🔍 Activating environment variables"
set .env
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate environment variables."
    exit 1
else
    echo "✅ Environment variables activated successfully."
fi


echo "🌐 Starting the FastAPI server."
# Run the FastAPI app
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
if [ $? -ne 0 ]; then
    echo "❌ Failed to start FastAPI server."
    exit 1
else
    echo "✅ FastAPI server terminated successfully."
fi
