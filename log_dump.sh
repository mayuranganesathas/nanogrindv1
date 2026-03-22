#!/bin/bash
# Dump nanobot-gateway journal logs for today to a daily file.
# Runs every minute via crontab. Overwrites today's file each run (no duplicates).
# Keeps 30 days of history.

LOG_DIR="$HOME/nanogrindv2/logs"
mkdir -p "$LOG_DIR"

TODAY=$(date +%Y-%m-%d)
journalctl --user -u nanobot-gateway --since "$TODAY 00:00:00" --no-pager > "$LOG_DIR/nanobot-$TODAY.log"
find "$LOG_DIR" -name "nanobot-*.log" -mtime +30 -delete
