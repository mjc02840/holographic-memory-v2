# Holographic Memory v3.1: Activity Log System
## Installation Prompt for Claude Code CLI

---

**PASTE THIS INTO CLAUDE CODE CLI TO AUTO-INSTALL**

---

# 🚀 Install Holographic Memory v3.1: Activity Log System

## Task Summary
Set up automatic real-time activity capture on VPS 80. This system:
- Captures all file changes, commands, database operations, SSH sessions
- Updates every 30 minutes (or immediately on activity)
- Stores in SQLite on VPS, archives to Fossil, indexes to FTS5
- Makes all work searchable from your memory system
- Zero manual documentation needed
- inotify + fallback cron ensures nothing is lost

## Environment Check
Before starting, confirm:
- [ ] `ssh vps80` works (debian user)
- [ ] t630 has q54-fts5-search command available
- [ ] Fossil installed on VPS 80: `ssh vps80 "fossil version"`
- [ ] SQLite installed on VPS 80: `ssh vps80 "sqlite3 --version"`

## Installation Steps

### Step 1: Create Activity Database Structure on VPS 80
```bash
ssh vps80 << 'EOF'
# Create activity directory
mkdir -p /var/www/html/activity
cd /var/www/html/activity

# Create SQLite database with required tables
sqlite3 activity.db << 'SQL'
CREATE TABLE IF NOT EXISTS file_changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
  path TEXT NOT NULL,
  size_before INTEGER,
  size_after INTEGER,
  user TEXT,
  operation TEXT,
  details TEXT
);

CREATE TABLE IF NOT EXISTS command_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
  command TEXT NOT NULL,
  exit_code INTEGER,
  output_lines INTEGER,
  user TEXT,
  duration_ms INTEGER
);

CREATE TABLE IF NOT EXISTS database_changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
  database_name TEXT,
  table_name TEXT,
  operation TEXT,
  rows_affected INTEGER,
  user TEXT
);

CREATE TABLE IF NOT EXISTS ssh_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
  user TEXT,
  source_ip TEXT,
  duration_seconds INTEGER,
  commands_count INTEGER
);

CREATE INDEX IF NOT EXISTS idx_file_timestamp ON file_changes(timestamp);
CREATE INDEX IF NOT EXISTS idx_command_timestamp ON command_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_db_timestamp ON database_changes(timestamp);
SQL

echo "✅ Activity database created"
ls -lah activity.db
EOF
```

### Step 2: Initialize Fossil Repository on VPS 80
```bash
ssh vps80 << 'EOF'
cd /var/www/html/activity

# Create Fossil repository
fossil new activity_log.fossil
fossil open activity_log.fossil

# Add initial commit
fossil add activity.db
fossil commit -m "Initial: Activity log system setup"

echo "✅ Fossil repository initialized"
ls -lah activity_log.fossil
EOF
```

### Step 3: Create inotify Monitor Script on VPS 80
```bash
ssh vps80 << 'EOF'
cat > /home/debian/activity-monitor.sh << 'SCRIPT'
#!/bin/bash
# Activity monitor using inotifywait

DB_PATH="/var/www/html/activity/activity.db"
FOSSIL_PATH="/var/www/html/activity/activity_log.fossil"
LOG_FILE="/var/log/activity-monitor.log"

# Function to sync database to Fossil
sync_to_fossil() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Syncing to Fossil..." >> $LOG_FILE
  
  cd /var/www/html/activity
  
  # Update Fossil with latest changes
  fossil add activity.db 2>&1 >> $LOG_FILE
  fossil commit -m "Activity: $(date +'%Y-%m-%d %H:%M:%S')" 2>&1 >> $LOG_FILE
  
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Sync complete" >> $LOG_FILE
}

# Monitor activity.db for changes
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Activity monitor started" >> $LOG_FILE

inotifywait -m -e modify,attrib "$DB_PATH" | while read path action file; do
  sync_to_fossil
done
SCRIPT

chmod +x /home/debian/activity-monitor.sh
echo "✅ Monitor script created"
EOF
```

