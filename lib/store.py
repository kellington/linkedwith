"""JSON flat-file store: load, save (atomic), and merge connection records.

Store is a dict keyed by normalized LinkedIn profile URL (D-01).
Atomic write via .tmp rename prevents half-written stores (D-10, D-11).
"""
import json
import os
from pathlib import Path

# LinkedIn-sourced fields that get overwritten on re-import.
# Fields NOT in this set (e.g. user_phone, user_notes, user_email) are preserved.
LINKEDIN_FIELDS = {
    "first_name",
    "last_name",
    "url",
    "email",
    "company",
    "position",
    "connected_on",
    "most_recent_message",
    "_meta",
}


def load_store(path: Path) -> dict:
    """Load JSON store from path. Returns empty dict if file does not exist."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_store(store: dict, path: Path) -> None:
    """Write store to path atomically via a .tmp file rename.

    Prevents corrupt stores if the process is interrupted mid-write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def merge_connections(existing: dict, new_records: dict) -> dict:
    """Upsert LinkedIn fields from new_records into existing store.

    For existing keys: only fields in LINKEDIN_FIELDS are updated.
    User-provided fields (user_phone, user_notes, user_email, etc.) are never touched.
    For new keys: the entire record is inserted.

    Args:
        existing: Current store dict (modified in place and returned).
        new_records: Dict keyed by normalized URL with LinkedIn-sourced record data.

    Returns:
        The updated existing dict (same object, modified in place).
    """
    for key, record in new_records.items():
        if key in existing:
            for field in LINKEDIN_FIELDS:
                if field in record:
                    existing[key][field] = record[field]
        else:
            existing[key] = record
    return existing
