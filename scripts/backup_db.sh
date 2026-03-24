#!/bin/bash

# Configuration
BACKUP_DIR="/opt/pulse-monolith-bot/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Make sure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting database backup: $BACKUP_FILE"

# Run pg_dump inside the postgres container
# Note: we use the custom compression format (-F c) which is safer and smaller
docker exec -t pulse_postgres pg_dump -U pulse -d pulsedb -F c > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup completed successfully."
else
    echo "Backup failed!"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Rotate backups: Keep only the 2 most recent ones
echo "Cleaning up old backups (keeping only the last 2)..."
ls -tp "$BACKUP_DIR"/db_backup_*.sql 2>/dev/null | grep -v '/$' | tail -n +3 | xargs -I {} rm -- "{}"

echo "Cleanup done."
