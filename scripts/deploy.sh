#!/bin/bash
set -e

echo "🚀 Starting Pulse Monolith Deployment..."

# 1. Pull the latest code
echo "📥 Pulling latest code..."
git pull

# 2. Rebuild and restart the containers
echo "🏗️ Building and restarting Docker containers..."
docker compose down
docker compose up --build -d

echo "✅ Deployment successful. Checking status..."
docker compose ps
