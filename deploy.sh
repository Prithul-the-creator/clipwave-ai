#!/bin/bash

echo "🚀 ClipWave AI Deployment Script"
echo "=================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ No remote repository found. Please add your GitHub repository:"
    echo "   git remote add origin https://github.com/yourusername/your-repo.git"
    exit 1
fi

echo "✅ Git repository ready"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Deploy to production" || echo "No changes to commit"
git push origin main || git push origin master

echo ""
echo "🎉 Code pushed to GitHub!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Create New Project → Deploy from GitHub repo"
echo "4. Select this repository"
echo "5. Add environment variable: OPENAI_API_KEY=your_api_key"
echo "6. Deploy!"
echo ""
echo "🌐 Your app will be available at: https://your-app.railway.app"
