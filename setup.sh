#!/bin/bash

# OpenAlex Explorer Setup Script

echo "🛠️  Setting up OpenAlex Explorer..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your email for OpenAlex API:"
echo "   export OPENALEX_EMAIL=\"your.email@example.com\""
echo ""
echo "2. Run the application:"
echo "   ./start.sh"
echo ""
echo "3. Or run manually:"
echo "   source venv/bin/activate"
echo "   python app.py"
