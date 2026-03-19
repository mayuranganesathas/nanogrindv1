"""Seed / patch notes.json and backfill completed_lang_quiz_ids. Safe to re-run."""
import json
from pathlib import Path

NOTES_FILE    = Path("/home/mayu/.nanobot/workspace/interview-prep/data/notes.json")
PROGRESS_FILE = Path("/home/mayu/.nanobot/workspace/interview-prep/data/progress.json")

# ── Notes ────────────────────────────────────────────────────────────────────

new_notes = {
    "algo": {
        "Two Pointers": [
            {
                "user_note": "- frequency maps are important to adhere to frequencies, .split() or .map() doesnt need return if there isnt curly braces, arrays are not unique keys in sets/maps, bucket sort to sort frequency values!",
                "coach_note": "Frequency maps track counts and are key for top-K and anagram problems. Arrow functions without curly braces have implicit return. Arrays as Set/Map keys use reference equality not value equality — always stringify (JSON.stringify) or use a delimiter-joined string. Bucket sort is O(n) for frequency-based ordering vs O(n log n) for comparison sort.",
                "date": "2026-03-19"
            }
        ],
        "Sliding Window": [
            {
                "user_note": "One-pass solution: track minBuy and globalProfit simultaneously. Don't need nested loops — update minBuy after calculating profit so you don't buy and sell on the same day.",
                "coach_note": "Buy & Sell Stock is a greedy + running-min pattern, not a traditional sliding window. Key insight: at each index, the best profit is price[i] - min(price[0..i-1]). Track running min and max profit in one pass — O(n) time, O(1) space. Always update minBuy AFTER profit calculation to avoid same-day buy/sell. Return 0 (not negative) if no profitable trade exists.",
                "date": "2026-03-19"
            }
        ]
    }
}

# Merge additively — don't overwrite existing entries
if NOTES_FILE.exists():
    existing = json.loads(NOTES_FILE.read_text())
else:
    existing = {}

for track, categories in new_notes.items():
    existing.setdefault(track, {})
    for category, entries in categories.items():
        if category not in existing[track]:
            existing[track][category] = entries
            print(f"Added notes: {track} / {category}")
        else:
            print(f"Skipped (already exists): {track} / {category}")

NOTES_FILE.write_text(json.dumps(existing, indent=2))

# ── Backfill completed_lang_quiz_ids ────────────────────────────────────────

progress = json.loads(PROGRESS_FILE.read_text())
completed_lang = progress.setdefault("completed_lang_quiz_ids", [])
last_lang = progress.get("last_lang_quiz_id")

if last_lang and last_lang not in completed_lang:
    completed_lang.append(last_lang)
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2) + "\n")
    print(f"Backfilled completed_lang_quiz_ids with {last_lang}")
else:
    print("completed_lang_quiz_ids already up to date")
