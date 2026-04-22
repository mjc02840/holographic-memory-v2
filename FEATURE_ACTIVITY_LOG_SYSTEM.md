# Feature: Activity Log System for Real-Time Work Tracking
## Holographic Memory v3.1 - Automatic VPS Activity Capture

---

## 🎯 Problem Statement

**The Blind Spot:** Work happens on your VPS that leaves no trace in memory.

- File modifications occur but aren't captured in conversation logs
- Database changes happen without documentation
- Commands execute silently without audit trails
- When context resets, you've lost 30 minutes of undocumented work
- Current memory system only captures text that appears in terminal

**Example Failure:**
- April 21, 13:20 UTC: `index_002.html` modified on VPS 80
- File size: 20KB, user: debian
- No FTS5 record (not in conversation)
- No Fossil record (not committed)
- No memory of what changed or why
- 30 minutes of work completely invisible to AI assistant

**Impact:** Up to 50% of development time lost to memory system issues

---

## ✅ Solution: 3-Tier Activity Log System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ VPS 80 (141.227.180.80)                                         │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Tier 1: Real-Time Capture (SQLite)                         │ │
│ │ Location: /var/www/html/activity/activity.db               │ │
│ │ ├─ file_changes (timestamp, path, size, user)              │ │
│ │ ├─ command_history (command, output, exit_code, user)      │ │
│ │ ├─ database_changes (db, table, operation, rows)           │ │
│ │ └─ ssh_sessions (user, source_ip, duration, commands)      │ │
│ │ Monitor: inotifywait on activity.db (triggers sync on change)│ │
│ └─────────────────────────────────────────────────────────────┘ │
│                             ↓                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Tier 2: Immutable Archive (Fossil)                         │ │
│ │ Location: /var/www/html/activity/activity_log.fossil       │ │
│ │ ├─ Daily dump of SQLite → Fossil (immutable)               │ │
│ │ ├─ SSH accessible: ssh://aaa@141.227.180.80/.../fossil     │ │
│ │ └─ Historical record for audit trail                        │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (SSH sync every 30 min)
┌─────────────────────────────────────────────────────────────────┐
│ t630 (192.168.1.12)                                             │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Tier 3: Searchable Memory (FTS5)                           │ │
│ │ Location: /var/www/html/@@_BIG_BEAUTIFUL_FTS5/db/...       │ │
│ │ ├─ Index all activity from activity_log.fossil             │ │
│ │ ├─ Full-text search: q54-fts5-search "index_002 modified"  │ │
│ │ └─ Instant query results with timestamps                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation & Setup

### For Claude Code CLI Users

**What You Need:**
- SSH access to VPS 80 (debian user, key auth)
- t630 local machine (with q54-fts5-search available)
- Nothing else to download

**Installation Method:**
1. Paste the provided PROMPT into Claude Code CLI
2. Claude Code CLI automatically:
   - SSHes to VPS 80
   - Creates SQLite database and tables
   - Sets up inotify monitoring
   - Creates Fossil wrapper
   - Configures systemd service
   - Sets up SSH sync mechanism
3. Configures t630:
   - Creates sync script
   - Sets up 30-minute cron job
   - Tests FTS5 integration
4. Validates everything works
5. Returns status report

**No manual installation. Claude Code CLI does it all.**

---

## 📋 What Gets Captured (VPS 80)

### file_changes Table
```sql
CREATE TABLE file_changes (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  path TEXT,
  size_before INTEGER,
  size_after INTEGER,
  user TEXT,
  operation TEXT,  -- 'create', 'modify', 'delete'
  details TEXT
);
```

**Examples:**
```
2026-04-21 13:20:15 | /var/www/html/.../index_002.html | 19KB → 20KB | debian | modify
2026-04-23 14:32:10 | /var/www/html/.../activity.db    | 512KB → 513KB | debian | modify
```

### command_history Table
```sql
CREATE TABLE command_history (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  command TEXT,
  exit_code INTEGER,
  output_lines INTEGER,
  user TEXT,
  duration_ms INTEGER
);
```

### database_changes Table
```sql
CREATE TABLE database_changes (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  database_name TEXT,
  table_name TEXT,
  operation TEXT,  -- 'INSERT', 'UPDATE', 'DELETE'
  rows_affected INTEGER,
  user TEXT
);
```

### ssh_sessions Table
```sql
CREATE TABLE ssh_sessions (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  user TEXT,
  source_ip TEXT,
  duration_seconds INTEGER,
  commands_count INTEGER
);
```

---

## 🔄 Real-Time Monitoring (inotifywait)

### How It Works

```
File changes on VPS 80
        ↓ (inotify detects <1ms)
activity.db updated
        ↓ (systemd service triggers)
conditional-activity-sync.sh runs
        ↓
Exports SQLite → Fossil (2 sec)
        ↓
activity_log.fossil created/updated
        ↓ (SSH pulls immediately)
t630 fetches fossil
        ↓
FTS5 indexes activity (2 sec)
        ↓ (Total latency: ~5-10 seconds)
SEARCHABLE in memory
```

### Fallback Mechanism

