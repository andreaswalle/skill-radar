import requests
import json
import time
import os

BASE_URL = "https://hn.algolia.com/api/v1"

def hole_hiring_threads(anzahl=3):
    url = f"{BASE_URL}/search?query=Ask+HN+Who+is+Hiring&tags=story&hitsPerPage={anzahl}"
    res = requests.get(url)
    hits = res.json()["hits"]
    return [(h["objectID"], h["title"]) for h in hits]

def hole_stellenanzeigen(thread_id, max_anzeigen=100):
    url = f"{BASE_URL}/search?tags=comment,story_{thread_id}&hitsPerPage={max_anzeigen}"
    res = requests.get(url)
    hits = res.json()["hits"]
    
    anzeigen = []
    for hit in hits:
        text = hit.get("comment_text", "")
        if text and len(text) > 100:
            anzeigen.append({
                "thread_id": thread_id,
                "text": text,
                "autor": hit.get("author", ""),
                "datum": hit.get("created_at", "")
            })
        time.sleep(0.05)
    
    return anzeigen

def sammle_daten(anzahl_threads=3, max_pro_thread=100):
    print("Hole Hiring-Threads...")
    threads = hole_hiring_threads(anzahl_threads)
    
    alle_anzeigen = []
    for thread_id, titel in threads:
        print(f"  → {titel}")
        anzeigen = hole_stellenanzeigen(thread_id, max_pro_thread)
        alle_anzeigen.extend(anzeigen)
        print(f"     {len(anzeigen)} Anzeigen gefunden")
        time.sleep(1)
    
    return alle_anzeigen

if __name__ == "__main__":
    daten = sammle_daten(anzahl_threads=2, max_pro_thread=50)
    print(f"\nGesamt: {len(daten)} Stellenanzeigen")
    
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/hn_jobs.json", "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)
    print("Gespeichert: data/raw/hn_jobs.json")