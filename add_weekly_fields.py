#!/usr/bin/env python3
"""Add week_start and week_completions to progress.json."""
import json
from pathlib import Path
from datetime import date, timedelta

p = Path("/home/mayu/.nanobot/workspace/interview-prep/data/progress.json")
data = json.loads(p.read_text())

today = date.today()
monday = (today - timedelta(days=today.weekday())).isoformat()

added = []
if "week_start" not in data:
    data["week_start"] = monday
    added.append("week_start")
if "week_completions" not in data:
    data["week_completions"] = {"algo": 0, "sql": 0, "gof": 0, "aiml": 0}
    added.append("week_completions")
if "last_quiz_id" not in data:
    data["last_quiz_id"] = None
    added.append("last_quiz_id")
if "total_aiml_sessions" not in data.get("stats", {}):
    data.setdefault("stats", {})["total_aiml_sessions"] = 0
    added.append("total_aiml_sessions")
if "quiz_today_count" not in data:
    data["quiz_today_count"] = 0
    added.append("quiz_today_count")
if "quiz_today_date" not in data:
    data["quiz_today_date"] = None
    added.append("quiz_today_date")
if "last_lang_quiz_id" not in data:
    data["last_lang_quiz_id"] = None
    added.append("last_lang_quiz_id")
if "completed_lang_quiz_ids" not in data:
    data["completed_lang_quiz_ids"] = []
    added.append("completed_lang_quiz_ids")

p.write_text(json.dumps(data, indent=2) + "\n")
print(f"Added: {added}" if added else "Already up to date")
print(f"week_start: {data['week_start']}, week_completions: {data['week_completions']}")
