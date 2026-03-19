"""
Remove the bogus nc_015 first attempt (hint-only, no real submission)
and fix the stale review queue entry.
"""
import json
from pathlib import Path

DATA = Path("/home/mayu/.nanobot/workspace/interview-prep/data")
ATTEMPTS_FILE    = DATA / "attempts.json"
REVIEW_FILE      = DATA / "review_queue.json"
WEAK_AREAS_FILE  = DATA / "weak_areas.json"

# ── Remove the bad nc_015 first attempt ──────────────────────────────────────
attempts_data = json.loads(ATTEMPTS_FILE.read_text())
before = len(attempts_data["attempts"])
attempts_data["attempts"] = [
    a for a in attempts_data["attempts"]
    if not (a.get("item_id") == "nc_015" and a.get("solution") == "User requested hint before submitting solution")
]
removed = before - len(attempts_data["attempts"])
ATTEMPTS_FILE.write_text(json.dumps(attempts_data, indent=2))
print(f"Removed {removed} bogus nc_015 attempt(s) from attempts.json")

# ── Remove stale nc_015 review (second attempt was 4.83 = no review needed) ──
rq = json.loads(REVIEW_FILE.read_text())
before = len(rq["items"])
rq["items"] = [i for i in rq["items"] if not (i["item_id"] == "nc_015" and i["track"] == "algo")]
removed = before - len(rq["items"])
REVIEW_FILE.write_text(json.dumps(rq, indent=2))
print(f"Removed {removed} stale nc_015 review entry from review_queue.json")

# ── Recompute weak_areas from clean attempts ──────────────────────────────────
from datetime import date, timedelta

tag_scores: dict[str, list[float]] = {}
tag_last_date: dict[str, str] = {}

for attempt in attempts_data["attempts"]:
    tags = attempt.get("pattern_tags", [])
    score = attempt.get("composite_score", 0.0)
    ts_date = attempt.get("timestamp", "")[:10]
    for tag in tags:
        tag_scores.setdefault(tag, []).append(score)
        if tag not in tag_last_date or ts_date > tag_last_date[tag]:
            tag_last_date[tag] = ts_date

today = date.today().isoformat()
decay_cutoff = (date.today() - timedelta(days=14)).isoformat()

by_tag = {}
for tag, scores in tag_scores.items():
    avg = round(sum(scores) / len(scores), 2)
    last = tag_last_date.get(tag, today)
    by_tag[tag] = {
        "avg_score": avg,
        "attempt_count": len(scores),
        "below_threshold": avg < 3.0,
        "last_attempt_date": last,
        "decayed": last < decay_cutoff,
    }

weak_areas = {
    "schema_version": "1.0",
    "last_computed": today,
    "by_pattern_tag": by_tag,
}
WEAK_AREAS_FILE.write_text(json.dumps(weak_areas, indent=2))
print(f"Recomputed weak_areas.json — {len(by_tag)} tags")
for tag, info in by_tag.items():
    print(f"  {tag}: avg={info['avg_score']} count={info['attempt_count']}")
