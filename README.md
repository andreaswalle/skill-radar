# SkillRadar

Automated extraction and analysis of in-demand skills from AI job postings.

## What it does

SkillRadar processes job postings and extracts the skills employers actually ask for — ranked by frequency, grouped by role, and visualized for clarity.

## Why it exists

The AI job market moves fast. This tool makes the signal visible.

## Stack

- Python · Pandas · Requests
- NLP (in progress)
- Streamlit (dashboard)
- Data: HackerNews "Who is Hiring" — live via API

## Status

- ✅ Phase 1: EDA on manual data, skill extraction, visualization
- ✅ Phase 2: HackerNews API integration, automated collection (1,517 job postings, 31 threads)
- 🔧 Phase 3: NLP extraction, Streamlit dashboard, deployment