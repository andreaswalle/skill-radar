import json
import re
import os
from html.parser import HTMLParser

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self):
        return ' '.join(self.text_parts)

def bereinige_text(text):
    text = re.sub(r'&#x27;', "'", text)
    text = re.sub(r'&#x2F;', '/', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    extractor = HTMLTextExtractor()
    extractor.feed(text)
    text = extractor.get_text()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

if __name__ == "__main__":
    with open("data/raw/hn_jobs.json", encoding="utf-8") as f:
        jobs = json.load(f)

    for job in jobs:
        job["text_clean"] = bereinige_text(job["text"])

    print(f"Bereinigt: {len(jobs)} Einträge")

    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/hn_jobs_clean.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print("Gespeichert: data/raw/hn_jobs_clean.json")