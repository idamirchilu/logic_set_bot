FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal for SQLite)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Create non-root user
RUN useradd -m -u 1000 botuser
RUN chown -R botuser:botuser /app
USER botuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "app.main"]