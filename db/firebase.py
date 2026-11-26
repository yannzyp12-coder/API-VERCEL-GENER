"""
Firebase Firestore CRUD
Collection: "accounts"
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

_initialized = False
_db          = None


def _get_db():
    global _initialized, _db
    if _initialized:
        return _db

    sa_json = os.environ.get("FIREBASE_SA")
    if sa_json:
        sa_dict = json.loads(sa_json)
        cred    = credentials.Certificate(sa_dict)
    elif os.path.exists("firebase_sa.json"):
        cred = credentials.Certificate("firebase_sa.json")
    else:
        raise RuntimeError(
            "Firebase SA tidak ditemukan. "
            "Set env var FIREBASE_SA atau taruh firebase_sa.json di root."
        )

    firebase_admin.initialize_app(cred)
    _db          = firestore.client()
    _initialized = True
    return _db


def save_account(account: dict) -> str:
    """
    Upsert satu akun ke Firestore.
    Doc ID = account_id.
    Return: doc_id
    """
    db  = _get_db()
    doc_id = account.get("account_id", account.get("uid", "unknown"))
    # Strip internal keys
    clean = {k: v for k, v in account.items() if not k.startswith("_")}
    db.collection("accounts").document(doc_id).set(clean)
    return doc_id


def get_account(account_id: str) -> dict | None:
    db  = _get_db()
    doc = db.collection("accounts").document(account_id).get()
    return doc.to_dict() if doc.exists else None


def list_accounts(region: str = None, limit: int = 50) -> list:
    db    = _get_db()
    query = db.collection("accounts")
    if region:
        query = query.where("region", "==", region.upper())
    query = (
        query
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    return [d.to_dict() for d in query.stream()]


def delete_account(account_id: str) -> bool:
    db = _get_db()
    db.collection("accounts").document(account_id).delete()
    return True
