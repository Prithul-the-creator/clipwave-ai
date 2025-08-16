# 🚀 ClipWave AI Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

1. **Fork/Clone this repository** to your GitHub account

2. **Go to [Railway](https://railway.app)** and sign up with GitHub

3. **Create New Project** → "Deploy from GitHub repo"

4. **Select your repository** and Railway will automatically detect the configuration

5. **Add Environment Variables**:
   - Go to your project → Variables tab
   - Add: `OPENAI_API_KEY=your_api_key_here`

6. **Deploy** - Railway will automatically build and deploy your app

7. **Get your URL** - Railway will provide a URL like `https://your-app.railway.app`

### Option 2: Render

1. **Fork/Clone this repository** to your GitHub account

2. **Go to [Render](https://render.com)** and sign up with GitHub

3. **Create New Web Service** → Connect your repository

4. **Configure the service**:
   - **Name**: `clipwave-ai-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_production.py`

5. **Add Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key

6. **Deploy** - Render will build and deploy your backend

7. **For Frontend** (optional):
   - Create another Web Service
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview`
   - **Static Publish Directory**: `dist`

### Option 3: Vercel + Railway

1. **Deploy Backend to Railway** (follow Option 1)

2. **Deploy Frontend to Vercel**:
   - Go to [Vercel](https://vercel.com)
   - Import your GitHub repository
   - Vercel will automatically detect it's a Vite app
   - Add environment variable: `VITE_API_URL=https://your-railway-backend.railway.app`

## Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

## Frontend Configuration

If deploying frontend separately, update the API URL in your frontend code:

```typescript
// src/lib/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your OpenAI API key is valid and has credits
2. **CORS Error**: The backend is configured to allow all origins
3. **Port Issues**: Railway/Render will set the PORT environment variable automatically
4. **Build Failures**: Make sure all dependencies are in requirements.txt

### Local Testing

Test your deployment locally first:

```bash
# Test backend
python start_production.py

# Test frontend
npm run build
npm run preview
```

## Production Considerations

1. **File Storage**: Videos are stored locally. For production, consider using cloud storage (AWS S3, etc.)
2. **Database**: Jobs are stored in JSON files. Consider using a proper database (PostgreSQL, etc.)
3. **Scaling**: The current setup is suitable for small to medium usage
4. **Security**: API keys are stored in environment variables

## Support

If you encounter issues:
1. Check the deployment logs
2. Verify environment variables are set correctly
3. Test the API endpoints manually
4. Check the Railway/Render documentation
