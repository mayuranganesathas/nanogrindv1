# Deployment Guide

Fresh setup from scratch. Assumes nanobot is already installed on your VM.

---

## Prerequisites

- A Linux VM (or any Linux host) running [nanobot](https://github.com/HKUDS/nanobot)
- Python 3.11+ on the VM
- An LLM accessible via OpenAI-compatible API (local or cloud — see model guide in README)
- A Telegram bot token + your Telegram user ID (for `allowFrom`)

---

## Step 1 — Clone and install

On the VM:

```bash
git clone https://github.com/youruser/nanogrindv2 ~/nanogrindv2
cd ~/nanogrindv2
python3 -m venv .venv
.venv/bin/pip install -e .
```

Verify:

```bash
.venv/bin/python -c "from servers.progress_server import mcp; print('ok')"
```

---

## Step 2 — Generate content files

Run locally (or on VM) to generate the data files:

```bash
python3 generate_language_quiz.py   # → data_generated/language_quiz/
python3 generate_sql_concepts.py    # → data_generated/sql/
python3 split_design_patterns.py    # → data_generated/gof/
```

Copy generated data to the VM's data directory:

```bash
DATA=~/.nanobot/workspace/interview-prep/data
scp -r data_generated/gof           user@<VM_IP>:$DATA/
scp -r data_generated/language_quiz user@<VM_IP>:$DATA/
scp -r data_generated/sql           user@<VM_IP>:$DATA/
```

---

## Step 3 — Initialize progress.json

On the VM, create a fresh `progress.json` if it doesn't exist:

```bash
cat > ~/.nanobot/workspace/interview-prep/data/progress.json << 'EOF'
{
  "schema_version": "1.0",
  "start_date": null,
  "streak_days": 0,
  "last_active_date": null,
  "in_progress": null,
  "stats": {},
  "completed_problem_ids": [],
  "completed_sql_ids": [],
  "completed_pattern_ids": [],
  "completed_concept_ids": [],
  "completed_design_ids": [],
  "completed_behavioral_ids": [],
  "completed_core_ids": [],
  "completed_ds_ids": [],
  "completed_lang_quiz_ids": [],
  "postponed_problem_ids": [],
  "postponed_sql_ids": [],
  "postponed_pattern_ids": [],
  "postponed_concept_ids": [],
  "postponed_design_ids": [],
  "postponed_behavioral_ids": [],
  "postponed_core_ids": [],
  "postponed_ds_ids": [],
  "week_start": null,
  "week_completions": {"algo": 0, "sql": 0, "gof": 0, "aiml": 0},
  "last_lang_quiz_id": null,
  "quiz_today_count": 0,
  "quiz_today_date": null
}
EOF
```

If upgrading from a previous version, run the migration scripts instead:

```bash
cd ~/nanogrindv2
.venv/bin/python add_weekly_fields.py
```

---

## Step 4 — Configure nanobot

Edit `config.json` with your values:

1. **Model/provider** — set `agents.defaults.model`, `provider`, and `contextWindowTokens` to match your LLM
2. **API base** — set `providers.custom.apiBase` to your llama-server or provider URL
3. **Telegram token** — set `channels.telegram.token` and `channels.telegram.allowFrom`
4. **MCP server paths** — update the `command` and `cwd` paths in `tools.mcpServers` to your actual install location

Then deploy:

```bash
scp config.json user@<VM_IP>:~/.nanobot/config.json
```

---

## Step 5 — Deploy agent instructions

```bash
scp AGENTS_MCP.md user@<VM_IP>:~/.nanobot/workspace/AGENTS.md
scp cron_jobs.json user@<VM_IP>:~/.nanobot/cron/jobs.json
```

---

## Step 6 — Set up timed mock pings (optional)

`timer_check.py` sends a Telegram message when a timed mock session expires. It runs as a system cron (not nanobot) so it fires even outside of LLM sessions.

Edit `timer_check.py` and set your `BOT_TOKEN` and `CHAT_ID`, then add to crontab on the VM:

```bash
scp timer_check.py user@<VM_IP>:~/nanogrindv2/timer_check.py
ssh user@<VM_IP> "crontab -l | { cat; echo '* * * * * /home/<user>/nanogrindv2/.venv/bin/python /home/<user>/nanogrindv2/timer_check.py'; } | crontab -"
```

---

## Step 7 — Start

```bash
ssh user@<VM_IP>
systemctl --user restart nanobot-gateway
journalctl --user -u nanobot-gateway -f
```

Send "hello" to Telegram. You should see `Tool call: start_track` in the logs.

---

## Redeploying after changes

```bash
# Server code
scp servers/progress_server.py user@<VM_IP>:~/nanogrindv2/servers/
scp servers/content_server.py  user@<VM_IP>:~/nanogrindv2/servers/

# Agent instructions
scp AGENTS_MCP.md user@<VM_IP>:~/.nanobot/workspace/AGENTS.md

# Clear sessions + restart (required after AGENTS.md changes)
ssh user@<VM_IP> "rm -f ~/.nanobot/workspace/sessions/telegram_*.jsonl ~/.nanobot/workspace/sessions/cron_*.jsonl && systemctl --user restart nanobot-gateway"
```

---

## Running Tests

```bash
cd ~/nanogrindv2
.venv/bin/python -m pytest tests/test_progress.py -v
```

---

## Switching Models

Keep separate config files per model and swap them without an SSH session:

```bash
# Switch to Qwen
scp config.qwen.json user@<VM_IP>:~/.nanobot/config.json
ssh user@<VM_IP> "systemctl --user restart nanobot-gateway"

# Switch to Mistral fallback
scp config.mistral.json user@<VM_IP>:~/.nanobot/config.json
ssh user@<VM_IP> "systemctl --user restart nanobot-gateway"
```
