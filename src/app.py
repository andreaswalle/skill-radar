import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

st.title("SkillRadar - HN Job Market Analysis")
st.caption("Based on 1,517 job postings from HackerNews 'Who is Hiring' (Jan 2024 – May 2026)")

with open("data/processed/skill_frequency.json", encoding="utf-8") as f:
    skill_counts = json.load(f)

with open("data/processed/skill_trends.json", encoding="utf-8") as f:
    by_month = json.load(f)

st.header("Top 20 (2024-2026)")
top20 = skill_counts[:20]
skills = [item[0] for item in top20]
counts = [item[1] for item in top20]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(skills[::-1], counts[::-1], color="skyblue")
ax.set_xlabel("Mentions")
st.pyplot(fig)

st.header("Skills Over Time")

df = pd.DataFrame(by_month).fillna(0).T
df.index = pd.to_datetime(df.index)
df = df.sort_index()

all_skills = [item[0] for item in skill_counts[:30]]
selected = st.sidebar.multiselect("Select skills to display", all_skills, default=all_skills[:5])

fig2, ax2 = plt.subplots(figsize=(12, 5))
for skill in selected:
    if skill in df.columns:
        ax2.plot(df.index, df[skill], marker="o", label=skill)

ax2.set_xlabel("Month")
ax2.set_ylabel("Mentions")
ax2.legend()
st.pyplot(fig2)