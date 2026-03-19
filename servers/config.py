import os
from pathlib import Path

# Production: VM path. Override for local dev/tests via env var.
DATA_DIR = Path(os.environ.get(
    "INTERVIEW_PREP_DATA",
    "/home/mayu/.nanobot/workspace/interview-prep/data"
))

PROGRESS_FILE    = DATA_DIR / "progress.json"
ATTEMPTS_FILE    = DATA_DIR / "attempts.json"
REVIEW_FILE      = DATA_DIR / "review_queue.json"
WEAK_AREAS_FILE  = DATA_DIR / "weak_areas.json"
NOTES_FILE       = DATA_DIR / "notes.json"
TIMER_FILE       = DATA_DIR / "timer_queue.json"
