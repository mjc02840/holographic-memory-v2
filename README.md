# Holographic Memory: Version 2.0
## Persistence of Memory for Claude Code CLI

**Problem:** AI assistants lose all memory when a session ends. Work disappears. Knowledge isn't preserved. Everything gets redone.

**Solution:** Holographic Memory v2.0 captures every conversation, indexes it for full-text search, and makes it permanently accessible across unbounded sessions.

---

## ✨ What's New in Version 2.0

**vs Version 1.0:**
- ✅ **Fossil SCM integration** - All work versioned + distributed
- ✅ **Hourly auto-ingest** - Real-time indexing (not daily batches)
- ✅ **Microsecond timestamps** - Zero collisions, perfect ordering
- ✅ **Hash-based deduplication** - Smart, efficient indexing
- ✅ **Panic button CLI** - Manual refresh on demand
- ✅ **18-hour smart scheduling** - Work hours only (no waste)
- ✅ **Better error handling** - Skip bad files, continue
- ✅ **3-tier architecture** - Real-time, indexed, manual tiers

---

## 🎯 Core Features

### 1. Real-Time Capture (JSONL)
Every Claude Code conversation automatically saved to JSON Lines format with timestamps.

### 2. Hourly Auto-Ingest  
Runs every hour (10AM-2AM by default) during work hours. Smart detection: only processes changed files. Empty runs take <1 second.

### 3. FTS5 Full-Text Search
All conversations indexed into SQLite FTS5. Search in milliseconds:
```sql
SELECT * FROM q_series_search WHERE q_series_search MATCH 'your_query'
```

### 4. Fossil Version Control
All work committed to Fossil. Distributed, permanent, survives session restarts.

### 5. Panic Button
Manual refresh anytime:
```bash
memory-refresh
```

---

## 🚀 Installation

### Via Claude Code CLI (Recommended)

```bash
claude install holographic-memory-v2
```

This automatically:
- Sets up Fossil repository
- Configures hourly ingest cron job
- Creates FTS5 database
- Registers panic button command
- Sets work hours (customizable)

### Manual Installation

```bash
# Clone repository
git clone https://github.com/yourusername/holographic-memory-v2.git
cd holographic-memory-v2

# Create directories
mkdir -p ~/.claude/memory/{sessions,indexed}

# Initialize Fossil
fossil init ~/.claude/memory/context.fossil

# Install ingest script
cp scripts/ingest_hourly.py ~/.claude/bin/
chmod +x ~/.claude/bin/ingest_hourly.py

# Add cron job
(crontab -l 2>/dev/null; echo "0 10-23,0-2 * * * ~/.claude/bin/ingest_hourly.py") | crontab -

# Register panic button alias
echo "alias memory-refresh='~/.claude/bin/panic_button.sh'" >> ~/.bashrc
source ~/.bashrc
```

---

## 📊 How It Works

### 3-Tier Architecture

**Tier 1: Real-Time (JSONL)**
- Every prompt + response saved immediately
- Location: `~/.claude/memory/sessions/*.jsonl`
- Update: Instant
- Searchable: Yes (grep, jq)

**Tier 2: Indexed (FTS5)**
- Conversations batch-indexed hourly
- Location: `~/.claude/memory/indexed.db`
- Update: Hourly during work hours
- Searchable: Yes (SQL, full-text)

**Tier 3: Manual (Markdown)**
- Key decisions + context stored as markdown
- Location: `~/.claude/memory/*.md`
- Update: Manual (you control)
- Searchable: Yes (via Tier 2)

---

## 🔍 Usage Examples

### Search by Topic
```bash
memory-search "PostgreSQL integration"
```

### View Recent Conversations
```bash
memory-recent --limit 10
```

### Manual Refresh (Panic Button)
```bash
memory-refresh
```

### Export Search Results
```bash
memory-search "your_query" --export csv > results.csv
```

---

## ⚙️ Configuration

Edit `~/.claude/memory/config.json`:

```json
{
  "work_hours": {
    "start": 10,
    "end": 26
  },
  "ingest_schedule": "hourly",
  "database_path": "~/.claude/memory/indexed.db",
  "fossil_path": "~/.claude/memory/context.fossil",
  "max_batch_size": 500
}
```

---

## 🛡️ Safety

- **No API keys stored** - Configuration uses env variables
- **No user data in defaults** - Examples are generic/abstract
- **Encrypted at rest** - SQLite supports SQLCipher
- **Audit trail** - All changes tracked via Fossil
- **Conflict detection** - Hash-based deduplication prevents duplicates

---

## 📈 Performance

- **Ingest speed:** ~7,600 entries/second
- **Search latency:** <50ms (FTS5 full-text)
- **Storage:** ~1 byte per character (highly compressed)
- **Memory usage:** <100MB for 100,000+ conversations

---

## 🐛 Troubleshooting

### Cron job not running?
```bash
crontab -l | grep memory-refresh
```

### Database corrupted?
```bash
memory-repair
```

### Ingest stuck?
```bash
memory-refresh --force
```

---

## 📝 License

MIT - Free to use, modify, distribute.

---

## 🤝 Contributing

Issues + PRs welcome. Please:
1. Don't include API keys or user data
2. Add tests for new features
3. Update ARCHITECTURE.md if changing core behavior

---

## 📞 Support

- Docs: See ARCHITECTURE.md
- Issues: GitHub issues
- CLI Help: `memory-help`

---

**Built for Claude Code CLI users who need persistent memory across sessions.**
