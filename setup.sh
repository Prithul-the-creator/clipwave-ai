#!/bin/bash

echo "🚀 Setting up ClipWave AI Shorts..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created! Please edit it with your API keys."
else
    echo "✅ .env file already exists."
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
npm install

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run './start.sh' to start the application"
echo ""
echo "For more information, see README.md"
