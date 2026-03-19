#!/usr/bin/env python3
"""Split design_patterns.json into individual files in a gof/ directory."""
import json
from pathlib import Path

src = Path("/mnt/c/Users/U/Documents/interview-prep-nanobot/workspace/interview-prep/data/design_patterns.json")
gof_dir = Path("/mnt/c/Users/U/Documents/nanogrindv2/data_generated/gof")
gof_dir.mkdir(exist_ok=True)

data = json.loads(src.read_text())
patterns = data["design_patterns"]["patterns"]

for pattern in patterns:
    out = gof_dir / f"{pattern['id']}.json"
    out.write_text(json.dumps(pattern, indent=2) + "\n")
    print(f"Written {out.name}")

print(f"\nDone: {len(patterns)} patterns → {gof_dir}")
