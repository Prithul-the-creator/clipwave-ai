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

# Copy requirements first for better caching
COPY requirements-minimal.txt requirements.txt

# Install Python dependencies with retry
RUN pip install --no-cache-dir --upgrade setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/
COPY railway_start.py .
COPY runtime.txt .

# Create storage directories
RUN mkdir -p backend/storage/videos

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "railway_start.py"]
