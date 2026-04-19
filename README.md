# Holographic Memory: Version 3.0
## Automatic Context Retrieval for Claude Code CLI

**Problem:** AI assistants lose context across sessions. Even when conversations are saved to a database, you still have to manually ask the AI to search it. Context loss continues.

**V2 Solution:** Capture and index everything. (But still requires manual search requests.)

**V3 Solution:** Automatic context retrieval. Give Claude standing instructions to search your memory when needed—without asking.

---

## 🚀 What's New in Version 3.0

### Major Improvements vs V2

| Feature | V2 | V3 | Benefit |
|---------|----|----|---------|
| **Search trigger** | Manual request | Automatic | Claude searches without being asked |
| **User interaction** | "Search for X" | None | Seamless, zero friction |
| **Update frequency** | Hourly | Every 30 min | Catches sprint work before context loss |
| **Dependencies** | None (pure) | None (pure) | Same simplicity, better results |
| **Session length** | Startup-dependent | Works 24+ hours | Long sessions stay productive |
| **Architecture** | Data capture | Auto-retrieval | Intelligent memory, not just storage |

### How V3 Works Differently

**V2 (Manual):**
```
User: "What did we decide about X?"
Claude: "I don't remember, let me search"
User: "Please search FTS5 for X"
Claude: [searches] "Found it..."
```

**V3 (Automatic):**
```
User: "What did we decide about X?"
Claude: [Automatically searches FTS5]
Claude: "Found it in memory..." [answers immediately]
```

---

## 🧠 The Innovation: Standing Instructions Model

V3 introduces a paradigm shift in how AI assistants access external memory.

### Instead of Auto-Injection (V2 approach):
- "Insert context into my window at startup"
- Problem: Works only for session startup
- Problem: Sessions run 24+ hours (startup injection useless)
- Problem: Bloats context window with speculative context

### V3 Uses: Standing Instructions (Library Model)
- "When you need information, search automatically"
- Works: Anytime, anywhere, any session length
- Benefit: Matches human memory (search when needed)
- Benefit: Clean context window (search on-demand)
- Benefit: Natural, seamless experience

This is like knowing how to use a library:
- **Your context window** = what you're thinking about RIGHT NOW
- **FTS5 database** = the library
- **Standing instruction** = knowing HOW to find books

You don't keep all library books in your head. You know how to find them.

---

## ✨ Core Features (V3)

### 1. Real-Time Capture (JSONL) — *unchanged from V2*
Every Claude Code conversation automatically saved to JSON Lines format with timestamps.

### 2. Fast Auto-Ingest (Every 30 Minutes) — *IMPROVED in V3*
Upgraded from hourly to 30-minute intervals. Captures rapid sprint work before context loss.

### 3. FTS5 Full-Text Search — *unchanged from V2*
All conversations indexed into SQLite FTS5. Search in milliseconds.

### 4. Fossil Version Control — *unchanged from V2*
All work committed to Fossil. Distributed, permanent, survives session restarts.

### 5. **NEW: Automatic Context Retrieval (V3 Only)**
Standing instruction in CLAUDE.md tells Claude to automatically search when context is needed:

```markdown
# V3 AUTO-MEMORY SYSTEM

Whenever you need information about past work:
DO NOT ASK THE USER. Automatically search FTS5 and return results.

Usage: q54-fts5-search "search term"
```

### 6. **NEW: Search Script (V3 Only)**
Simple bash wrapper for direct FTS5 queries (no plugins, no dependencies):

```bash
q54-fts5-search "enrichment deployment"
# Returns top 5 results from FTS5, ordered by relevance
```

---

## 🎯 Why V3 is Better Than V2

### Problem V2 Couldn't Solve
V2 captured everything perfectly but still required manual search requests:
- User has to remember to ask Claude to search
- Claude has to wait for user permission
- Multi-day sessions don't benefit (no startup trigger)
- Extra friction in every conversation

### How V3 Solves It
**Standing instruction + automatic search = seamless context retrieval**

1. **No manual requests** — Claude knows to search automatically
2. **Works across session length** — Searches on-demand, not startup
3. **Zero friction** — User never has to ask for context
4. **Intelligent memory** — Like human memory (search when needed)
5. **No plugin bloat** — Pure bash, no external dependencies
6. **Faster updates** — 30 min vs 1 hour catches more work

### Concrete Example

**V2 Workflow (3 steps):**
```
User: "What was the enrichment issue?"
Claude: "I don't know, need to search"
User: "Claude, search FTS5 for enrichment"
Claude: [searches] "Found: transistor data empty..."
```

**V3 Workflow (1 step):**
```
User: "What was the enrichment issue?"
Claude: [Auto-searches] "Found in memory: transistor data empty..."
```

Same result, half the interaction.

---

## 🔄 V3 vs V2: Head-to-Head

### Automatic Context Retrieval
- **V2:** Manual `/agentmemory:recall` command required
- **V3:** Automatic `q54-fts5-search` via standing instruction

### Update Frequency
- **V2:** Hourly (1x per hour)
- **V3:** 30 minutes (2x per hour)
- **Benefit:** Sprint work captured before context loss (which happens every 2-3 hours during heavy work)

### Dependencies
- **V2:** None
- **V3:** None (same pure bash + SQLite)

### Search Model
- **V2:** Library analogy, but manual ("Ask librarian")
- **V3:** Library analogy, automatic ("Know how to find books")

### Session Handling
- **V2:** Startup-based injection (fails for 24+ hour sessions)
- **V3:** On-demand search (works any session length)

