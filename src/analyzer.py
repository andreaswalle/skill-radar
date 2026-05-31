import json
from collections import defaultdict
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

BLACKLIST = {"Security", "monitoring"}

with open("data/processed/extracted_skills.json", encoding="utf-8") as f:
    jobs = json.load(f)

skill_counts = Counter()
for job in jobs:
    for category, skill in job["skills"]:
        if skill not in BLACKLIST:
            skill_counts[skill] += 1

by_month = defaultdict(lambda: defaultdict(int))
for job in jobs:
    month = job["date"][:7]
    for category, skill in job["skills"]:
        by_month[month][skill] += 1

with open("data/processed/skill_frequency.json", "w") as f:
    json.dump(skill_counts.most_common(), f, indent=2)
with open("data/processed/skill_trends.json", "w") as f:
    json.dump(by_month, f, indent=2)
with open("data/processed/skill_frequency.json") as f:
    skill_counts = json.load(f)

top20 = skill_counts[:20]
skills = [item[0] for item in top20]
counts = [item[1] for item in top20]

plt.figure(figsize=(12, 6))
plt.barh(skills[::-1], counts[::-1], color="skyblue")
plt.xlabel("Mentions")
plt.title("Top 20 Skills in HN Who's Hiring (2024-2025)")
plt.tight_layout()
plt.savefig("data/processed/top20_skills.png", dpi=150)
plt.show()

jobs_per_month = defaultdict(int)
for job in jobs:
    month = job["date"][:7]
    jobs_per_month[month] += 1

by_month_norm = {}
for month, skills in by_month.items():
    total = jobs_per_month[month]
    by_month_norm[month] = {skill: count / total for skill, count in skills.items()}

with open("data/processed/skill_trends.json", encoding="utf-8") as f:
    by_month = json.load(f)

df = pd.DataFrame(by_month_norm).fillna(0).T
df.index = pd.to_datetime(df.index)
df = df.sort_index()

top_skills = [item[0] for item in skill_counts[:10] if item[0] not in BLACKLIST]

plt.figure(figsize=(14, 7))
for skill in top_skills:
    if skill in df.columns:
        plt.plot(df.index, df[skill], marker="o", label=skill)

plt.title("Top Skills Over Time (HN Who's Hiring)")
plt.xlabel("Month")
plt.ylabel("Mentions")
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("data/processed/skill_trends.png", dpi=150)
plt.show()