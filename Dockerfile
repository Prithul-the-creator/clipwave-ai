FROM node:18-alpine AS frontend-builder

# Set working directory for frontend build
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY . .

# Build frontend
RUN npm run build

# Python runtime
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/dist ./dist

# Copy other necessary files
COPY start_production.py .

# Copy cookies file (required for restricted content)
COPY cookies.txt ./

# Create storage directory
RUN mkdir -p storage/videos

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "start_production.py"] 
