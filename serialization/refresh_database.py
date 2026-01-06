import json
from pathlib import Path
from typing import Iterable, Mapping, Optional

import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = Path(__file__).resolve().parent

# Fetch the service account key JSON file contents
cred = credentials.Certificate('mrewards-3156b-firebase-adminsdk-fbsvc-2ede6e1e0a.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()


def _load_json(filename: str) -> Iterable[Mapping]:
    path = BASE_DIR / filename
    return json.loads(path.read_text(encoding='utf-8'))


def _clear_collection(collection: str, batch_size: int = 500) -> int:
    """Remove all documents in the given collection. For large collections, consider pagination limits."""
    total = 0
    docs = list(db.collection(collection).limit(batch_size).stream())
    while docs:
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
            total += 1
        batch.commit()
        docs = list(db.collection(collection).limit(batch_size).stream())
    return total


def _upsert_collection(collection: str, records: Iterable[Mapping]) -> int:
    count = 0
    for record in records:
        doc_id: Optional[str] = record.get("id") or record.get("slug")
        if not doc_id:
            continue
        db.collection(collection).document(doc_id).set(record)
        count += 1
    return count


def refresh_cards():
    records = _load_json("cards.json")
    removed = _clear_collection("cards")
    total = _upsert_collection("cards", records)
    print(f"cards refreshed: {total} docs (cleared {removed}).")


def refresh_card_faces():
    records = _load_json("card_faces.json")
    removed = _clear_collection("card_faces")
    total = _upsert_collection("card_faces", records)
    print(f"card_faces refreshed: {total} docs (cleared {removed}).")


def refresh_issuers():
    records = _load_json("issuers.json")
    removed = _clear_collection("issuers")
    total = _upsert_collection("issuers", records)
    print(f"issuers refreshed: {total} docs (cleared {removed}).")


if __name__ == "__main__":
    refresh_issuers()
    refresh_cards()
    refresh_card_faces()
