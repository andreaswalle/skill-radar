import requests
import json
import time
import os

from datetime import datetime, timezone

BASE_URL = "https://hn.algolia.com/api/v1"
DATEN_PFAD = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "hn_jobs.json")


# --- Deduplizierung ---

def lade_bestehende(pfad):
    """Lädt bestehende Daten oder gibt leere Liste zurück."""
    pfad = os.path.normpath(pfad)
    if not os.path.exists(pfad):
        return []
    with open(pfad, encoding="utf-8") as f:
        return json.load(f)


def dedupliziere(bestehende, neue):
    """Merged neue Einträge in bestehende, ohne Duplikate.

    Schlüssel: (thread_id, autor) — jeder Autor postet pro Thread
    maximal eine Stellenanzeige.
    """
    bekannte = {(e["thread_id"], e["autor"]) for e in bestehende}
    hinzugefuegt = 0

    for eintrag in neue:
        schluessel = (eintrag["thread_id"], eintrag["autor"])
        if schluessel not in bekannte:
            bestehende.append(eintrag)
            bekannte.add(schluessel)
            hinzugefuegt += 1

    return bestehende, hinzugefuegt


def speichere(daten, pfad):
    """Speichert Daten als JSON."""
    pfad = os.path.normpath(pfad)
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)


# --- API-Zugriffe ---

def hole_hiring_threads(anzahl=3, max_alter_tage=180):
    """Holt aktuelle 'Who is Hiring'-Threads von HackerNews."""
    url = "https://hacker-news.firebaseio.com/v0/user/whoishiring.json"
    res = requests.get(url)
    daten = res.json()
    submitted = daten.get("submitted", [])

    threads = []
    for story_id in submitted[:50]:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()
        titel = story.get("title", "")
        datum = story.get("time", 0)
        if "hiring" in titel.lower():
            datum_dt = datetime.fromtimestamp(datum, tz=timezone.utc)
            jetzt = datetime.now(timezone.utc)
            if (jetzt - datum_dt).days < max_alter_tage:
                threads.append((str(story_id), titel))
                print(f"  Gefunden: {titel}")
        time.sleep(0.1)
        if len(threads) >= anzahl:
            break

    return threads


def hole_stellenanzeigen(thread_id, max_anzeigen=100):
    """Holt Top-Level-Kommentare (= Stellenanzeigen) aus einem Thread."""
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


# --- Sammel-Funktionen ---

def sammle_daten(anzahl_threads=3, max_pro_thread=100):
    """Sammelt Stellenanzeigen aus den neuesten Hiring-Threads."""
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


def sammle_von_ids(thread_ids, max_pro_thread=100):
    """Sammelt Stellenanzeigen aus einer Liste von Thread-IDs."""
    alle_anzeigen = []
    for thread_id in thread_ids:
        print(f"  → Thread {thread_id}")
        anzeigen = hole_stellenanzeigen(thread_id, max_pro_thread)
        alle_anzeigen.extend(anzeigen)
        print(f"     {len(anzeigen)} Anzeigen gefunden")
        time.sleep(1)
    return alle_anzeigen


if __name__ == "__main__":
    thread_ids = ['40224213', '40846428', '42919502', '41425910', '39217310',
                  '38842977', '45800465', '40563283', '43243024', '42297424',
                  '41129813', '42017580', '39894820', '44159528', '39562986',
                  '41709301', '46466074', '42575537', '46857488', '46108941',
                  '47975571', '47601859', '43547611', '44434576', '45093192',
                  '43858554', '47219668', '45438503', '44757794', '39886586', '40548216']

    # Bestehende Daten laden
    bestehende = lade_bestehende(DATEN_PFAD)
    print(f"Bestehende Einträge: {len(bestehende)}")

    # Neue Daten sammeln
    neue = sammle_von_ids(thread_ids, max_pro_thread=100)
    print(f"\nNeu gesammelt: {len(neue)} Stellenanzeigen")

    # Mergen und deduplizieren
    gesamt, hinzugefuegt = dedupliziere(bestehende, neue)
    print(f"Davon neu: {hinzugefuegt}")
    print(f"Gesamt nach Merge: {len(gesamt)}")

    # Speichern
    speichere(gesamt, DATEN_PFAD)
    print(f"Gespeichert: {DATEN_PFAD}")