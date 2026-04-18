# CHANGELOG

## Version 2.0.0 (2026-04-18)

### Major Features Added

#### Fossil SCM Integration
- All conversations + decisions now versioned in Fossil distributed repository
- Enables rollback, offline access, and permanent audit trails
- Survives session restarts and storage failures
- **Benefit:** No more lost work; complete history preservation

#### Hourly Auto-Ingest (vs Daily)
- Changed from 23:59 batch to hourly schedule (10AM-2AM default, configurable)
- Smart change detection: only processes modified files
- Empty runs take <1 second (no database writes if nothing changed)
- **Benefit:** Work is searchable within 1 hour instead of 18+ hours

#### Microsecond Timestamps
- JSONL files and logs now use microsecond precision (`2026-04-18T14:03:27_246098`)
- Prevents filename collisions in high-volume environments
- Perfect ordering even during rapid fire events
- **Benefit:** No ambiguity; exact temporal ordering guaranteed

#### Hash-Based Deduplication
- Replaced full-file re-indexing with MD5 hash comparison
- Only processes files that have actually changed
- Tracks hashes in `ingest_log` table
- **Benefit:** ~100x faster ingest (0.5s vs 50s for 7,000 entries)

#### Panic Button CLI
- New command: `memory-refresh`
- Manually trigger ingest anytime (doesn't wait for hourly cron)
- Respects same logic as hourly ingest (smart change detection)
- Returns to work instantly
- **Benefit:** High-volume work days (5,000+ lines) can be saved immediately

#### Work Hours Awareness
- Ingest runs ONLY during work hours (10AM-2AM by default)
- Configurable via `MEMORY_WORK_START` and `MEMORY_WORK_END` env vars
- Off-hours requests still return success (just skip actual work)
- **Benefit:** Reduced system load at night; still available if needed

#### Error Resilience
- Single file parse errors no longer crash entire ingest
- Bad JSONL lines are logged + skipped; rest continue
- Corrupted markdown files parsed as plain text (fallback)
- Status tracked in `ingest_log` (success/partial/error)
- **Benefit:** One bad file doesn't break the entire system

#### Database Tracking (ingest_log)
- New SQLite table tracks all ingest operations
- Records: filename, hash, timestamp, entries_added, status
- Enables audit trail + prevents double-indexing
- Allows users to understand system health
- **Benefit:** Transparency + debugging; can answer "was this indexed?"

#### CLI Tools
New commands added:
- `memory-refresh` - Panic button (manual ingest)
- `memory-search "query"` - Full-text search
- `memory-recent --limit N` - Show recent conversations
- `memory-status` - System health check
- `memory-help` - Built-in documentation

**Benefit:** Better UX; discoverable features; easier debugging

### Breaking Changes

- **Directory structure changed:** Sessions now stored in `~/.claude/memory/sessions/` instead of root
- **Config format changed:** Now uses environment variables instead of config.json
- **Cron syntax changed:** Uses new work hours logic (10-23,0-2 instead of 23:59)

### Performance Improvements

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| Ingest frequency | 1x/day | 18x/day | 18x faster catchup |
| File change detection | ~50s | <0.5s | 100x faster |
| Timestamp precision | 1 second | 1 microsecond | 1,000,000x better |
| Empty run time | N/A | <0.1s | Negligible |
| Error handling | Stop | Continue | Robustness ✓ |

### Bug Fixes

- Fixed: Ingest would fail if any file was malformed (now skips + continues)
- Fixed: Daily cron collision at 23:59:59 (hourly distribution)
- Fixed: No deduplication checking (added hash tracking)
- Fixed: No audit trail (added ingest_log table)
- Fixed: No way to manually trigger ingest (added panic button)

### Migration Path

Users upgrading from v1.0:
1. Backup existing data: `cp -r ~/.claude/memory ~/.claude/memory.v1.backup`
2. Install v2.0 scripts
3. Import v1.0 JSONL files
4. Initialize Fossil repository
5. Run full ingest: `memory-refresh --force`

**Estimated time:** 10 minutes

### Documentation

- NEW: ARCHITECTURE.md - Complete system design + v1 vs v2 comparison
- NEW: CLI.md - All commands with examples
- UPDATED: README.md - Installation, usage, safety
- UPDATED: CHANGELOG.md - This file

### Testing

- Tested ingest of 7,693 entries (8 JSONL files + 6 markdown files)
- Tested on-error continuation (malformed JSON handling)
- Tested work hours logic (off-hours skip)
- Tested hash-based dedup (100% accuracy)
- Tested panic button (instant execution)
- Tested cron scheduling (hourly 10AM-2AM)

### Known Limitations

- No encryption at rest (v2.1 feature)
- No multi-machine sync (v2.2 feature)
- No web UI (v2.3 feature)
- No semantic search (v2.4 feature)

### Roadmap

- **v2.1:** SQLCipher integration for at-rest encryption
- **v2.2:** Fossil sync across machines (P2P)
- **v2.3:** Web dashboard for search + browse
- **v2.4:** Vector embeddings for semantic search
- **v3.0:** Native Claude Code CLI integration

---

## Version 1.0.0 (2026-03-15)

### Initial Release

- JSONL real-time conversation capture
- SQLite FTS5 indexing
- Daily batch ingest (23:59 cron)
- Full-text search capability
- Markdown memory files

---

**Last Updated:** 2026-04-18  
**Version:** 2.0.0  
**Maintained By:** M Jcar  
