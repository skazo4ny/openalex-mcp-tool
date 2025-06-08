#!/bin/bash

# OpenAlex Explorer Startup Script

echo "🚀 Starting OpenAlex Explorer..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if OPENALEX_EMAIL is set
if [ -z "$OPENALEX_EMAIL" ]; then
    echo "⚠️  Warning: OPENALEX_EMAIL environment variable is not set."
    echo "   For better API access, please set it:"
    echo "   export OPENALEX_EMAIL=\"your.email@example.com\""
    echo ""
fi

# Start the application
echo "📚 Launching OpenAlex Explorer on http://127.0.0.1:7860"
python app.py
