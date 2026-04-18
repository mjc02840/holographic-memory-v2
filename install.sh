#!/bin/bash
# Holographic Memory v2.0 - Installation Script

set -e

echo "=================================================================================="
echo "📦 Holographic Memory v2.0 - Installation"
echo "=================================================================================="
echo ""

# Configuration
MEMORY_PATH="${MEMORY_PATH:-$HOME/.claude/memory}"
BIN_PATH="$MEMORY_PATH/bin"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installation path: $MEMORY_PATH"
echo "Repository dir:    $REPO_DIR"
echo ""

# Step 1: Create directories
echo "📁 Creating directories..."
mkdir -p "$MEMORY_PATH"/{sessions,memory_files,logs,bin}

# Step 2: Copy scripts
echo "📋 Installing scripts..."
cp "$REPO_DIR/scripts/ingest_hourly.py" "$BIN_PATH/"
cp "$REPO_DIR/bin/memory-refresh.sh" "$BIN_PATH/"
chmod +x "$BIN_PATH/ingest_hourly.py"
chmod +x "$BIN_PATH/memory-refresh.sh"

# Step 3: Create alias
echo "⌨️  Creating shell alias..."
if ! grep -q "alias memory-refresh" ~/.bashrc 2>/dev/null; then
    echo "alias memory-refresh='$BIN_PATH/memory-refresh.sh'" >> ~/.bashrc
    echo "  Added to ~/.bashrc"
fi

if [ -f ~/.zshrc ]; then
    if ! grep -q "alias memory-refresh" ~/.zshrc 2>/dev/null; then
        echo "alias memory-refresh='$BIN_PATH/memory-refresh.sh'" >> ~/.zshrc
        echo "  Added to ~/.zshrc"
    fi
fi

# Step 4: Install cron job
echo "⏰ Installing cron job (10AM-2AM)..."
(crontab -l 2>/dev/null | grep -v "ingest_hourly"; echo "0 10-23,0-2 * * * $BIN_PATH/ingest_hourly.py >> $MEMORY_PATH/logs/cron.log 2>&1") | crontab -
echo "  Cron job installed"

# Step 5: Initialize database
echo "💾 Initializing database..."
python3 << EOF
import sqlite3
from pathlib import Path

db_path = Path("$MEMORY_PATH/indexed.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Create FTS5 table
cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS q_series_search USING fts5(
        source,
        content,
        indexed_date
    )
""")

# Create ingest_log table
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
print("  Database initialized at $MEMORY_PATH/indexed.db")
EOF

# Step 6: Environment setup
echo "🔧 Setting up environment..."
cat > "$MEMORY_PATH/.env" << EOF
# Holographic Memory v2.0 Environment

export MEMORY_PATH="$MEMORY_PATH"
export MEMORY_DB="$MEMORY_PATH/indexed.db"
export MEMORY_FOSSIL="$MEMORY_PATH/context.fossil"
export MEMORY_WORK_START=10    # 10 AM
export MEMORY_WORK_END=26      # 2 AM (26:00 = next day 2 AM)

# Add to PATH
export PATH="$BIN_PATH:\$PATH"
EOF
echo "  Created .env file at $MEMORY_PATH/.env"

# Step 7: Initialize Fossil
if [ ! -f "$MEMORY_PATH/context.fossil" ]; then
    echo "🔗 Initializing Fossil repository..."
    cd "$MEMORY_PATH"
    fossil init context.fossil
    fossil open context.fossil
    fossil add -r .
    fossil commit -m "Initial Holographic Memory v2.0 setup"
    echo "  Fossil repository initialized"
fi

# Step 8: Final checks
echo ""
echo "=================================================================================="
echo "✅ Installation Complete!"
echo "=================================================================================="
echo ""
echo "📌 Next Steps:"
echo ""
echo "1. Source the environment file:"
echo "   source $MEMORY_PATH/.env"
echo ""
echo "2. Test the installation:"
echo "   memory-refresh"
echo ""
echo "3. Verify database:"
echo "   sqlite3 $MEMORY_PATH/indexed.db \"SELECT COUNT(*) FROM q_series_search;\""
echo ""
echo "4. Check cron job:"
echo "   crontab -l | grep ingest_hourly"
echo ""
echo "5. Read the docs:"
echo "   cat $REPO_DIR/README.md"
echo "   cat $REPO_DIR/ARCHITECTURE.md"
echo ""
echo "📚 Documentation:"
echo "  - README.md         - Overview + quick start"
echo "  - ARCHITECTURE.md   - Complete design + v1 vs v2"
echo "  - CHANGELOG.md      - What's new in v2.0"
echo ""
echo "🆘 Help:"
echo "  - Run: memory-refresh --help"
echo "  - Logs: tail -f $MEMORY_PATH/logs/*.log"
echo ""
