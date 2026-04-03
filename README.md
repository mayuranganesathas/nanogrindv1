# nanogrindv2

A self-hosted Telegram bot for structured, full-stack interview prep. Covers algorithms, SQL, system design, GoF patterns, AI/ML, behavioral, NeetCode Core implementations, and data structures — all in one place, driven by a coached session model with spaced repetition.

Runs on a local VM. No cloud dependencies, no subscriptions. Powered by [nanobot](https://github.com/HKUDS/nanobot) + two Python MCP servers.

---

## Intent

Most interview prep tools give you problems and a blank editor. This bot acts as a coach:

- It asks for your brute force first, won't let you skip to optimal
- It runs follow-up Q&A after every solution — walks you through edge cases, complexity trade-offs, and "why this data structure"
- It scores every attempt (1–5) and schedules the problem for spaced repetition review
- It tracks weak pattern areas and surfaces them over time
- It keeps a study schedule with weekly goals and unlock milestones toward a target date

The LLM is the coach. The MCP servers are the source of truth — all queue order, scoring, and writes go through typed tool calls so the LLM never manipulates data directly.

---

## Architecture

```
Telegram ──► nanobot gateway (VM)
                ├── progress_server  (MCP, stdio)  ← queue, writes, spaced repetition, reviews, notes
                └── content_server   (MCP, stdio)  ← problem/topic content files

LLM (local llama-server or cloud API)
  └── receives tool results, runs session flows defined in AGENTS_MCP.md
```

---

## Curriculum

| Track | Count | IDs | Unlocks |
|-------|-------|-----|---------|
| Algo (NeetCode 150) | 149 | nc_001–nc_149 | Week 1 |
| SQL (query + conceptual) | 65 | sql_001–sql_065 | Week 1 |
| GoF + SOLID patterns | 28 | gof_001–023, solid_001–005 | Week 1 |
| Data Structures | 19 | ds_a01–ds_ag01 | Week 1 |
| NeetCode Core (implementations) | 33 | nc_core_* | Week 1 |
| System Design | 41 | sd_c01–sd_l08 | Week 6 |
| Behavioral | 30 | bq_001–bq_030 | Week 8 (Sunday only) |
| AI/ML (Math → Core → DL → Frontier → ML System Design) | 36 | ml_m01–ml_sd08 | Week 8 |
| Language Quiz (TypeScript; Python + C# from June 2026) | 80 | ts_001–030, py_001–025, cs_001–025 | Daily |

**Target:** Complete all tracks by July 31, 2026.

---

## Weekly Goals

| Track | Weekly Target | Notes |
|-------|--------------|-------|
| Algo | 15 | ~2–3/day Mon–Sat |
| SQL | 5 | ~1/day |
| GoF | 3 | |
| DS | 3 | |
| NC Core | 4 | |
| System Design | 4 | Unlocks week 6 |
| Behavioral | 5 | Sundays only, unlocks week 8 |
| AI/ML | 4 | Unlocks week 8 |

Goals reset every Monday. Tracked via `week_completions` in progress.json.

---

## Session Flows

Each track has a structured flow the LLM follows exactly. All flows are defined in `AGENTS_MCP.md`.

### Algo
1. `start_track("algo")` → `get_problem(id)`
2. Present problem + thinking questions
3. **Brute force round** — accept logic/pseudocode, push back if wrong
4. **Optimal round** — 3-tier hint escalation (L1 nudge → L2 approach → L3 pseudocode)
5. Evaluate submitted code as-is (no mental corrections)
6. **Follow-up Q&A** — edge cases, complexity, data structure justification, invariants
7. `complete_item` — atomic: marks done + records attempt + schedules review
8. Category completion check — if category done, show cheat sheet + ask for notes

### SQL
Same structure with correctness-focused scoring. Supports both query problems and conceptual questions (ACID, indexes, sharding).

### GoF / SOLID
Question-driven: state intent → Q&A → code example → score on conceptual understanding + application + code quality.

### System Design (week 6+)
Mock interview format. Requirements → architecture → scalability → trade-offs.

### Behavioral (Sundays, week 8+)
STAR format enforcement. Saves best response per question; shows it before re-attempts.

### AI/ML (week 8+)
Concept walk-through → thinking questions in Python → reveal reference implementation → exercises.

### Data Structures / NC Core
Concept card + thinking questions + implementation.

---

## Features

### Session Management
- **`start_track`** — single tool call starts or resumes any session; handles in-progress detection, postponed items, queue order
- **Session resume** — if an in-progress item is < 2 hours old, `start_track` resumes it automatically
- **Postpone** — up to 3 items per track in backlog; postponed items shown with `[Postponed]` prefix and rotated to front of queue
- **Cancel** — `/cancel` clears in-progress without recording an attempt

### Scoring
- Strict 1–5 per dimension; never inflated
- Score is locked on first submission — no resubmissions after feedback (except clear syntax typos)
- Composite score is the average across dimensions
- Correctness is judged on actual output, not intent

### Spaced Repetition
- Score 1 → review in 1 day
- Score 2 → review in 2 days
- Score 3 → review in 4 days
- Score 4 → review in 7 days
- Score 5 → no review scheduled
- Manual override: `add_to_review(track, id, days)` — queue any completed item for review at any time

### Weak Areas
- Aggregated by pattern tag (e.g. "monotonic_stack", "two_pointers")
- Flags tags with avg score < 3.0
- Flags tags not practiced in 14+ days (confidence decay)
- Surface via `/weak-areas`

### Daily Quizzes
- **Pop quiz** (9am Mon–Fri, 7pm Mon–Sat) — brute force + optimal pattern on a completed problem; weighted toward weak/decayed tags
- **Lang quiz** — chains automatically after pop quiz; TypeScript only until June 2026, then Python + C# added
- **Quiz window** — 30-minute window per session; fires a nudge if the window closes with no quiz done
- Quizzes are silenced if an active session is in progress

### Notes System
- Save takeaways per category after completing it
- Notes surfaced during reviews: "📝 Your notes from last time: …"

### Timed Mock
- Trigger: "mock" or "timed"
- Easy 15min / Medium 25min / Hard 40min
- `timer_check.py` runs as a system cron (every minute) and sends a Telegram ping when time expires
- `within_time_limit` recorded in the attempt

### Cron Schedule (America/Los_Angeles)

| Time | Job | Purpose |
|------|-----|---------|
| Mon–Sat 8:00am | `/morning-reminder` | Today's schedule card |
| Mon–Fri 9:00am | `/pop-quiz` | Morning quiz block (chains to lang quiz) |
| Mon–Fri 9:30am | Quiz window close | Nudge if quiz not done |
| Wed 6:00pm | `/midweek-check` | Weekly pace check |
| Mon–Sat 7:00pm | `/pop-quiz` | Evening quiz block (chains to lang quiz) |
| Mon–Sat 7:30pm | Quiz window close | Nudge if quiz not done |
| Mon–Sat 9:30pm | `/evening-drill` | GoF pattern review (3 questions) |
| Mon–Sat 10:00pm | `/day-review` | Full progress card |
| Sat 5:00pm | `/weekly-summary` | Weekly totals |
| Sun 9:00am | `/morning-reminder` | Sunday schedule |
| Sun 10:00am | Behavioral nudge | "Say 'behavioral' to start" |
| Sun 5:00pm | `/week-kickoff` | Next week's queue preview |
| Mon–Sat 11:45pm | `/end-of-day` | Streak + tomorrow's queue |

System cron (every minute): `timer_check.py` — sends Telegram ping when timed mock timer fires.

---

## MCP Tools

### progress_server

| Tool | Purpose |
|------|---------|
| `start_track(track)` | Start or resume a session — returns next item id, title, is_resume flag |
| `get_greeting_card()` | Streak, stats, next items with titles, due reviews, weekly progress — all in one call |
| `get_progress_report()` | Completed counts, stats, quiz counts |
| `get_progress()` | Streak, stats, completed counts, last active date |
| `get_today_activity()` | All attempts completed today |
| `get_evening_drill()` | GoF pattern for evening drill; rotates across completed patterns |
| `complete_item(track, id, scores, solution, hints_used, ...)` | Atomic: mark done + log attempt + schedule review + category check |
| `log_attempt(track, id, scores, solution, ...)` | Record scores, trigger spaced repetition, update weak areas |
| `add_completed(track, id)` | Mark item completed (use `complete_item` instead for sessions) |
| `add_postponed(track, id)` | Add to backlog (max 3) |
| `remove_postponed(track, id)` | Clear from backlog |
| `get_next_items(track, n)` | Next N items — postponed first, then uncompleted in order |
| `get_due_reviews()` | Reviews due today, sorted most overdue first |
| `clear_review(track, item_id)` | Remove from review queue after reviewing |
| `add_to_review(track, item_id, days)` | Manually add any completed item to the review queue |
| `get_weak_areas()` | Pattern tags by avg score; includes confidence decay |
| `get_in_progress()` | Current in-progress item |
| `clear_in_progress()` | Cancel session without recording attempt |
| `get_quiz_problem()` | Pick a completed algo problem for pop quiz (weighted toward weak/decayed tags) |
| `get_lang_quiz_problem()` | Next language quiz question in difficulty order (active languages only) |
| `reset_last_lang_quiz()` | Remove last lang quiz from completed list |
| `get_category_summary(track, id)` | Check if category complete; return cheat sheet + key patterns |
| `save_note(track, category, user_note, coach_note)` | Save session takeaway |
| `get_notes(track, category)` | Read saved notes |
| `save_behavioral_response(question_id, response, score, improvements)` | Save best behavioral answer |
| `get_behavioral_best(question_id)` | Retrieve best saved behavioral response |
| `start_timer(minutes, label)` | Write timer file for system cron pickup |
| `stop_timer()` | Stop active timer; returns whether it stopped before expiry |
| `get_last_completed(track)` | Most recently completed item for a track |

### content_server

| Tool | Purpose |
|------|---------|
| `get_problem(id)` | Algo problem — description, constraints, test cases, hints, follow-up questions, complexity |
| `get_sql_problem(id)` | SQL query problem or conceptual question |
| `get_pattern(id)` | GoF/SOLID pattern — intent, questions, code example |
| `get_aiml_topic(id)` | AI/ML topic — concepts, thinking questions, code example, exercises |
| `get_behavioral_questions(ids)` | Behavioral questions by ID |
| `get_system_design(id)` | System design problem |
| `get_core_problem(id)` | NeetCode Core implementation problem |
| `get_data_structure(id)` | Data structure concept card |
| `get_item_titles(track, ids)` | Lightweight id → title lookup |

---

## Choosing a Model

The bot works with any OpenAI-compatible API. Model quality directly affects tool calling reliability and code evaluation.

| Tier | Examples | Tool Calling | Notes |
|------|----------|-------------|-------|
| **Small (7B–13B)** | Qwen 2.5 7B, Llama 3.1 8B | Unreliable | Frequent tool call errors. Usable for simple flows only. |
| **Mid (24B–27B)** | Mistral Small 3.2 24B, Qwen 3.5 27B | Good | Recommended minimum. Qwen 3.5 27B outperforms Mistral on code evaluation. |
| **Large (70B+)** | Llama 3.3 70B, Qwen 2.5 72B | Excellent | Most reliable. Needs ~40GB VRAM. |
| **Cloud API** | Claude Sonnet/Opus, GPT-4o | Excellent | Best results. No local VRAM needed. |

See `nanobot-llama-qwen.md` for llama-server setup, VRAM budget, and the 9B fallback.

---

## Repository Structure

```
servers/
    progress_server.py   — queue, spaced repetition, weak areas, notes, timer, quiz logic
    content_server.py    — content serving for all tracks
    config.py            — file path constants

tests/
    test_progress.py     — unit tests

data_generated/          — generated locally, copied to VM data dir
    gof/                 — individual gof_{id}.json files
    language_quiz/       — ts_001–030, py_001–025, cs_001–025
    sql/                 — sql_051–065 (conceptual questions)

AGENTS_MCP.md            — nanobot system prompt (all session flows and rules)
config.json              — nanobot config + MCP server registration
config.qwen.json         — Qwen-specific config
config.mistral.json      — Mistral fallback config
cron_jobs.json           — scheduled cron jobs
timer_check.py           — system cron: sends Telegram ping when timed mock expires

generate_language_quiz.py  — generates data_generated/language_quiz/
generate_sql_concepts.py   — generates data_generated/sql/ (sql_051–065)
split_design_patterns.py   — splits design_patterns.json → individual gof/{id}.json files
add_weekly_fields.py       — migration: adds weekly tracking fields to progress.json
```

---

## Stack

- **Bot framework:** [nanobot](https://github.com/HKUDS/nanobot) v0.1.4.post3
- **MCP:** [FastMCP](https://github.com/jlowin/fastmcp) (Python)
- **Default LLM:** Qwen 3.5 27B Q4_K_M via [llama.cpp](https://github.com/ggml-org/llama.cpp) server
- **Delivery:** Telegram
