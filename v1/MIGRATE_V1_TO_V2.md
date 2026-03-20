# Migrating from nanogrind v1 to nanogrindv2

This guide covers the upgrade from the prompt-only v1 architecture to the MCP server architecture (v2).

---

## What changed

| | v1 | v2 |
|---|---|---|
| Queue logic | LLM reads raw progress.json and calculates order | Server calculates — LLM just calls `get_next_items` |
| Write safety | LLM writes full JSON (can corrupt) | `add_completed()` touches only the fields it needs |
| Postponed priority | Prompt instruction (ignored sometimes) | Enforced in server code, always first |
| AGENTS.md size | ~1000 lines (sequence lists, scanning guards) | ~300 lines (session flows only) |
| Tool iterations | 40+ | 15 (fails fast, no infinite loops) |
| Scanning bugs | Ongoing | Eliminated |
| message() loop risk | Ongoing | Mitigated by EXACTLY N tool call pattern |
| Data integrity | LLM could overwrite unrelated fields | Atomic writes per field |

---

## Step 1 — Copy repo to VM

```powershell
scp -r C:\path\to\nanogrindv2 user@<VM_IP>:~/nanogrindv2
```

---

## Step 2 — Install dependencies

```bash
ssh user@<VM_IP>
cd ~/nanogrindv2
python3 -m venv .venv
.venv/bin/pip install -e .
```

Verify:
```bash
.venv/bin/python -c "from servers.progress_server import mcp; print('ok')"
```

---

## Step 3 — Migrate progress.json

Your existing `progress.json` will work — v2 just needs a few extra fields. Run the migration scripts:

```bash
cd ~/nanogrindv2
.venv/bin/python add_new_fields.py       # adds completed_core_ids, completed_ds_ids, postponed fields
.venv/bin/python add_weekly_fields.py    # adds week_start, week_completions, quiz counters, lang quiz fields
```

---

## Step 4 — Generate new content files

v2 adds GoF individual files, language quiz questions, and SQL conceptual questions.

Run locally (or on VM):

```bash
python3 split_design_patterns.py   # splits design_patterns.json → data_generated/gof/
python3 generate_language_quiz.py  # → data_generated/language_quiz/
python3 generate_sql_concepts.py   # → data_generated/sql/ (sql_051–065)
```

Copy to VM data directory:

```bash
DATA=~/.nanobot/workspace/interview-prep/data
scp -r data_generated/gof           user@<VM_IP>:$DATA/
scp -r data_generated/language_quiz user@<VM_IP>:$DATA/
scp -r data_generated/sql           user@<VM_IP>:$DATA/
```

---

## Step 5 — Update nanobot config

Add the `mcpServers` block to `~/.nanobot/config.json` under `tools`. Use the full venv python path — nanobot spawns servers without activating the venv:

```json
"tools": {
  "mcpServers": {
    "interview-prep-progress": {
      "command": "/home/<user>/nanogrindv2/.venv/bin/python",
      "args": ["-m", "servers.progress_server"],
      "cwd": "/home/<user>/nanogrindv2",
      "env": {
        "INTERVIEW_PREP_DATA": "/home/<user>/.nanobot/workspace/interview-prep/data"
      },
      "enabledTools": [
        "get_progress", "get_greeting_card", "get_progress_report", "get_evening_drill",
        "get_next_items", "start_track", "set_in_progress", "get_in_progress",
        "add_completed", "add_postponed", "remove_postponed", "log_attempt",
        "get_due_reviews", "clear_review", "get_weak_areas", "get_last_completed",
        "get_quiz_problem", "get_lang_quiz_problem", "reset_last_lang_quiz",
        "get_category_summary", "save_note", "get_notes", "start_timer"
      ]
    },
    "interview-prep-content": {
      "command": "/home/<user>/nanogrindv2/.venv/bin/python",
      "args": ["-m", "servers.content_server"],
      "cwd": "/home/<user>/nanogrindv2",
      "env": {
        "INTERVIEW_PREP_DATA": "/home/<user>/.nanobot/workspace/interview-prep/data"
      },
      "enabledTools": [
        "get_problem", "get_sql_problem", "get_pattern", "get_aiml_topic",
        "get_behavioral_questions", "get_system_design", "get_core_problem",
        "get_data_structure", "get_item_titles"
      ]
    }
  }
}
```

Also set:
```json
"agents": {
  "defaults": {
    "maxToolIterations": 15
  }
}
```

---

## Step 6 — Deploy new AGENTS.md

The v1 AGENTS.md is ~1000 lines and contains inline sequence lists that the LLM scans to find the next item. Replace it entirely:

```bash
# Backup first
cp ~/.nanobot/workspace/AGENTS.md ~/.nanobot/workspace/AGENTS.md.v1.bak

# Deploy v2 version
scp AGENTS_MCP.md user@<VM_IP>:~/.nanobot/workspace/AGENTS.md
scp cron_jobs.json user@<VM_IP>:~/.nanobot/cron/jobs.json
```

---

## Step 7 — Clear sessions and restart

Session files contain the old conversation context including v1 tool references. Clear them:

```bash
rm -f ~/.nanobot/workspace/sessions/telegram_*.jsonl
rm -f ~/.nanobot/workspace/sessions/cron_*.jsonl
systemctl --user restart nanobot-gateway
journalctl --user -u nanobot-gateway -f
```

Send "hello" to Telegram. You should see `Tool call: start_track` in the logs — not `read_file`.

---

## Rollback

If something breaks, restore from backup:

```bash
cp ~/.nanobot/workspace/AGENTS.md.v1.bak ~/.nanobot/workspace/AGENTS.md
# Remove mcpServers block from config.json
nano ~/.nanobot/config.json
systemctl --user restart nanobot-gateway
```
