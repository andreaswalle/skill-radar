# SkillRadar – Inbox & Backlog

Unstrukturierte Ideen, offene Fragen und nächste Schritte für das Projekt.

---

## Projektideen & Features

### Hoch priorisiert
- [ ] Scraper für HackerNews „Who is Hiring"-Threads (monatlich, öffentliche API)
- [ ] Regelbasierte Skill-Extraktion mit einer kuratierten Skill-Liste (Python, PyTorch, LangChain, MLOps, …)
- [ ] Skill-Ranking nach Häufigkeit, gruppiert nach Rolle (ML Engineer, Data Scientist, AI Researcher)
- [ ] Streamlit-Dashboard mit Balken-/Radardiagramm der Top-N-Skills

### Mittlere Priorität
- [ ] Trend-Ansicht: Skill-Häufigkeit über mehrere Monate hinweg
- [ ] Exportfunktion (CSV, JSON) für Analyse-Ergebnisse
- [ ] Filterung nach Region (Remote, EU, US)
- [ ] E-Mail-/Slack-Digest mit monatlichem Skill-Report

### Ideen für später
- [ ] LLM-gestützte Skill-Extraktion (GPT/Claude) statt regelbasiert
- [ ] Vergleich: gefragte Skills vs. Skills auf LinkedIn-Profilen
- [ ] Interaktive Skill-Gap-Analyse (Was fehlt mir noch?)
- [ ] Öffentliche Web-App auf Streamlit Cloud oder Hugging Face Spaces

---

## Datenquellen

| Quelle | Typ | Zugang |
|--------|-----|--------|
| HackerNews „Ask HN: Who is Hiring?" | Monatliche Threads | Algolia HN API (kostenlos) |
| RemoteOK | KI/ML-Stellen | Öffentliche JSON-API |
| LinkedIn Jobs | Breit gefächert | Scraping (Terms prüfen!) |
| Indeed / Stepstone | Regional | Scraping (Terms prüfen!) |
| Arbeitnow.com | EU/Remote | Öffentliche API |

---

## Offene Fragen

- **NLP-Ansatz**: Regelbasiert (schnell, erklärbar) oder LLM-basiert (flexibler, teurer)?
- **Skill-Taxonomie**: Eigene Liste pflegen oder bestehende Ontologie nutzen (z. B. ESCO)?
- **Speicherformat**: CSV-Dateien reichen für Phase 1, oder gleich SQLite/DuckDB?
- **Update-Frequenz**: Einmalig manuell, monatlich per Cron-Job oder Echtzeit?
- **Deployment**: Lokal genug für MVP, oder direkt in die Cloud (Streamlit Cloud, HF Spaces)?

---

## Nächste Schritte (Phase 1)

1. `requirements.txt` füllen (pandas, requests, beautifulsoup4, spacy, streamlit, plotly)
2. `src/collector.py` – HackerNews-Scraper implementieren
3. `src/extractor.py` – Skill-Extraktion mit Keyword-Liste
4. `notebooks/01_eda.ipynb` – Erste Daten inspizieren und visualisieren
5. `src/app.py` – Minimales Streamlit-Dashboard mit Beispieldaten
