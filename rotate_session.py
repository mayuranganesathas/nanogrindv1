import os

SESSION_FILE = os.path.expanduser("~/.nanobot/workspace/sessions/telegram_1851230297.jsonl")
HISTORY_FILE = os.path.expanduser("~/.nanobot/workspace/memory/HISTORY.md")
KEEP_MESSAGES = 20
KEEP_HISTORY_LINES = 50

# Rotate session history
if os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "r") as f:
        lines = [l for l in f.readlines() if l.strip()]
    if len(lines) > KEEP_MESSAGES:
        with open(SESSION_FILE, "w") as f:
            f.writelines(lines[-KEEP_MESSAGES:])
        print("Session rotated: kept last {} of {} messages".format(KEEP_MESSAGES, len(lines)))
    else:
        print("Session ok: {} messages".format(len(lines)))

# Trim HISTORY.md — keep header block + last N lines
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        lines = f.readlines()
    if len(lines) > KEEP_HISTORY_LINES:
        # Always keep the CURRICULUM RESET block (first 20 lines) + last 30 lines of history
        header = lines[:20]
        tail = lines[-30:]
        with open(HISTORY_FILE, "w") as f:
            f.writelines(header + ["\n[... older history trimmed ...]\n\n"] + tail)
        print("HISTORY.md trimmed: {} -> {} lines".format(len(lines), 20 + 30))
    else:
        print("HISTORY.md ok: {} lines".format(len(lines)))
