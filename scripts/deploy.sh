#!/bin/bash

# Deployment script for Logic Bot

set -e

echo "🚀 Starting deployment of Logic Bot..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
else
    echo "⚠️  .env file not found. Using default values."
fi

# Build and start containers
echo "📦 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ All services are running successfully!"
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Run database migrations
echo "🗄️  Initializing database..."
docker-compose exec bot python -c "
from app.database import db_manager
import asyncio
asyncio.run(db_manager.init_db())
print('Database initialized successfully')
"

echo "🎉 Deployment completed successfully!"
echo "📊 Access pgAdmin at: http://localhost:5050"
echo "🤖 Bot is now running and ready to receive messages!"