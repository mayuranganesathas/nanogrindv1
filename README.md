# nanogrind

> A self-hosted, Telegram-based interview prep coach that runs entirely on your local machine — no cloud, no subscriptions, no data leaving your network.

Built by [@mayuranganesathas](https://github.com/mayuranganesathas) — made with love and mild suffering.

---

## Why I Built This

I'm a senior SWE prepping for top-tier interviews. I wanted something that would:

- **Drill me daily** — algo problems, design patterns, SQL, and AI/ML theory on a structured schedule
- **Not let me cheat** — hints only when I ask, strict scoring, pushback on vague answers
- **Run locally** — I don't want my progress and code attempts going to some SaaS product
- **Work on my phone** — Telegram means I can practice from anywhere, no laptop required

So I wired together [nanobot](https://github.com/HKUDS/nanobot), [ollama](https://ollama.com/), and a custom curriculum. Every morning my Telegram gets a greeting with my streak and exactly what to study that day.

---

## Why Nanobot?

I evaluated a few local agent frameworks and landed on nanobot for a few reasons:

- **Simplicity** — skills are just markdown files. No code to write for routing or tool dispatch.
- **Bootstrap injection** — `USER.md` and `AGENTS.md` are always loaded into the system prompt, so the bot always has context without needing to remember anything between sessions.
- **Telegram gateway built-in** — one command and you have a fully functional Telegram bot backed by your local LLM. No webhook setup, no server.
- **Skill routing** — you define intents in plain English and the LLM routes naturally. No slash commands, no regex.
- **Cron support** — morning reminders and daily summaries are just JSON entries, no daemon to manage.

The tradeoff is that nanobot is a young project — a few rough edges (see [Gotchas](#gotchas)).

---

## Why a VM?

A few practical reasons:

- **Isolation** — ollama running a 24B model consumes serious RAM (18GB+). Keeping it in a VM means your main Windows machine stays responsive.
- **Always-on** — the VM can run headless in the background. The Telegram bot is always available even when your laptop is closed.
- **Clean environment** — nanobot and ollama don't touch your main system. Easy to nuke and rebuild.
- **Hyper-V is free** — already included in Windows 10/11 Pro. No extra software needed.

The VM talks to your Windows machine only via SSH/SCP for file transfers. Everything else stays inside the VM.

---

## Why mistral-small3.2:24b?

Short answer: it's the best balance of tool-call reliability, context efficiency, and VRAM for this use case.

nanogrind reads individual problem/topic files (~700 tokens each) via `read_file` tool calls. Smaller models frequently produce malformed JSON in tool call payloads, causing silent failures — the bot invents content instead of reading the file.

| Model | Tool Calls | VRAM | Notes |
|---|---|---|---|
| mistral-small3.2:24b | Reliable | ~21GB at 48k ctx | **Recommended** |
| qwen2.5:27b | Reliable | ~22GB | Works, higher VRAM |
| qwen2.5:14b | Usually works | ~12GB | Acceptable if RAM-limited |
| 9B and below | Frequent failures | — | Not recommended |

**Context window**: The Modelfile sets `num_ctx 49152` (48k tokens). This covers a full day session including all split content files, session history, USER.md, and AGENTS.md with comfortable headroom. A 3090 (24GB) fits this with ~3GB to spare.

---

## What's Inside

- **149 NeetCode 150 algo problems** — full problem description, constraints, L1/L2/L3 hints, thinking questions, test cases, complexity (split into individual files)
- **50 SQL problems** — full problem description, schema, constraints, hints, optimal solution (split into individual files)
- **NeetCode Core Skills** — 33 implementation problems enforced inline during sessions: sorting algorithms, graph algorithms, data structures, design pattern code, ML coding (1 per session, triggered by category)
- **23 GoF design patterns + 5 SOLID principles** — 7 questions each, conceptual through implementation
- **36 AI/ML topics** — math refresher (10 topics) gates into core ML → deep learning → frontier (LLMs, RAG, diffusion, LoRA) → ML system design (split into individual files)
- **8 ML system design problems**
- **30 behavioral questions**
- **Progress tracking** — all completions written to local JSON, streak tracking, postpone system

Daily schedule (4 hours):

| Block | Time | Weeks |
|---|---|---|
| Algo | 1.5h | 1–8 (1h weeks 9–10) |
| GoF Patterns | 30m | all |
| Math Refresher | 1h | 1–2 (gates into AI/ML) |
| AI/ML | 1h | 3–10 (after math complete) |
| SQL | ~20m | all (2 problems/session) |
| Behavioral | 30m | 3+ |
| System Design | 2h Saturdays | 5+ |

---

## Requirements

**Windows only** (currently — Hyper-V required for the VM approach)

- Windows 10/11 Pro or Enterprise
- 24GB+ RAM (mistral-small3.2:24b needs ~21GB allocated to the VM at 48k context)
- A Telegram account
- ~15GB free disk space for the model

---

## Setup

### 1. Create a Hyper-V VM

1. Open **Hyper-V Manager** → New → Virtual Machine
2. Install Ubuntu 22.04 LTS
3. Recommended: 4 vCPUs, 22GB RAM, 60GB disk
4. Note the VM's IP after boot: run `ip addr show` inside the VM

**Set the VM timezone** (critical — nanobot injects VM local time into every message):

```bash
sudo timedatectl set-timezone America/Los_Angeles  # or your timezone
timedatectl status  # verify
```

### 2. Install Ollama on Windows (Docker)

Run ollama in Docker on your Windows host (not inside the VM):

```bash
docker run -d --gpus all -p 11434:11434 --name ollama ollama/ollama
```

Pull the model:

```bash
docker exec ollama ollama pull mistral-small3.2:24b-instruct-2506-q4_K_M
```

### 3. Create the custom model with the right context window

```bash
# From the nanogrind directory on Windows
make setup
```

Or manually:

```bash
make pull         # pulls base model
make create-model # creates mistral-small3.2:24b-48k from Modelfile
```

### 4. Install nanobot on the VM

```bash
pip install nanobot-ai
nanobot init
```

This creates `~/.nanobot/` with the workspace structure.

### 5. Create a Telegram Bot

1. Open Telegram → search `@BotFather` → `/newbot`
2. Follow the prompts, save your **bot token**
3. Get your **chat ID**: message `@userinfobot`

Configure nanobot — edit `~/.nanobot/config.json`. Key fields:

```json
{
  "agents": [...],
  "channels": {
    "telegram": {
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_CHAT_ID"]
    }
  },
  "providers": {
    "ollama": {
      "model": "mistral-small3.2:24b-48k"
    }
  }
}
```

**Note:** As of nanobot v0.1.4.post4, empty `allowFrom: []` denies all senders. You must set your chat ID explicitly.

### 6. Clone nanogrind and copy files to the VM

On your Windows machine (WSL):

```bash
git clone https://github.com/mayuranganesathas/nanogrind.git
cd nanogrind
```

Edit `workspace/USER.md` — change the name and timezone to yours.

SCP everything to the VM:

```bash
# Replace mayu@10.0.0.163 with your VM user@IP
ssh mayu@10.0.0.163 "mkdir -p ~/.nanobot/workspace/interview-prep/data/algo ~/.nanobot/workspace/interview-prep/data/aiml ~/.nanobot/workspace/interview-prep/data/sql ~/.nanobot/workspace/interview-prep/data/core ~/.nanobot/workspace/skills/interview-prep ~/.nanobot/workspace/memory"

scp workspace/USER.md mayu@10.0.0.163:~/.nanobot/workspace/USER.md
scp workspace/AGENTS.md mayu@10.0.0.163:~/.nanobot/workspace/AGENTS.md
scp workspace/SOUL.md mayu@10.0.0.163:~/.nanobot/workspace/SOUL.md
scp workspace/interview-prep/data/progress.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/progress.json
scp workspace/interview-prep/data/attempts.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/attempts.json
scp workspace/interview-prep/data/design_patterns.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/design_patterns.json
scp workspace/interview-prep/data/behavioral.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/behavioral.json
scp workspace/interview-prep/data/system_design.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/system_design.json
scp workspace/interview-prep/data/data_structures.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/data_structures.json
scp workspace/interview-prep/data/algo/*.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/algo/
scp workspace/interview-prep/data/aiml/*.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/aiml/
scp workspace/interview-prep/data/sql/*.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/sql/
scp workspace/interview-prep/data/core/*.json mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/core/
scp workspace/memory/MEMORY.md mayu@10.0.0.163:~/.nanobot/workspace/memory/MEMORY.md
scp skills/interview-prep.md mayu@10.0.0.163:~/.nanobot/workspace/skills/interview-prep/SKILL.md
```

### 7. Set Up Cron Jobs

Copy the included cron config:

```bash
scp cron/jobs.json mayu@10.0.0.163:~/.nanobot/cron/jobs.json
```

This sets up 5 automated jobs (all Mon-Sat, America/Los_Angeles):

| Time | Job | Trigger |
|---|---|---|
| 8:00am | Morning reminder + today's plan | `/morning-reminder` |
| 9:00pm | Evening pattern drill | `/evening-drill` |
| 9:30pm | Daily progress report | `/progress-report` |
| 11:45pm | End of day summary + tomorrow's plan | `/end-of-day` |
| 5:00pm Sat | Weekly summary | `/weekly-summary` |

### 8. Set Up Session Rotation (optional but recommended)

Copy the rotation script and set up a cron job to run it daily:

```bash
scp rotate_session.py mayu@10.0.0.163:~/rotate_session.py
```

On the VM, add to crontab (`crontab -e`):

```
0 10 * * * python3 ~/rotate_session.py
```

This trims session history to the last 20 messages daily, preventing the session file from growing until it drowns out AGENTS.md instructions.

### 9. Start the Gateway

```bash
# As a systemd user service (recommended)
systemctl --user start nanobot-gateway
systemctl --user enable nanobot-gateway  # start on boot

# Or manually
nanobot gateway
```

Message your bot in Telegram. You should get a greeting with your streak and today's plan.

---

## Day-to-Day Usage

| Say this | What happens |
|---|---|
| anything | Bot greets you, shows streak + today's plan |
| "algo" | Presents today's LeetCode problems |
| "hint" | Gives L1 hint (ask again for L2, again for L3) |
| paste your code | Bot scores you 1–5 on four dimensions |
| "gof" or "patterns" | Starts today's GoF pattern session |
| "math" | Starts today's Math topic (weeks 1–2) |
| "ai/ml" | Starts today's AI/ML topic (after math complete) |
| "sql" | Presents today's SQL problems |
| "behavioral" | Starts behavioral question session (week 3+) |
| "system design" | Starts mock system design interview (Saturdays, week 5+) |
| "skip" or "postpone" | Defers current problem to tomorrow (max 3 in backlog) |
| "skip core" | Defers today's core implementation problem |
| "stats" or "progress" | Shows progress summary |
| "tomorrow" or "wrap up" | Shows tomorrow's plan |

---

## Postpone System

Say "skip", "postpone", "defer", or "pass" on any problem to defer it to tomorrow.

- Max 3 postponed items **per track** (algo, GoF, AI/ML, SQL, behavioral each have their own limit)
- Postponed items appear first in the next session's queue (marked 🔒)
- Re-postponing an already-postponed item is allowed
- Clearing your backlog mid-session unlocks new problems immediately
- **Safe for lineage** — `completed_*_ids` is the only source of truth. Postponed items don't affect stats or sequence integrity. Worst case: you stall on a track but nothing corrupts.

---

## Architecture: Why Split Files?

The original `algo_problems.json` was ~106k tokens. Loading it on every session consumed most of the model's context window, leaving little room for session history and responses.

The fix: each problem and topic lives in its own file.

| File | Tokens per read |
|---|---|
| `data/algo/nc_001.json` | ~800 |
| `data/aiml/ml_m01.json` | ~700 |
| `data/sql/sql_001.json` | ~600 |
| `data/core/nc_core_s01.json` | ~400 |
| `data/design_patterns.json` | ~7k (one file, read per GoF session) |

The bot reads only the specific file needed for the current problem. A full day session stays well under 20k tokens of content reads.

`sql_problems.json` was also split after testing showed it took 16 seconds to load during the greeting (62KB, ~15k tokens). Now each SQL problem is its own file and the greeting reads only the 2 needed.

---

## Model Behavior Notes (mistral-small3.2:24b)

**Tool calls are reliable.** mistral-small3.2:24b consistently makes correct `read_file` tool calls when instructed properly.

**Instructions must be imperative but not recursive.** Soft language gets ignored under session pressure. Use direct imperatives — but avoid "before generating any response" which causes an infinite re-read loop. Use "ONCE — do not re-read" instead.

**Never use cross-flow references.** Saying "same logic as GREETING FLOW" causes the model to reinterpret from scratch without inheriting anti-scan constraints. Every flow must inline the full explicit instructions.

**Always specify the full ml_XXX sequence explicitly.** Don't say "Phase order: ml_m01→ml_m10". Write out the full list: `ml_m01, ml_m02, ..., ml_sd08`. The model must be able to find the next ID by scanning a list, not computing a range.

**maxToolIterations: 40 is a hard limit.** If instructions are ambiguous about which files to read, the model scans sequentially through all files in a directory (all 36 aiml files, all 50 SQL files). This hits the limit and breaks the session. Fix: always derive the next ID from `completed_XXX_ids` in progress.json and read ONLY that one file.

**Anti-scan guard pattern.** Every ID selection step uses two explicit guards to prevent sequential scanning:
1. **Memory lookup** — `completed_*_ids` is already in context from the progress.json read. The correct ID can be derived without any file reads.
2. **Read guard** — before each file read, verify the ID is NOT in the relevant completed list. If it is, skip it and pick the next valid ID.

This pattern is applied consistently across all flows and tracks:

| Flow | Algo | SQL | AIML | GoF | Behavioral | System Design | Core |
|---|---|---|---|---|---|---|---|
| Greeting | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Morning Reminder | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Evening Drill | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Progress Report | ✅ | ✅ | ✅ | ✅ | — | — | — |
| End of Day | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Algo Session | ✅ | — | — | — | — | — | — |
| SQL Session | — | ✅ | — | — | — | — | — |
| AIML Session | — | — | ✅ | — | — | — | — |
| GoF Session | — | — | — | ✅ | — | — | — |
| Behavioral Session | — | — | — | — | ✅ | — | — |
| System Design | — | — | — | — | — | ✅ | — |
| Core (inline) | — | — | — | — | — | — | ✅ |

**The model uses cached session history over instructions.** Clear `~/.nanobot/workspace/sessions/telegram_*.jsonl` any time the bot goes off-rails.

---

## Gotchas

**Skill directory format**
Skills must be at `workspace/skills/{name}/SKILL.md`. A flat file like `workspace/skills/interview-prep.md` is silently ignored by nanobot.

**VM timezone must be set**
nanobot injects VM local time into every message. If the VM is in UTC (Ubuntu default), the bot will think it's a different day at midnight boundaries. Fix: `sudo timedatectl set-timezone America/Los_Angeles`.

**allowFrom breaking change (v0.1.4.post4+)**
Empty `allowFrom: []` now denies all senders. Set `"allowFrom": ["YOUR_CHAT_ID"]` in your Telegram channel config.

**Rest day is configurable**
The bot enforces Sunday as a rest day by default. To change it, update `rest_days` in `progress.json` and the "Rest day: Sunday" line in `USER.md`. The LLM follows whatever is configured.

**sudo mkdir breaks scp**
If you create the skill directory with `sudo`, it's owned by root and `scp` fails. Fix: `sudo chown -R youruser:youruser ~/.nanobot/workspace/skills/`

**scp overwrites manual VM edits**
Always fix files locally in nanogrind first, then re-scp. Never edit files directly on the VM.


**Do NOT use the message() tool**
`message()` is a tool call that re-triggers the agent loop — causing infinite loops. The model should output plain text with no tool calls. Nanobot automatically delivers the final text response to Telegram when the loop ends (no tool calls = loop terminates).

**Stale session history overrides AGENTS.md**
nanobot accumulates every message in `~/.nanobot/workspace/sessions/telegram_CHATID.jsonl`. As this grows, history drowns out startup instructions. Symptoms: bot ignores the study plan, behaves like a generic assistant. Fix: clear the session file and restart.

```bash
ssh mayu@10.0.0.163 "rm ~/.nanobot/workspace/sessions/telegram_*.jsonl && systemctl --user restart nanobot-gateway"
```

**Stale cron sessions cause bad output**
Cron jobs have their own session files (`cron_*.jsonl`). If they accumulate old history, cron messages go off-rails. Fix:

```bash
ssh mayu@10.0.0.163 "rm -f ~/.nanobot/workspace/sessions/cron_*.jsonl && systemctl --user restart nanobot-gateway"
```

**Restarting ollama breaks the gateway**
If you restart your ollama container, the nanobot gateway loses its connection. Always restart the gateway after restarting ollama.

**Context window truncation**
ollama's default context window is 32,768 tokens. The custom `mistral-small3.2:24b-48k` model (Modelfile sets `num_ctx 49152`) prevents this. Confirm with: `make status` and check ollama logs for `msg="truncating input prompt"`.

---

## File Structure

```
nanogrind/
├── README.md
├── Modelfile                              # Custom model: mistral-small3.2:24b, 48k ctx
├── Makefile                               # make setup / make scp VM=user@IP
├── rotate_session.py                      # Trims session JSONL + HISTORY.md daily
├── cron/
│   └── jobs.json                          # 5 scheduled cron jobs
├── skills/
│   └── interview-prep.md                  # Copy to VM as skills/interview-prep/SKILL.md
└── workspace/
    ├── USER.md                            # Edit name/timezone; always loaded as system prompt
    ├── AGENTS.md                          # All flows, routing, data file refs, session rules
    ├── SOUL.md                            # Bot personality
    ├── memory/
    │   └── MEMORY.md                      # Bot persistent memory (curriculum, user info)
    └── interview-prep/
        └── data/
            ├── algo/                      # 149 files: nc_001.json … nc_149.json
            │   └── nc_XXX.json            # One problem each (~800 tokens)
            ├── aiml/                      # 36 files: ml_m01.json … ml_sd08.json
            │   └── ml_XXX.json            # One topic each (~700 tokens)
            ├── sql/                       # 50 files: sql_001.json … sql_050.json
            │   └── sql_XXX.json           # One problem each (~600 tokens)
            ├── core/                      # 33 files: nc_core_s01.json … nc_core_ml03.json
            │   └── nc_core_XXX.json       # One implementation problem each (~400 tokens)
            ├── design_patterns.json       # 23 GoF + 5 SOLID patterns
            ├── data_structures.json       # 19 DS/algo category cards

            ├── behavioral.json            # 30 behavioral questions
            ├── system_design.json         # System design problems
            ├── progress.json              # Source of truth — bot writes completions here
            └── attempts.json             # Bot appends session history here
```

**AI/ML phase order** (gated — math must complete before AI unlocks):

| Phase | IDs | Topics |
|---|---|---|
| Math Refresher | ml_m01–ml_m10 | Linear algebra, calculus, probability, stats, optimization |
| Core ML | ml_c01–ml_c08 | Regression, classification, SVMs, trees, clustering, PCA |
| Deep Learning | ml_d01–ml_d05 | Neural nets, CNNs, RNNs, transformers, training techniques |
| Frontier AI | ml_f01–ml_f05 | LLMs, RAG, diffusion models, LoRA/fine-tuning, alignment |
| ML System Design | ml_sd01–ml_sd08 | Design problems for ML infrastructure |

---

## Useful Commands

```bash
# Pull base model and create the custom model (via Docker on Windows host)
make setup

# SCP all workspace files to VM
make scp VM=mayu@10.0.0.163

# Restart the gateway after config/file changes
ssh mayu@10.0.0.163 "systemctl --user restart nanobot-gateway"

# Clear chat history for a fresh session
ssh mayu@10.0.0.163 "rm ~/.nanobot/workspace/sessions/telegram_*.jsonl && systemctl --user restart nanobot-gateway"

# Clear stale cron sessions
ssh mayu@10.0.0.163 "rm -f ~/.nanobot/workspace/sessions/cron_*.jsonl && systemctl --user restart nanobot-gateway"

# Check gateway logs
ssh mayu@10.0.0.163 "journalctl --user -u nanobot-gateway -n 50"

# Pull progress.json back to local after a session
scp mayu@10.0.0.163:~/.nanobot/workspace/interview-prep/data/progress.json ./workspace/interview-prep/data/progress.json

# Check model status
make status
```

---

## Contributing

PRs welcome — especially:
- Linux/macOS native setup (no Hyper-V)
- Docker Compose version
- Additional curriculum content or problem sets

---

## License

MIT

---

*Made with love (and a lot of debugging) by [@mayuranganesathas](https://github.com/mayuranganesathas)*