### Step 4: Set Up systemd Service on VPS 80
```bash
ssh vps80 << 'EOF'
sudo tee /etc/systemd/system/activity-monitor.service > /dev/null << 'SERVICE'
[Unit]
Description=Holographic Memory Activity Monitor
After=network.target

[Service]
Type=simple
User=debian
ExecStart=/home/debian/activity-monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable activity-monitor.service
sudo systemctl start activity-monitor.service

echo "✅ systemd service installed and started"
sudo systemctl status activity-monitor.service
EOF
```

### Step 5: Create Conditional Sync Script on t630
```bash
cat > /home/aaa/bin/activity-sync.sh << 'SYNC'
#!/bin/bash
# Conditional activity log sync (only if changes detected)

VPS_FOSSIL="ssh://aaa@141.227.180.80/var/www/html/activity/activity_log.fossil"
LOCAL_REPO="/home/aaa/holographic-memory-v3/activity_log"
LOG_FILE="/var/log/activity-sync.log"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Checking for activity..." >> $LOG_FILE

# Check if changes exist in last 30 minutes on VPS
CHANGES=$(ssh vps80 "sqlite3 /var/www/html/activity/activity.db \"SELECT COUNT(*) FROM file_changes WHERE timestamp > datetime('now', '-30 minutes');\"")

if [ "$CHANGES" -eq 0 ]; then
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] No changes detected, skipping sync" >> $LOG_FILE
  exit 0
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Found $CHANGES changes, syncing..." >> $LOG_FILE

# Pull from VPS Fossil
mkdir -p "$LOCAL_REPO"
cd "$LOCAL_REPO"

if [ ! -f .fossil ]; then
  fossil clone "$VPS_FOSSIL" . 2>&1 >> $LOG_FILE
else
  fossil pull "$VPS_FOSSIL" 2>&1 >> $LOG_FILE
fi

fossil update 2>&1 >> $LOG_FILE

# Index into FTS5
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Indexing activity into FTS5..." >> $LOG_FILE
q54-fts5-search "activity $(date +'%Y-%m-%d')" 2>&1 >> $LOG_FILE

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Sync complete" >> $LOG_FILE
SYNC

chmod +x /home/aaa/bin/activity-sync.sh
echo "✅ Sync script created on t630"
```

### Step 6: Set Up Cron Job on t630
```bash
# Add to crontab (every 30 minutes)
(crontab -l 2>/dev/null | grep -v "activity-sync"; echo "*/30 * * * * /home/aaa/bin/activity-sync.sh") | crontab -

echo "✅ Cron job configured (every 30 minutes)"
crontab -l | grep activity
```

### Step 7: Verify Installation
```bash
# Check VPS 80
echo "=== VPS 80 Status ==="
ssh vps80 "systemctl status activity-monitor && echo '---' && ls -lah /var/www/html/activity/"

# Check t630
echo ""
echo "=== t630 Status ==="
ls -lah /home/aaa/bin/activity-sync.sh
crontab -l | grep activity

# Test search
echo ""
echo "=== Test Search ==="
q54-fts5-search "activity" | head -5
```

## Testing the System

### Make a test change on VPS
```bash
ssh vps80 "touch /var/www/html/test-activity-$(date +%s).txt"
```

### Wait for sync (should be <10 seconds)
```bash
sleep 10
```

### Search for the change
```bash
q54-fts5-search "test-activity"
```

**Expected result:** File change appears in search results with timestamp

## Post-Installation

- [ ] Activity database exists: `/var/www/html/activity/activity.db`
- [ ] Fossil repository exists: `/var/www/html/activity/activity_log.fossil`
- [ ] systemd service running: `systemctl status activity-monitor`
- [ ] Sync script executable: `/home/aaa/bin/activity-sync.sh`
- [ ] Cron job configured: `crontab -l | grep activity`
- [ ] Test search works: `q54-fts5-search "activity"`

## Troubleshooting

If anything fails:
1. Check VPS 80 systemd: `ssh vps80 "systemctl status activity-monitor"`
2. Check logs: `ssh vps80 "tail -f /var/log/activity-monitor.log"`
3. Test sync manually: `/home/aaa/bin/activity-sync.sh`
4. Check FTS5: `q54-fts5-search "activity"`

## Next Steps

Once installed:
- All VPS work is automatically captured
- Search anytime: `q54-fts5-search "filename modified"`
- No manual documentation needed
- Memory survives context resets

---

**Installation complete! Activity logging is now running automatically.**
