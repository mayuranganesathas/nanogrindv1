"""
Migrate behavioral.json: convert question strings to objects with id, competency, question fields.
Safe to re-run — skips questions that already have id fields.
"""
import json
from pathlib import Path

BEHAVIORAL_FILE = Path("/home/mayu/.nanobot/workspace/interview-prep/data/behavioral.json")

data = json.loads(BEHAVIORAL_FILE.read_text())
competencies = data["behavioral"]["competencies"]

counter = 1
changed = 0
for comp_name, comp in competencies.items():
    new_questions = []
    for q in comp["questions"]:
        if isinstance(q, str):
            new_questions.append({
                "id": f"bq_{counter:03d}",
                "competency": comp_name,
                "question": q,
            })
            changed += 1
        elif isinstance(q, dict) and "id" not in q:
            # Already a dict but missing id — add it
            q["id"] = f"bq_{counter:03d}"
            q.setdefault("competency", comp_name)
            new_questions.append(q)
            changed += 1
        else:
            # Already has id — preserve as-is
            new_questions.append(q)
        counter += 1
    comp["questions"] = new_questions

BEHAVIORAL_FILE.write_text(json.dumps(data, indent=2))
print(f"Migrated {changed} behavioral questions to objects with id fields.")
print(f"Total questions: {counter - 1}")
