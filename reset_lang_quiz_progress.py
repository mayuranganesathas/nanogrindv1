"""Reset lang quiz progress so questions start fresh from beginner difficulty."""
import json
from pathlib import Path

PROGRESS_FILE = Path("/home/mayu/.nanobot/workspace/interview-prep/data/progress.json")

data = json.loads(PROGRESS_FILE.read_text())
data["completed_lang_quiz_ids"] = []
data["last_lang_quiz_id"] = None
PROGRESS_FILE.write_text(json.dumps(data, indent=2) + "\n")
print("Reset completed_lang_quiz_ids=[] and last_lang_quiz_id=null")
