import spacy
import json
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from spacy.matcher import PhraseMatcher

# --- Phase B: Skill Taxonomy (filled AFTER discovery) ---
SKILLS = {
    "languages": ["Python", "TypeScript", "JavaScript", "Rust", "Ruby", "Java", "Go", "C++", "SQL"],
    "frameworks": ["React", "Node.js", "Next.js", "Django", "FastAPI", "Rails", "GraphQL", "Vue.js", "NestJS", "React Native", "Redux", "Tailwind"],
    "cloud": ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "Linux", "Prometheus", "Grafana", "Datadog"],
    "databases": ["PostgreSQL", "MySQL", "Snowflake", "Redis", "Kafka"],
    "ai_ml": ["LLMs", "machine learning", "deep learning", "computer vision", "RAG", "generative AI", "AI agents", "PyTorch", "TensorFlow", "LangChain", "fine-tuning", "embeddings"],
    "devops": ["CI/CD", "DevOps", "Git", "GitHub", "SRE"],
    "concepts": ["distributed systems", "observability", "monitoring", "data pipelines", "data science", "scalability", "security"],
    "mobile": ["Android", "React Native"],
    "platforms": ["OpenAI", "Anthropic", "Hugging Face", "Pinecone", "Weaviate", "ChromaDB", "Weights & Biases", "Vertex AI", "Bedrock"],
}

ALIASES = {
    "k8s": "Kubernetes",
    "ReactJS": "React",
    "React.js": "React",
    "nodejs": "Node.js",
    "node": "Node.js",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "react/next.js": "Next.js",
    "react/typescript": "React",
    "golang": "Go",
    "llm": "LLMs",
    "ml": "machine learning",
    "genai": "generative AI",
    "gen ai": "generative AI",
}


# === PHASE A: DISCOVERY ===

def extract_noun_phrases(texts, nlp):
    phrases = []
    for text in texts:
        doc = nlp(text)
        for chunk in doc.noun_chunks:
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

    vectorizer = CountVectorizer(ngram_range=(1, 3), max_features=100, stop_words="english")
    vectorizer.fit(texts)
    ngram_counts = zip(vectorizer.get_feature_names_out(), vectorizer.transform(texts).toarray().sum(axis=0))
    ngram_sorted = sorted(ngram_counts, key=lambda x: x[1], reverse=True)[:50]

    with open("data/processed/discovery_output.txt", "w") as f:
        f.write("=== NOUN PHRASES (Top 500) ===\n\n")
        for phrase, count in counter.most_common(500):
            f.write(f"{count:4d}  {phrase}\n")
        f.write("\n=== N-GRAMS (Top 50) ===\n\n")
        for term, count in ngram_sorted:
            f.write(f"{int(count):4d}  {term}\n")

    print("Saved: data/processed/discovery_output.txt")


# === PHASE B: EXTRACTION ===

def build_matcher(nlp, skills):
    """Build a PhraseMatcher for the given skills."""
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for category, skill_list in skills.items():
        patterns = [nlp.make_doc(skill) for skill in skill_list]
        matcher.add(category, patterns)
    return matcher


def extract_skills(text, nlp, matcher):
    """Extract skills from text using the matcher."""
    doc = nlp(text)
    matches = matcher(doc)
    found_skills = set()
    for match_id, start, end in matches:
        category = nlp.vocab.strings[match_id]
        skill = doc[start:end].text
        # apply alias mapping
        skill_normalized = ALIASES.get(skill.lower(), skill)
        found_skills.add((category, skill_normalized))
    return found_skills


def extract_all(jobs):
    """Run extraction on all job postings."""
    nlp = spacy.load("en_core_web_sm")
    matcher = build_matcher(nlp, SKILLS)
    for job in jobs:
        job["skills"] = extract_skills(job["text_clean"], nlp, matcher)
    return jobs


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