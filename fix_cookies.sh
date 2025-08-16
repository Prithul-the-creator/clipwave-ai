#!/bin/bash
# Fix cookies file for Docker build

echo "🔍 Checking for cookies.txt..."

# Check if cookies.txt exists and has content
if [ -f "cookies.txt" ] && [ -s "cookies.txt" ]; then
    echo "✅ Found cookies.txt with content"
    echo "📋 File size: $(wc -l < cookies.txt) lines"
    echo "📋 First line: $(head -1 cookies.txt)"
else
    echo "⚠️ No valid cookies.txt found, creating empty file"
    echo "# Empty cookies file - YouTube authentication may be limited" > cookies.txt
fi

echo "✅ Cookies setup complete"
