# nanogrind — v1 to v2 History & Architecture Notes

Personal reference. Documents what broke in v1, why v2 was built the way it was, and the decisions made along the way.

---

## Why v1 existed

v1 was a pure prompt-engineering bot. The entire system lived in one large `AGENTS.md` file (~1000 lines). The LLM:
- Scanned inline sequence lists (`nc_001, nc_002, nc_003…`) to find the next item
- Read raw `progress.json` and calculated queue order itself
- Wrote full JSON back when marking things complete
- Had guards and warnings baked into the prompt to prevent it from skipping items or looping

It worked well enough to get through the first ~15 NeetCode problems. But as the curriculum grew and more tracks were added, the cracks appeared fast.

---

## What broke in v1

### Queue calculation errors
The LLM would sometimes calculate the wrong next item — skipping problems, repeating completed ones, or picking from the wrong track. The prompt had `⚠️ GUARD` comments and explicit sequence lists to prevent this, but the model ignored them intermittently.

### JSON corruption
When `add_completed` was a prompt instruction rather than a tool call, the LLM would write back the entire `progress.json`. This occasionally corrupted fields it wasn't supposed to touch — wrong timestamps, dropped fields, mangled arrays.

### Postponed items not prioritized
The prompt said "check for postponed items first" but the model didn't always do it. Postponed items would get buried and forgotten.

### message() loops
The model sometimes called `message()` in a loop — sending the same message 3–5 times before stopping. The only mitigation was prompt instructions, which didn't fully work.

### Scanning bugs on long sequences
With 149 algo problems listed inline, the model would occasionally miscalculate its position in the list — especially after skips or postpones. This got worse as the list grew.

### Tool iteration overrun
With `maxToolIterations: 40`, a bad session could run 30+ tool calls before failing. No fast-fail, so bad sessions were expensive in tokens and time.

### SQL flow score-before-write bug
The model would output the score and feedback before calling `add_completed` + `log_attempt` — meaning the UI showed results before the data was written. On a retry, it would write duplicate attempts.

---

## v2 Design Decisions

### All queue logic moves server-side
`get_next_items(track, n)` returns the correct next items — postponed first, then uncompleted in sequence order. The LLM never sees the raw sequence list or progress.json. It can't calculate wrong.

### Atomic writes only
`add_completed(track, id)` touches exactly three fields: the completed list, the stat counter, and the streak. Nothing else. Corruption is structurally impossible.

### `start_track` as the single session entry point
Before v2, starting a session took 4 tool calls: `get_in_progress`, `get_next_items`, `set_in_progress`, then content. `start_track(track)` does all three progress operations in one call. Every session now starts with exactly 2 tool calls: `start_track` + the content tool. This is also the first line of defense against the message() loop — fewer calls means fewer opportunities to go off-script.

### EXACTLY N tool calls pattern
Every session flow in `AGENTS_MCP.md` specifies the exact number of tool calls. `maxToolIterations: 15` fails fast if the model overruns. This made debugging much faster — a bad session fails in 15 calls instead of 40.

### "Evaluate internally → tool calls → output" order
In v1 the SQL flow would evaluate the answer, output the score, then try to write it — meaning the write happened after the user already saw the result. v2 enforces: evaluate silently first, call `add_completed` + `log_attempt`, then output. A `⛔` guard is in every session flow in AGENTS_MCP.md to reinforce this.

### Spaced repetition server-side
`log_attempt` calculates the review delay and writes to `review_queue.json` directly. The LLM passes scores; the server handles all the math. Review scheduling, weak area aggregation, confidence decay — all computed without LLM involvement.

### session_active guard on crons
Pop quiz and lang quiz crons check `in_progress` before firing. If a session is active, they return `{"session_active": true}` and the cron does nothing. Previously, a cron would interrupt a live session by pushing a new message mid-conversation.

### Timer system without LLM
Timed mock pings are sent by `timer_check.py`, a standalone system cron that runs every minute. It reads `timer_queue.json` and sends a Telegram message directly via the Bot API if the timer has expired. The LLM is never involved — it just calls `start_timer(minutes, label)` at session start and `add_completed` at the end (which clears the timer file so no stale pings).

