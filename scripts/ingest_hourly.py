#!/usr/bin/env python3
"""
Holographic Memory v2.0 - Hourly Ingest Script
Parses JSONL + markdown, indexes into FTS5 with deduplication
Work hours: Configurable (default 10AM-2AM)
"""

import sqlite3
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys

# Configuration (use env vars or defaults)
BASE_DIR = Path(os.getenv("MEMORY_PATH", "~/.claude/memory")).expanduser()
JSONL_DIR = BASE_DIR / "sessions"
MARKDOWN_DIR = BASE_DIR / "memory_files"
DB_PATH = Path(os.getenv("MEMORY_DB", BASE_DIR / "indexed.db"))
LOG_DIR = BASE_DIR / "logs"
LAST_INGEST_FILE = BASE_DIR / ".last_ingest"

# Create directories if needed
for d in [BASE_DIR, JSONL_DIR, MARKDOWN_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

WORK_START = int(os.getenv("MEMORY_WORK_START", "10"))
WORK_END = int(os.getenv("MEMORY_WORK_END", "26"))  # 26 = next day 2AM


def get_timestamp_with_microseconds():
    """Return ISO format timestamp with microseconds"""
    return datetime.utcnow().isoformat()


def log_message(msg, status="INFO"):
    """Log with microsecond timestamp to file"""
    ts = get_timestamp_with_microseconds()
    log_filename = f"ingest_{ts.replace(':', '-').replace('.', '_')}.log"
    log_path = LOG_DIR / log_filename

    with open(log_path, 'a') as f:
        f.write(f"{ts} | {status} | {msg}\n")

    print(f"{ts} | {status} | {msg}")


def file_hash(filepath):
    """Compute MD5 hash of file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        log_message(f"Hash error {filepath}: {e}", "ERROR")
        return None


def is_work_hours():
    """Check if current time is within work hours"""
    hour = datetime.utcnow().hour

    if WORK_END <= 24:
        # Same day (e.g., 10-22)
        return WORK_START <= hour <= WORK_END
    else:
        # Spans midnight (e.g., 10-26 = 10am-2am next day)
        return hour >= WORK_START or hour < (WORK_END - 24)


def get_last_ingest_time():
    """Get timestamp of last successful ingest"""
    if LAST_INGEST_FILE.exists():
        return LAST_INGEST_FILE.read_text().strip()
    return None


def set_last_ingest_time():
    """Update last ingest timestamp"""
    LAST_INGEST_FILE.write_text(get_timestamp_with_microseconds())


def init_database():
    """Create FTS5 table + ingest_log if needed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # FTS5 table for searchable conversations
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS q_series_search USING fts5(
            source,
            content,
            indexed_date
        )
    """)

    # Tracking table for deduplication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingest_log (
            id INTEGER PRIMARY KEY,
            source_file TEXT UNIQUE,
            source_type TEXT,
            file_hash TEXT,
            entries_added INTEGER,
            last_file_mtime REAL,
            ingested_at TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_ingest_record(filename):
    """Check if file was already ingested"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT file_hash FROM ingest_log WHERE source_file = ?", (filename,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def parse_jsonl_file(filepath):
    """Parse JSONL file, return list of entries"""
    entries = []
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError as e:
                        log_message(f"JSONL parse error {filepath.name}:{line_num}: {e}", "ERROR")
                        continue
    except Exception as e:
        log_message(f"Failed to read {filepath.name}: {e}", "ERROR")

    return entries


def parse_markdown_file(filepath):
    """Parse markdown file, return as single text entry"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return [{"content": content, "type": "markdown", "source": filepath.name}]
    except Exception as e:
        log_message(f"Failed to read markdown {filepath.name}: {e}", "ERROR")
        return []


def ingest_to_fts5(entries):
    """Batch insert entries to FTS5"""
    if not entries:
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted = 0
    for entry in entries:
        try:
            if isinstance(entry, dict):
                content = entry.get("content") or entry.get("text") or json.dumps(entry)
                source = entry.get("source_file", "unknown")
            else:
                content = str(entry)
                source = "unknown"

            cursor.execute("""
                INSERT INTO q_series_search (source, content, indexed_date)
                VALUES (?, ?, ?)
            """, (source, content, get_timestamp_with_microseconds()))

            inserted += 1
        except Exception as e:
            log_message(f"FTS5 insert error: {e}", "ERROR")
            continue

    conn.commit()
    conn.close()
    return inserted


def update_ingest_log(filename, file_type, fhash, entries_count, status="success"):
    """Record ingest in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR REPLACE INTO ingest_log
            (source_file, source_type, file_hash, entries_added, last_file_mtime, ingested_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (filename, file_type, fhash, entries_count, os.path.getmtime(filename),
              get_timestamp_with_microseconds(), status))
        conn.commit()
    finally:
        conn.close()


def main():
    """Main ingest process"""
    start_time = get_timestamp_with_microseconds()

    # Check work hours (skip if off-hours)
    if not is_work_hours():
        log_message("OFF-HOURS | Skipping ingest (outside work hours)", "SKIP")
        return

    log_message("START | Checking for changes...", "START")

    init_database()

    total_ingested = 0
    files_processed = 0

    # Process JSONL files
    if JSONL_DIR.exists():
        for jsonl_file in sorted(JSONL_DIR.glob("*.jsonl")):
            old_hash = get_ingest_record(jsonl_file.name)
            new_hash = file_hash(jsonl_file)

            if not new_hash:
                continue

            if old_hash == new_hash:
                log_message(f"SKIP | {jsonl_file.name} (hash unchanged)", "SKIP")
                continue

            log_message(f"FOUND | {jsonl_file.name}", "FOUND")
            entries = parse_jsonl_file(jsonl_file)

            if entries:
                ingested = ingest_to_fts5(entries)
                update_ingest_log(jsonl_file.name, "jsonl", new_hash, len(entries))
                log_message(f"INGEST | {jsonl_file.name}: {ingested} entries → FTS5", "INGEST")
                total_ingested += ingested
                files_processed += 1

    # Process markdown files
    if MARKDOWN_DIR.exists():
        for md_file in sorted(MARKDOWN_DIR.glob("*.md")):
            old_hash = get_ingest_record(md_file.name)
            new_hash = file_hash(md_file)

            if not new_hash:
                continue

            if old_hash == new_hash:
                log_message(f"SKIP | {md_file.name} (hash unchanged)", "SKIP")
                continue

            log_message(f"FOUND | {md_file.name}", "FOUND")
            entries = parse_markdown_file(md_file)

            if entries:
                ingested = ingest_to_fts5(entries)
                update_ingest_log(md_file.name, "markdown", new_hash, len(entries))
                log_message(f"INGEST | {md_file.name}: {ingested} entries → FTS5", "INGEST")
                total_ingested += ingested
                files_processed += 1

    # Final status
    set_last_ingest_time()

    if total_ingested > 0:
        log_message(f"COMPLETE | {files_processed} files, {total_ingested} entries indexed", "COMPLETE")
    else:
        log_message(f"COMPLETE | No changes since last ingest", "COMPLETE")


if __name__ == "__main__":
    main()
