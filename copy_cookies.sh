#!/bin/bash
# Copy cookies.txt if it exists

if [ -f "cookies.txt" ]; then
    echo "✅ Found cookies.txt, copying..."
    cp cookies.txt /app/cookies.txt
    echo "📋 Cookies file copied successfully"
else
    echo "⚠️ No cookies.txt found, creating empty file"
    echo "# Empty cookies file" > /app/cookies.txt
fi
