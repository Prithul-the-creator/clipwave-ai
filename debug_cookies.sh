#!/bin/bash
# Debug cookies file copying

echo "🔍 Debugging cookies file..."

# List all files in current directory
echo "📂 Files in current directory:"
ls -la

# Try to copy cookies.txt if it exists
if [ -f "cookies.txt" ]; then
    echo "✅ Found cookies.txt in build context"
    cp cookies.txt /app/cookies.txt
    echo "📋 Copied cookies.txt to /app/"
    echo "📋 File size: $(wc -l < cookies.txt) lines"
    echo "📋 First 3 lines:"
    head -3 cookies.txt
else
    echo "❌ cookies.txt not found in build context"
    echo "# Empty cookies file" > /app/cookies.txt
    echo "📋 Created empty cookies.txt"
fi

echo "✅ Debug complete"
