FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN pip install playwright && playwright install chromium

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data/documents data/images data/vectorstore

# Default command
CMD ["uvicorn", "app.api.app:app", "--host", "0.0.0.0", "--port", "8000"] 