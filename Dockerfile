FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd -m -u 1000 botuser
USER botuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "app.main"]