```
inotifywait monitors 24/7 (primary)
  ├─ Triggers immediately on changes
  └─ If crashes: cron catches up

Cron runs every 30 minutes (secondary fallback)
  ├─ Checks if changes exist since last sync
  ├─ If yes: runs full sync
  └─ If no: skips (zero overhead)
```

**Result:** Nothing ever lost, minimal resource usage

---

## 🔍 Searching the Activity Log

### From Claude Code CLI

```bash
# Search for file changes in last 30 minutes
q54-fts5-search "file_changes 2026-04-23 14:3"

# Search for specific file modifications
q54-fts5-search "index_002.html modified"

# Search for database changes
q54-fts5-search "database_changes INSERT 2026-04-23"

# Search for command history
q54-fts5-search "command_history exit_code"
```

### Search Results Format
```
Name: Activity Log 2026-04-23
Date: 2026-04-23 14:32:10

Activity Record:
- File: /var/www/html/.../index_002.html
- Change: modify
- Size: 19KB → 20KB
- User: debian
- Timestamp: 2026-04-23 14:32:10
```

---

## 📦 Deployment Checklist

### Pre-Installation
- [ ] SSH access to VPS 80 working (test: `ssh vps80`)
- [ ] t630 has q54-fts5-search available
- [ ] Fossil installed on VPS 80
- [ ] PostgreSQL/SQLite available on VPS 80

### Installation
- [ ] Paste prompt into Claude Code CLI
- [ ] Claude Code CLI completes setup (5-10 min)
- [ ] Check VPS 80: `/var/www/html/activity/activity.db` exists
- [ ] Check VPS 80: `systemctl status activity-monitor` running
- [ ] Check t630: `/home/aaa/bin/activity-sync.sh` exists
- [ ] Test search: `q54-fts5-search "activity"`

### Post-Installation
- [ ] Make file change on VPS (touch test file)
- [ ] Wait 10 seconds (inotify latency)
- [ ] Search from t630: `q54-fts5-search "test"`
- [ ] Verify result appears in memory
- [ ] Monitor cron logs: `tail -f /var/log/activity-sync.log`

---

## 🔐 Security Considerations

- All activity logged with user attribution
- Fossil provides audit trail (who made what change)
- SSH key-based auth (no passwords stored)
- inotifywait runs as daemon user
- No external dependencies (pure local system)
- MIT License (audit-friendly)

---

## 📊 Expected Overhead

| Metric | Impact | Notes |
|--------|--------|-------|
| **Disk** | ~500KB/day | activity.db + fossil growth |
| **CPU** | Negligible | inotify passive, ~1% during sync |
| **Network** | ~2KB/sync | Small fossil deltas, 48/day = 96KB |
| **Memory** | ~50MB | inotifywait + systemd service |
| **SSH Connections** | 48/day | Key-based, <1 sec each |

**Total Cost:** Minimal. Easily sustainable on any VPS.

---

## 🛠️ Manual Control Commands (optional)

```bash
# Force immediate sync (on t630)
/home/aaa/bin/activity-sync.sh

# Check activity log status
systemctl status activity-monitor  # (on VPS 80)

# View recent activity (on VPS 80)
sqlite3 /var/www/html/activity/activity.db \
  "SELECT * FROM file_changes ORDER BY timestamp DESC LIMIT 10;"

# Check inotifywait status
ps aux | grep inotifywait

# View sync logs
tail -f /var/log/activity-sync.log
```

---

## 🐛 Troubleshooting

### Activity not appearing in FTS5 search
1. Check VPS 80: `systemctl status activity-monitor`
2. Check t630: `tail -f /var/log/activity-sync.log`
3. Manually trigger: `/home/aaa/bin/activity-sync.sh`
4. Force FTS5 reindex: (handled automatically)

### inotifywait crashed
- Systemd auto-restarts automatically
- Cron fallback catches any missed events at 30-min mark
- Check: `systemctl status activity-monitor`

### Fossil sync failing
- Check SSH key: `ssh -i ~/.ssh/vps80_aaa vps80 "echo ok"`
- Check Fossil: `ssh vps80 "fossil info"`
- Restart service: `systemctl restart activity-monitor`

---

## 📝 What This Solves

✅ **Before (V3.0):** "I don't know what changed on VPS"  
✅ **After (V3.1):** Search memory, find exact timestamp and details

✅ **Before:** Manual documentation of changes  
✅ **After:** Automatic capture, zero manual work

✅ **Before:** Lost 30 min of work when context resets  
✅ **After:** Complete activity log searchable instantly

✅ **Before:** 50% of time lost to memory issues  
✅ **After:** Memory system covers all work automatically

---

## 📄 License

MIT License - Free to use, modify, and distribute.
See LICENSE file for details.

---

## 🙏 Author's Note

This system was created by a Claude Code CLI user who has struggled with context persistence issues for 10 months. After waiting for the Claude Code team to implement automatic memory persistence and seeing it not materialize, they decided to build their own solution and contribute it freely as open source.

**Purpose:** Help all Claude Code CLI users avoid the productivity loss this user experienced.

**Maintenance:** Will be maintained and improved based on community feedback.

---

**Version:** 3.1  
**Status:** Production Ready  
**Last Updated:** 2026-04-23  
**Tested On:** Debian 12 (VPS 80), Debian 12 (t630)
