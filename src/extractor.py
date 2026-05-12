import spacy
import json
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer

# --- Phase B: Skill Taxonomy (filled AFTER discovery) ---
SKILLS = {
    "languages": [],
    "frameworks": [],
    "cloud": [],
    "ai_ml": [],
}

ALIASES = {
    "k8s": "Kubernetes",
    "ReactJS": "React",
    # ... add more after discovery
}


# === PHASE A: DISCOVERY ===

def extract_noun_phrases(texts, nlp):
    phrases = []
    for text in texts:
        doc = nlp(text)
        for chunk in doc.noun_chunks:
            if not all(token.is_stop for token in chunk):
                phrases.append(chunk.text.lower())
            if len(chunk.text) > 2 and not all(token.is_stop for token in chunk):
                phrases.append(chunk.text.lower())
    return phrases


def top_ngrams(texts, n=2, top_k=100):
    """Find most frequent n-grams across all texts."""
    # use CountVectorizer with ngram_range=(1, n)
    # fit on texts
    # return top_k most frequent
    pass


def discover(jobs):
    nlp = spacy.load("en_core_web_sm")
    texts = [job["text_clean"] for job in jobs]
    phrases = extract_noun_phrases(texts, nlp)
    counter = Counter(phrases)
    for phrase, count in counter.most_common(50):
        print(f"{count:4d}  {phrase}")


# === PHASE B: EXTRACTION ===

def build_matcher(nlp, skills):
    """Build a PhraseMatcher from the skill taxonomy."""
    pass


def extract_skills(text, nlp, matcher):
    """Extract and normalize skills from a single text."""
    pass


def extract_all(jobs):
    """Run extraction on all job postings."""
    pass


if __name__ == "__main__":
    with open("data/raw/hn_jobs_clean.json", encoding="utf-8") as f:
        jobs = json.load(f)

    # --- Toggle: run discovery OR extraction ---
    MODE = "discover"   # switch to "extract" once SKILLS is filled

    if MODE == "discover":
        discover(jobs)
    else:
        results = extract_all(jobs)
        # save to data/processed/hn_jobs_skills.json