# nanogrindv2 — Build Plan

## What This Is
A rewrite of the interview prep bot using MCP servers for all data logic.
The key insight: move "what's next" logic into the server so the LLM never scans files.

## Context
- Existing bot: nanogrind (`/mnt/c/Users/U/Documents/nanogrind/`)
- Data files: `nanogrind/workspace/interview-prep/data/` — point MCP servers here, do not copy
- Existing progress schema: `nanogrind/workspace/interview-prep/data/progress.json`
- Existing prompts/flows: `nanogrind/workspace/AGENTS.md` (reference for session flow logic)

## Architecture Decisions
- **LLM**: mistral (Ollama) for prod, Claude API for integration tests
- **Gateway**: keep nanobot + Telegram (do not replace)
- **Data**: MCP servers read/write the existing `interview-prep/data/` directory
- **in_progress**: single item `{"track": "algo", "id": "nc_015"}` or null

## Folder Structure
```
nanogrindv2/
├── servers/
│   ├── __init__.py
│   ├── progress_server.py   # MCP server — owns all progress.json reads/writes
│   └── content_server.py    # MCP server — serves problem/pattern/topic files
├── tests/
│   ├── __init__.py
│   ├── test_progress.py     # Unit tests (no LLM needed)
│   ├── test_content.py      # Unit tests (no LLM needed)
│   └── test_integration.py  # Claude API integration tests
├── pyproject.toml
└── PLAN.md                  # This file
```

## Phase 1 — Progress Server (`servers/progress_server.py`)

Use FastMCP. Expose these tools:

### Tools

**`get_progress()`**
Returns a minimal context object — only fields the LLM needs:
```json
{
  "streak_days": 6,
  "last_active_date": "2026-03-16",
  "start_date": "2026-03-08",
  "total_problems_solved": 14,
  "total_sql_solved": 0,
  "total_pattern_sessions": 0,
  "total_behavioral_sessions": 0,
  "in_progress": null
}
```
Does NOT return full completed_*_ids lists — those are internal state used by get_next_items.

**`get_next_items(track: str, n: int = 1) -> list[dict]`**
Returns next N items for a track, in correct priority order (postponed first).
```json
[
  {"id": "sql_001", "postponed": true},
  {"id": "sql_002", "postponed": true}
]
```
Tracks: "algo", "sql", "gof", "aiml", "behavioral", "system_design"
Server handles all queue logic — LLM never needs to scan.

**`set_in_progress(track: str, id: str)`**
Sets `in_progress` field. Called when LLM presents a problem to the user.

**`add_completed(track: str, id: str)`**
Atomically:
1. Appends id to the correct `completed_*_ids` list
2. Increments the correct `stats.*` counter
3. Sets `last_active_date` to today (PST)
4. Removes id from `postponed_*_ids` if present
5. Clears `in_progress` if it matches
6. Updates `streak_days` if needed
Returns updated stats.

**`add_postponed(track: str, id: str)`**
Adds to postponed list. Enforces max 3 per track.
Returns `{"ok": true}` or `{"ok": false, "error": "Backlog full (3/3)"}`.

**`remove_postponed(track: str, id: str)`**
Removes from postponed list.

**`get_in_progress()`**
Returns current `in_progress` value or null.

### Track → Field Mapping (internal to server)
```python
TRACK_MAP = {
    "algo":          ("completed_problem_ids",   "postponed_problem_ids",   "total_problems_solved",    "nc_001"..."nc_149"),
    "sql":           ("completed_sql_ids",        "postponed_sql_ids",       "total_sql_solved",         "sql_001"..."sql_050"),
    "gof":           ("completed_pattern_ids",    "postponed_pattern_ids",   "total_pattern_sessions",   "gof_001"..."gof_023"),
    "aiml":          ("completed_concept_ids",    "postponed_concept_ids",   None,                       "ml_m01"..."ml_sd08"),
    "behavioral":    ("completed_behavioral_ids", "postponed_behavioral_ids","total_behavioral_sessions","bq_001"..."bq_030"),
    "system_design": ("completed_design_ids",     "postponed_design_ids",    "total_design_mocks",       "sd_c01"..."sd_l08"),
}
```

### AIML Phase Gating (internal to server)
- Math phase: ml_m01–ml_m10 (active until all 10 complete)
- Core ML: ml_c01–ml_c08 (unlocks after math complete)
- Deep Learning: ml_d01–ml_d05
- Frontier: ml_f01–ml_f05
- ML System Design: ml_sd01–ml_sd08
`get_next_items("aiml")` returns the correct phase automatically.

---

## Phase 2 — Content Server (`servers/content_server.py`)

**`get_problem(id: str)`** — reads `data/algo/nc_XXX.json`
**`get_sql_problem(id: str)`** — reads `data/sql/sql_XXX.json`
**`get_pattern(id: str)`** — reads from `data/design_patterns.json`, returns single pattern
**`get_aiml_topic(id: str)`** — reads `data/aiml/ml_XXX.json`
**`get_behavioral_questions(ids: list[str])`** — reads from `data/behavioral.json`
**`get_system_design(id: str)`** — reads from `data/system_design.json`

All tools return only the fields needed, not the full JSON.

---

## Phase 3 — Tests

### Unit tests (`tests/test_progress.py`, `tests/test_content.py`)
- No LLM needed
- Test each MCP tool directly
- Use a temp copy of progress.json so tests don't corrupt real data
- Key cases:
  - `get_next_items("algo")` skips completed IDs correctly
  - `get_next_items("sql")` returns postponed items first
  - `add_completed` only changes the 3 correct fields, leaves all else intact
  - `add_postponed` enforces 3-per-track limit
  - `add_completed` removes from postponed if present
  - AIML phase gating: ml_c01 not returned until all ml_m* complete

### Integration tests (`tests/test_integration.py`)
- Use Claude API (claude-haiku-4-5 for cost)
- Verify the agent correctly calls tools in right order for each flow
- Key cases:
  - Greeting: exactly 7 tool calls, correct IDs
  - Algo session: get_next_items → set_in_progress → present → add_completed → get_next_items
  - SQL session: postponed items presented first
  - Write safety: add_completed doesn't corrupt other fields

---

## Progress Schema Changes
Add `in_progress` field to progress.json:
```json
"in_progress": null
// or: {"track": "algo", "id": "nc_015"}
```
The progress server manages this — no LLM calculation needed.

---

## Setup
```toml
# pyproject.toml
[project]
name = "nanogrindv2"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]",        # FastMCP
    "anthropic",       # for integration tests only
    "pytest",
    "pytest-asyncio",
]
```

## Data Path Config
```python
# servers/config.py
import os
DATA_DIR = os.environ.get(
    "INTERVIEW_PREP_DATA",
    "/home/mayu/.nanobot/workspace/interview-prep/data"  # VM path (prod)
)
# Override in tests: INTERVIEW_PREP_DATA=/tmp/test_data pytest
```

---

## What Disappears from AGENTS.md Once This Is Live
- All `EXACTLY N tool calls` counting
- All `⚠️ GUARD: verify ID is NOT in completed_problem_ids`
- All inline nc_001…nc_149 sequences
- All `IMMEDIATELY after reading — determine ALL slot IDs`
- All `Do NOT start from after slot 1`
- The entire AIML QUICK REFERENCE table
- All per-flow FILE ACCESS RULES

The new system prompt becomes ~50 lines instead of ~1000.