### Notes system
v1 had no way to persist session takeaways. After completing a category, the LLM's notes would disappear when the context window cleared. v2 adds `save_note(track, category, user_note, coach_note)` → `notes.json`, and `get_notes` is called during reviews so past insights resurface.

---

## Model Evolution

### Mistral Small 3.2 24B (Ollama) — original
Worked fine for tool calling. Weak at code evaluation — scores felt imprecise and it would sometimes misevaluate Big O. Session instructions needed to be very explicit.

### Qwen 3.5 27B (Ollama) — attempted upgrade
Better reasoning and code evaluation, but Ollama has multiple bugs with Qwen's tool calling:
- Wrong pipeline (Hermes JSON instead of Qwen's Coder XML format)
- Unclosed `<think>` blocks when tool calls follow thinking output
- Missing generation prompt after tool call turns
- `presence_penalty` silently discarded on the Go runner

These are Ollama bugs, not model bugs. The model works correctly; Ollama's template renderer doesn't.

### Qwen 3.5 27B (llama-server + barubary template) — current
Switched to `llama.cpp` `llama-server` running in Docker with the community-fixed chat template by barubary (21 fixes for tool calling, thinking mode, parallel tool calls). Runs on RTX 3090 (24GB VRAM) with Q4_K_M quantization and KV cache quantization (q8_0) to fit 49K context. Noticeably better code evaluation than Mistral.

---

## DEPLOY.md — original v1→v2 migration steps (preserved)

### Prerequisites
- nanobot running on VM
- nanogrindv2 folder at `C:\Users\U\Documents\nanogrindv2\` on Windows

### Step 1 — Copy files to VM

```powershell
scp -r C:\Users\U\Documents\nanogrindv2 mayu@10.0.0.163:~/nanogrindv2
```

### Step 2 — Install on VM

```bash
ssh mayu@10.0.0.163
cd ~/nanogrindv2
python3 -m venv .venv
.venv/bin/pip install -e .
```

Verify servers can be imported:
```bash
.venv/bin/python -c "from servers.progress_server import get_next_items; print('ok')"
.venv/bin/python -c "from servers.content_server import get_problem; print('ok')"
```

### Step 3 — Update progress.json (add in_progress field)

```bash
python3 - << 'EOF'
import json
path = "/home/mayu/.nanobot/workspace/interview-prep/data/progress.json"
with open(path) as f:
    data = json.load(f)
if "in_progress" not in data:
    data["in_progress"] = None
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("Added in_progress field")
else:
    print("Already has in_progress field")
EOF
```

### Step 4 — Update nanobot config.json

Add the `mcpServers` block inside `"tools"`. The initial enabledTools list was minimal — this grew significantly through v2 development.

### Step 5 — Replace AGENTS.md with the MCP version

The v1 AGENTS.md had ~1000 lines. With MCP, each flow dropped to ~10 lines.

```powershell
scp C:\Users\U\Documents\nanogrind\workspace\AGENTS_MCP.md mayu@10.0.0.163:~/.nanobot/workspace/AGENTS.md
```

### Step 6 — Test MCP servers manually

```bash
cd ~/nanogrindv2
.venv/bin/python - << 'EOF'
import os
os.environ["INTERVIEW_PREP_DATA"] = "/home/mayu/.nanobot/workspace/interview-prep/data"
from servers.progress_server import get_next_items, get_progress
print("Progress:", get_progress())
print("Next algo:", get_next_items("algo", 3))
EOF
```

### Step 7 — Clear sessions and restart

```bash
echo "# History" > ~/.nanobot/workspace/memory/HISTORY.md
rm -f ~/.nanobot/workspace/sessions/telegram_*.jsonl
systemctl --user restart nanobot-gateway
```

### What changes vs v1

| | Before (v1) | After (v2) |
|---|---|---|
| Queue logic | LLM calculates from raw JSON | Server calculates, LLM calls get_next_items |
| Write safety | LLM writes full JSON (can corrupt) | add_completed() touches only 3 fields |
| Postponed priority | Prompt instruction (ignored sometimes) | Enforced in server code |
| AGENTS.md size | ~1000 lines | ~300 lines |
| Scanning bugs | Ongoing | Eliminated |
| message() loop | Ongoing | Mitigated by EXACTLY N pattern |
