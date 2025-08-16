# Multi-stage build for full-stack application
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY . .

# Build frontend
RUN npm run build

# Backend stage
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements-minimal.txt requirements.txt
RUN pip install --no-cache-dir --upgrade setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/
COPY railway_start.py .
COPY runtime.txt .
COPY copy_cookies.sh .

# Handle cookies file
RUN chmod +x copy_cookies.sh && ./copy_cookies.sh

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/dist ./frontend

# Create storage directories
RUN mkdir -p backend/storage/videos

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "railway_start.py"]
