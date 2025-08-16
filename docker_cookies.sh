#!/bin/bash
# Handle cookies file for Docker build

echo "🔍 Checking for cookies.txt in build context..."

# Check if cookies.txt exists in the current directory (build context)
if [ -f "cookies.txt" ]; then
    echo "✅ Found cookies.txt in build context"
    echo "📋 File size: $(wc -l < cookies.txt) lines"
    echo "📋 First few lines:"
    head -3 cookies.txt
    echo "✅ Cookies file is ready for use"
else
    echo "⚠️ No cookies.txt found in build context"
    echo "# Empty cookies file - YouTube authentication may be limited" > cookies.txt
    echo "📋 Created empty cookies.txt"
    echo "⚠️ YouTube downloads may be limited without authentication"
fi

echo "✅ Cookies setup complete"
