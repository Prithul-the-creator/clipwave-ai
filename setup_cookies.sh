#!/bin/bash
# Setup cookies file for YouTube authentication

echo "🔍 Checking for cookies.txt..."

if [ -f "cookies.txt" ]; then
    echo "✅ Found cookies.txt, copying to /app/"
    cp cookies.txt /app/cookies.txt
    echo "📋 Cookies file size: $(wc -l < cookies.txt) lines"
else
    echo "⚠️  No cookies.txt found, creating empty file"
    touch /app/cookies.txt
    echo "# Empty cookies file - YouTube authentication may be limited" > /app/cookies.txt
fi

echo "✅ Cookies setup complete"
