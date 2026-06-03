import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "hn_jobs.json")
META_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "metadata.json")

with open(DATA_PATH, encoding="utf-8") as f:
    raw = json.load(f)

dates = [e["date"][:7] for e in raw if e.get("date")]

meta = {
    "total_postings": len(raw),
    "date_from": min(dates),
    "date_to": max(dates)
}

with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

print(f"Saved: {meta}")