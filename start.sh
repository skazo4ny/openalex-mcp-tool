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
    echo "   Setting default email: gradio@gradio.ai"
    export OPENALEX_EMAIL="gradio@gradio.ai"
    echo ""
fi

# Start the application
echo "📚 Launching OpenAlex Explorer on http://127.0.0.1:7860"
python app.py
