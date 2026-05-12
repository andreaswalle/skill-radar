import requests
import json
import time
import os

from datetime import datetime, timezone

BASE_URL = "https://hn.algolia.com/api/v1"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "hn_jobs.json")


# --- Deduplication ---

def load_existing(path):
    """Load existing data from disk, or return an empty list."""
    path = os.path.normpath(path)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def merge_unique(existing, new_entries):
    """Merge new entries into existing data, skipping duplicates.

    Key: (thread_id, author) — each author posts at most one
    job listing per thread.
    """
    known_keys = {(e["thread_id"], e["author"]) for e in existing}
    added = 0

    for entry in new_entries:
        key = (entry["thread_id"], entry["author"])
        if key not in known_keys:
            existing.append(entry)
            known_keys.add(key)
            added += 1

    return existing, added


def save(data, path):
    """Save data as JSON."""
    path = os.path.normpath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --- API access ---

def fetch_hiring_threads(count=3, max_age_days=180):
    """Fetch recent 'Who is Hiring' threads from HackerNews."""
    url = "https://hacker-news.firebaseio.com/v0/user/whoishiring.json"
    res = requests.get(url)
    data = res.json()
    submitted = data.get("submitted", [])

    threads = []
    for story_id in submitted[:50]:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()
        title = story.get("title", "")
        timestamp = story.get("time", 0)
        if "hiring" in title.lower():
            posted = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            if (now - posted).days < max_age_days:
                threads.append((str(story_id), title))
                print(f"  Found: {title}")
        time.sleep(0.1)
        if len(threads) >= count:
            break

    return threads


def fetch_job_postings(thread_id, max_posts=100):
    """Fetch top-level comments (= job postings) from a thread."""
    url = f"{BASE_URL}/search?tags=comment,story_{thread_id}&hitsPerPage={max_posts}"
    res = requests.get(url)
    hits = res.json()["hits"]

    postings = []
    for hit in hits:
        text = hit.get("comment_text", "")
        parent_id = hit.get("parent_id")
        story_id = hit.get("story_id")

        if text and len(text) > 100 and parent_id == story_id:
            postings.append({
                "thread_id": thread_id,
                "text": text,
                "author": hit.get("author", ""),
                "date": hit.get("created_at", "")
            })
        time.sleep(0.05)

    return postings


# --- Collection ---

def collect(num_threads=3, max_per_thread=100):
    """Collect job postings from the latest hiring threads."""
    print("Fetching hiring threads...")
    threads = fetch_hiring_threads(num_threads)

    all_postings = []
    for thread_id, title in threads:
        print(f"  → {title}")
        postings = fetch_job_postings(thread_id, max_per_thread)
        all_postings.extend(postings)
        print(f"     {len(postings)} postings found")
        time.sleep(1)

    return all_postings


def collect_from_ids(thread_ids, max_per_thread=100):
    """Collect job postings from a list of thread IDs."""
    all_postings = []
    for thread_id in thread_ids:
        print(f"  → Thread {thread_id}")
        postings = fetch_job_postings(thread_id, max_per_thread)
        all_postings.extend(postings)
        print(f"     {len(postings)} postings found")
        time.sleep(1)
    return all_postings


if __name__ == "__main__":
    thread_ids = ['40224213', '40846428', '42919502', '41425910', '39217310',
                  '38842977', '45800465', '40563283', '43243024', '42297424',
                  '41129813', '42017580', '39894820', '44159528', '39562986',
                  '41709301', '46466074', '42575537', '46857488', '46108941',
                  '47975571', '47601859', '43547611', '44434576', '45093192',
                  '43858554', '47219668', '45438503', '44757794', '39886586', '40548216']

    # Load existing data
    existing = load_existing(DATA_PATH)
    print(f"Existing entries: {len(existing)}")

    # Collect new data
    new_entries = collect_from_ids(thread_ids, max_per_thread=100)
    print(f"\nNewly collected: {len(new_entries)} postings")

    # Merge and deduplicate
    total, added = merge_unique(existing, new_entries)
    print(f"New entries added: {added}")
    print(f"Total after merge: {len(total)}")

    # Save
    save(total, DATA_PATH)
    print(f"Saved: {DATA_PATH}")
