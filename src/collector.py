import requests
import json
import time
import os

from datetime import datetime, timezone

def ist_aktuell(datum_str, max_monate=6):
    datum = datetime.fromisoformat(datum_str.replace("Z", "+00:00"))
    jetzt = datetime.now(timezone.utc)
    differenz = (jetzt - datum).days
    return differenz < (max_monate * 30)

BASE_URL = "https://hn.algolia.com/api/v1"

def hole_hiring_threads(anzahl=3):
    url = "https://hacker-news.firebaseio.com/v0/user/whoishiring.json"
    res = requests.get(url)
    daten = res.json()
    submitted = daten.get("submitted", [])
    
    threads = []
    for story_id in submitted[:20]:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()
        titel = story.get("title", "")
        datum = story.get("time", 0)
        if "hiring" in titel.lower():
            from datetime import datetime, timezone
            datum_dt = datetime.fromtimestamp(datum, tz=timezone.utc)
            jetzt = datetime.now(timezone.utc)
            if (jetzt - datum_dt).days < 180:
                threads.append((str(story_id), titel))
                print(f"Gefunden: {titel}")
        time.sleep(0.1)
        if len(threads) >= anzahl:
            break
    
    return threads

def hole_stellenanzeigen(thread_id, max_anzeigen=100):
    url = f"{BASE_URL}/search?tags=comment,story_{thread_id}&hitsPerPage={max_anzeigen}"
    res = requests.get(url)
    hits = res.json()["hits"]
    
    anzeigen = []
    for hit in hits:
        text = hit.get("comment_text", "")
        parent_id = hit.get("parent_id")
        story_id = hit.get("story_id")
        
        if text and len(text) > 100 and parent_id == story_id:
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