### Context Window Bloat
- **V2:** Risk of injection adding unnecessary context
- **V3:** Clean searches, minimal overhead

---

## 🚀 Installation

### From V2 to V3 (Upgrade)

If you have V2 running:

```bash
# 1. Update CLAUDE.md with V3 standing instruction
# (Copy the section from this README)

# 2. Create search script
cp bin/q54-fts5-search /home/aaa/bin/
chmod +x /home/aaa/bin/q54-fts5-search

# 3. Update cron from hourly to 30-minute
crontab -e
# Change: 0 10-23 * * * → */30 * * * *

# 4. Done. V3 is live.
```

### Fresh V3 Installation

```bash
git clone https://github.com/mjc02840/holographic-memory-v2.git
cd holographic-memory-v2

# Copy search script
cp bin/q54-fts5-search ~/.local/bin/
chmod +x ~/.local/bin/q54-fts5-search

# Add to CLAUDE.md (your personal settings file):
# [Copy the V3 AUTO-MEMORY SYSTEM section from this README]

# Add to crontab:
(crontab -l 2>/dev/null; echo "*/30 * * * * /path/to/ingest_hourly.py") | crontab -

# Test it
q54-fts5-search "test"
```

---

## 📊 How V3 Works

### Architecture (Improved)

```
JSONL Session Files (raw conversations)
    ↓ (every 30 minutes)
FTS5 SQLite Database (indexed, searchable)
    ↓ (on-demand, automatic)
q54-fts5-search Script (returns top 5 results)
    ↓ (standing instruction triggers this)
Claude Context Window (Claude uses results to answer)
```

### The Standing Instruction (Core of V3)

Added to CLAUDE.md:

```markdown
# V3 AUTO-MEMORY SYSTEM

Whenever you need information about past work:
- User asks about past decisions
- You need database status
- You're unsure about project history
- Any time you think "should check memory"

DO NOT ASK THE USER. Automatically run:
  q54-fts5-search "search term"

Include results in your response. This is your knowledge base.
```

This single instruction unlocks automatic context retrieval.

---

## 🎓 Why This Matters

### The Problem It Solves

Claude CLI users hit this issue regularly:
- **Hour 1-3:** Context full, working well
- **Hour 3-4:** Context compacts, older work lost
- **User reality:** "Wait, what did we decide about X last session?"
- **Current workaround:** Search manually or ask for recap

### V3's Solution

By giving Claude standing instructions to search automatically:
- Work stays in memory (FTS5 database)
- Claude knows how to access it (search script)
- User never has to ask (automatic)
- Works across session length (on-demand, not startup)

It's the difference between:
- **Passive memory** (storing data, hoping user asks)
- **Active memory** (data stored, AI retrieves when needed)

---

## 🛠️ Technical Details

### Search Script (q54-fts5-search)
```bash
#!/bin/bash
# Direct SQLite FTS5 query
sqlite3 /path/to/fts5.db \
  "SELECT content, timestamp FROM conversations_fts 
   WHERE conversations_fts MATCH '$1' 
   ORDER BY rank, timestamp DESC 
   LIMIT 5;"
```

**Why bash, not plugin?**
- No dependencies
- Works everywhere
- User has full control
- No vendor lock-in
- Portable to other tools (ChatGPT, local LLMs, etc.)

### Update Frequency (30 Minutes)
```bash
# Cron schedule
*/30 * * * * /home/aaa/bin/ingest_hourly.py

# Reasoning:
# - Context loss happens every 2-3 hours during sprints
# - 30-min updates = 2 captures before context loss
# - Still efficient (minimal I/O overhead)
```

---

## 📈 Performance (V3 Unchanged from V2)

- **Ingest speed:** ~7,600 entries/second
- **Search latency:** <50ms (FTS5 full-text)
- **Storage:** ~1 byte per character (highly compressed)
- **Memory usage:** <100MB for 100,000+ conversations
- **Cron overhead:** Negligible (only processes changed files)

---

## 🤝 Compared to Alternatives

### vs agentmemory Plugin
- **Plugin:** Requires iii-engine (complex dependency)
- **V3:** Pure bash + SQLite (zero dependencies)
- **Plugin:** Auto-injects context (bloats window)
- **V3:** Searches on-demand (clean window)
- **Plugin:** Vendor-controlled
- **V3:** Your code, your control

### vs Manual FTS5 Searches (V2)
- **V2:** User must ask Claude to search
- **V3:** Claude searches automatically
- **V2:** Works only at session start
- **V3:** Works anytime (on-demand)

### vs Hand-Written Memory Files
- **Manual:** You write summaries (time-consuming)
- **V3:** Automatic capture + search (zero effort)

---

## 📝 License

MIT - Free to use, modify, distribute commercially or personally.

---

## 🚀 Use Cases

**Claude Code CLI:**
- Long coding sessions (24+ hours without restart)
- Sprint work (rapid context changes every 30 min)
- Complex projects (need to remember decisions from weeks ago)

**Adaptable to:**
- ChatGPT conversations (via API)
- Local LLMs (Llama, Mixtral, etc.)
- Anthropic API projects
- Any tool with a conversation log

---

## 📞 Getting Started

1. **Read:** ARCHITECTURE.md (how it works)
2. **Install:** Follow installation instructions above
3. **Configure:** Add standing instruction to your CLAUDE.md
4. **Test:** Ask about past work, Claude searches automatically
5. **Use:** Just work normally. Memory is automatic.

---

**V3: Memory that works like human memory. Automatic, intelligent, private.**

Built by and for Claude Code users who want persistent context across unbounded sessions.

MIT License - 2026
