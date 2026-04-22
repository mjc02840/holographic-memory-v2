# Holographic Memory v3.1: Activity Log System
## For Claude Code CLI Users

**Problem:** You lose 30-50% of your development time to context persistence issues.

**Solution:** Automatic real-time activity logging that survives context resets.

---

## 🚨 The Problem This Solves

### The Blind Spot
Your Claude Code CLI context window lasts ~30 minutes. When it resets, you've lost everything you've done on the VPS:

- File modifications on VPS 80? **Not captured**
- Database changes? **Not documented**
- Commands executed? **No audit trail**
- Work from last 30 minutes? **Gone**

### The Time Cost
- Rediscovering work location: 5 minutes
- Re-understanding changes: 10 minutes
- Re-explaining architecture to Claude: 10 minutes
- Re-establishing context: 10 minutes
- **Total per context reset: 35 minutes lost**

With context resets every 30 minutes during heavy coding:
- **35 min lost × 8 resets/day = 280 min = 4.7 hours lost per day**
- **50% of your working time disappeared to memory recovery**

---

## 👤 Who Built This (And Why)

A Claude Code CLI user suffered this problem **for 10 months**. They:

1. Waited for the Claude Code team to implement automatic memory persistence
2. Saw the problem not get fixed
3. Created their own solution
4. **Now offering it free as open source with MIT license**

**Purpose:** Help other Claude Code CLI users avoid the productivity loss this creator experienced.

---

## ✅ What v3.1 Does

### Real-Time Capture
- **File changes:** Automatically captures every file modification on VPS
- **Commands:** Logs all executed commands with results
- **Database ops:** Tracks all database changes
- **Sessions:** Records SSH session activity

### Automatic Indexing
- Captures happen instantly (inotify, <1ms latency)
- Syncs to your memory every 30 minutes (or immediately on activity)
- Searchable via: `q54-fts5-search "what changed"`

### Works Offline
- No external dependencies
- No cloud services
- Pure local system (VPS + your machine)
- MIT licensed

---

## 🚀 Installation (For Claude Code CLI Users)

**You need nothing except the concept.**

1. Save the `INSTALLATION_PROMPT.md` file from this repository
2. Paste the content into Claude Code CLI
3. Claude Code CLI automatically:
   - SSHes to your VPS 80
   - Creates SQLite activity database
   - Sets up Fossil archive
   - Configures inotify monitoring
   - Syncs to your memory (FTS5)
4. Returns status report when complete

**No files to download. No manual installation. Just paste the prompt.**

---

## 🔍 Using It

### Search for What Changed
```bash
# What files changed 30 minutes ago?
q54-fts5-search "file_changes 2026-04-23 14:3"

# What happened to index_002.html?
q54-fts5-search "index_002.html modified"

# Database changes?
q54-fts5-search "database_changes INSERT"
```

### When Context Resets
Instead of losing 30 minutes:

```
Claude (new context): "What was I working on?"
→ Automatically searches memory
→ "Found your activity log: 23 file changes, 5 database operations, 47 commands"
→ Restores full context instantly
```

---

## 📊 What Gets Captured

| Type | Examples | Searchable |
|------|----------|-----------|
| **File Changes** | create, modify, delete with timestamp and size | Yes |
| **Commands** | Every SSH command, exit code, output lines | Yes |
| **Database Ops** | INSERT, UPDATE, DELETE with row counts | Yes |
| **Sessions** | SSH logins, duration, command count | Yes |
| **All with** | User attribution, exact timestamps | Yes |

---

## 💼 Deployment

### What You Get
- **VPS 80:** SQLite activity.db + Fossil archive
- **t630:** Sync script + FTS5 integration
- **Cron Job:** Every 30 minutes (smart—only syncs if changes exist)
- **Zero overhead:** ~50MB disk, negligible CPU/network

### Fallback Safety
- **Primary:** inotify triggers sync immediately on file changes
- **Secondary:** Cron job every 30 min (catches anything missed)
- **Result:** Nothing ever lost, even if inotify fails

---

## 🛠️ Technical Details

### 3-Tier Architecture
```
VPS 80: SQLite (real-time) → Fossil (archive) → t630: FTS5 (searchable)
```

- **Tier 1:** SQLite captures activity instantly
- **Tier 2:** Fossil creates immutable historical record
- **Tier 3:** FTS5 makes activity searchable in your memory

### Search Latency
- File change on VPS → searchable in memory: **~10 seconds**
- Every 30 minutes: Guaranteed sync even if missed

---

## 📝 Files in This Repository

- `README_V3.1.md` — This file (user story + overview)
- `FEATURE_ACTIVITY_LOG_SYSTEM.md` — Complete technical specification
- `INSTALLATION_PROMPT.md` — Claude Code CLI installation prompt (paste into CLI)
- `LICENSE` — MIT License (free to use, modify, distribute)

---

## 🚀 Quick Start

### For Claude Code CLI Users

1. **Copy the installation prompt:**
   ```bash
   cat INSTALLATION_PROMPT.md
   ```

2. **Paste into Claude Code CLI and run**

3. **Test it works:**
   ```bash
   q54-fts5-search "activity"
   ```

That's it. Your 30-minute context window is now fully captured.

---

## 🔐 Security & Privacy

- All activity logged **locally only** (your VPS + your machine)
- No external services, no cloud uploads
- SSH key-based auth (no passwords)
- MIT License (audit-friendly)
- User attribution in all logs

---

## 📈 Impact

### Before v3.1
- Context loss every 30 minutes
- Manual documentation of VPS work
- Rediscovery time: 35 minutes per reset
- **50% of time lost to memory recovery**

### After v3.1
- Context resets show full activity log
- **Zero manual documentation**
- Rediscovery time: <1 minute (search memory)
- **Reclaim 4-5 hours per development day**

---

## 🙏 Support the Creator

This project was built by someone who suffered 10 months of productivity loss waiting for a fix. They created their own solution and offer it **free as open source**.

**Ways to support:**
- Use it and share your experience
- Report bugs or suggest improvements
- Contribute enhancements via pull requests
- Star the repository if it helps you

---

## 📜 License

MIT License - Free to use, modify, and distribute.

See LICENSE file for full text.

---

## 🤝 Contributing

This project is maintained by the original creator. Contributions welcome:

1. Test the installation prompt
2. Report issues
3. Suggest improvements
4. Share your use cases

---

## ❓ FAQ

**Q: Will this slow down my VPS?**  
A: No. inotify is kernel-level, ~50MB memory, negligible CPU. Sync only when changes exist.

**Q: What if inotify fails?**  
A: Cron job runs every 30 min as fallback. Nothing is ever lost.

**Q: Can I customize what gets captured?**  
A: Yes. SQL tables are documented. Add your own monitoring as needed.

**Q: Does this work with other LLMs?**  
A: No, this is Claude Code CLI specific. Requires Claude's standing instructions feature.

**Q: What about my private data?**  
A: All local. No cloud, no external services. You control everything.

---

## 📞 Contact / Feedback

For issues, questions, or feedback:
- Check the INSTALLATION_PROMPT.md for troubleshooting
- Review FEATURE_ACTIVITY_LOG_SYSTEM.md for technical details
- Report issues on GitHub

---

**Version:** 3.1  
**Status:** Production Ready  
**License:** MIT  
**Tested on:** Debian 12 (VPS 80 + t630)  
**Created:** 2026-04-23  
**For:** Claude Code CLI Users

---

**Stop losing 50% of your development time to context loss.**  
**Use Holographic Memory v3.1 — Activity Log System.**
