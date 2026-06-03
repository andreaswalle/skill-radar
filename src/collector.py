import requests
import json
import time
import os

from datetime import datetime, timezone

BASE_URL = "https://hn.algolia.com/api/v1"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "hn_jobs.json")


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

def fetch_all_thread_ids(from_date="2024-01-01", to_date=None):
    """Fetch all 'Who is Hiring' thread IDs within a date range."""
    url = "https://hacker-news.firebaseio.com/v0/user/whoishiring.json"
    res = requests.get(url)
    submitted = res.json().get("submitted", [])

    from_dt = datetime.fromisoformat(from_date).replace(tzinfo=timezone.utc)
    to_dt = datetime.now(timezone.utc) if to_date is None else datetime.fromisoformat(to_date).replace(tzinfo=timezone.utc)

    thread_ids = []
    for story_id in submitted:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()
        title = story.get("title", "")
        timestamp = story.get("time", 0)
        posted = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        if posted < from_dt:
            break  # No need to check older stories
        
        if "hiring" in title.lower() and from_dt <= posted <= to_dt:
            thread_ids.append(str(story_id))
            print(f"  Found: {title} ({posted.strftime('%Y-%m')})")
        
        time.sleep(0.1)

    return thread_ids

    thread_ids = []
    for hit in hits:
        title = hit.get("title", "")
        created_at = hit.get("created_at", "")
        if "hiring" in title.lower():
            created_date = datetime.fromisoformat(created_at[:-1])
            if from_date <= created_date.strftime("%Y-%m-%d") <= (to_date or datetime.now().strftime("%Y-%m-%d")):
                thread_ids.append(str(hit["objectID"]))
                print(f"  Found: {title} ({created_at})")
        time.sleep(0.1)

    return thread_ids

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
    print("Fetching thread IDs (2024-01-01 to now)...")
    thread_ids = fetch_all_thread_ids(from_date="2024-01-01")
    print(f"Total threads found: {len(thread_ids)}")

    existing = load_existing(DATA_PATH)
    print(f"Existing entries: {len(existing)}")

    new_entries = collect_from_ids(thread_ids, max_per_thread=100)
    print(f"\nNewly collected: {len(new_entries)} postings")

    total, added = merge_unique(existing, new_entries)
    print(f"New entries added: {added}")
    print(f"Total after merge: {len(total)}")

    # Save
    save(total, DATA_PATH)
    print(f"Saved: {DATA_PATH}")
