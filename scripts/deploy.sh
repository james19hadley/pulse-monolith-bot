#!/bin/bash
set -e

echo "🚀 Starting Pulse Monolith Deployment..."

# 1. Pull the latest code
echo "📥 Pulling latest code..."
git pull

# 2. Rebuild and restart the containers
echo "🏗️ Building and restarting Docker containers..."
# We rely on docker compose caching to only rebuild what changed (e.g. your Python code).
# It will only recreate containers whose image or configuration has changed, meaning
# PostgreSQL and Redis won't experience downtime during simple code updates.
docker compose build
docker compose up -d

# Clean up dangling images to save space without destroying build caches
docker image prune -f

# 3. Ensure backup cron job is registered
echo "⏰ Configuring auto-backups (cron)..."
# We grep -v to remove any old identical cron jobs so we don't duplicate, then append the fresh one
CRON_CMD="0 3 * * * /opt/pulse-monolith-bot/scripts/backup_db.sh >> /var/log/pulse_backup.log 2>&1"
(crontab -l 2>/dev/null | grep -v "backup_db.sh" ; echo "$CRON_CMD") | crontab -

echo "✅ Deployment successful. Checking status..."
docker compose ps
