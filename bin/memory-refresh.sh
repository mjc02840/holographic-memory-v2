#!/bin/bash
# Holographic Memory v2.0 - Panic Button
# Manual ingest trigger (doesn't wait for hourly cron)

set -e

MEMORY_PATH="${MEMORY_PATH:-$HOME/.claude/memory}"
INGEST_SCRIPT="$MEMORY_PATH/../bin/ingest_hourly.py"

echo "🚨 PANIC BUTTON: Manual Memory Refresh"
echo "========================================"
echo ""
echo "Starting ingest at: $(date)"
echo ""

# Check if ingest script exists
if [ ! -f "$INGEST_SCRIPT" ]; then
    echo "ERROR: Ingest script not found at $INGEST_SCRIPT"
    exit 1
fi

# Run ingest
python3 "$INGEST_SCRIPT"

echo ""
echo "✅ Ingest complete!"
echo ""
echo "Current status:"
if [ -f "$MEMORY_PATH/.last_ingest" ]; then
    echo "  Last ingest: $(cat $MEMORY_PATH/.last_ingest)"
fi

echo ""
echo "Search example:"
echo "  sqlite3 $MEMORY_PATH/indexed.db \"SELECT COUNT(*) FROM q_series_search WHERE q_series_search MATCH 'your_query';\""
