"""contact_info.csv parser with URL-primary and name-fallback matching.

Merges user-supplied contact data (email, phone, notes) into the JSON store.
Implements decisions D-01 through D-09 from CONTEXT.md.

contact_info.csv format: URL, First Name, Last Name, Email, Phone, Notes
- All columns are optional per-row
- URL present (D-04): used exclusively; First+Last Name ignored
- URL absent (D-05): fall back to case-insensitive First+Last Name match
- Blank CSV cells never overwrite existing user fields (anti-pattern #5 in RESEARCH.md)
"""
import csv
import sys

from lib.normalizer import normalize_linkedin_url


def merge_contact_info(store: dict, contact_info_path) -> dict:
    """Merge user-supplied contact data from contact_info.csv into store.

    contact_info.csv columns: URL, First Name, Last Name, Email, Phone, Notes
    URL match: normalize_linkedin_url() applied to CSV URL value (D-04).
    Name fallback: case-insensitive first+last match; skip with warning on 0 or 2+ matches (D-05).
    Updates user_email, user_phone, user_notes. Does not touch LinkedIn-sourced fields.
    Blank CSV cells are not applied — existing store values are preserved.

    Args:
        store: The store dict keyed by normalized LinkedIn profile URL (modified in place).
        contact_info_path: Path to the contact_info.csv file (not inside the ZIP).

    Returns:
        The updated store dict (same object, modified in place).
    """
    with open(contact_info_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for row in reader:
            # Guard against None from row.get() when column is absent from CSV (Pitfall 5)
            url_raw = (row.get("URL", "") or "").strip()
            first = (row.get("First Name", "") or "").strip()
            last = (row.get("Last Name", "") or "").strip()

            if url_raw:
                # D-04: URL present — use exclusively, ignore name columns
                norm_url = normalize_linkedin_url(url_raw)
                if norm_url not in store:
                    print(
                        f"WARNING: URL {norm_url!r} not found in store. Skipped.",
                        file=sys.stderr,
                        flush=True,
                    )
                    continue
                match_key = norm_url
            else:
                # D-05: Name fallback
                match_key = _find_by_name(store, first, last)
                if match_key is None:
                    continue  # warning already printed by _find_by_name

            # Apply user fields ONLY if CSV cell is non-empty (anti-pattern: blank overwrites)
            # D-01: user-editable fields are user_email, user_phone, user_notes
            email = (row.get("Email", "") or "").strip()
            phone = (row.get("Phone", "") or "").strip()
            notes = (row.get("Notes", "") or "").strip()

            if email:
                store[match_key]["user_email"] = email
            if phone:
                store[match_key]["user_phone"] = phone
            if notes:
                store[match_key]["user_notes"] = notes

    return store


def _find_by_name(store: dict, first: str, last: str) -> str | None:
    """Find store key by case-insensitive First+Last match.

    D-06: case-insensitive match.
    D-07/D-08: 2+ matches -> warn with count, URLs, companies, "re-submit with URL to resolve", return None.
    D-09: 0 matches -> warn "no connection found for '{first} {last}'. Skipped.", return None.

    Args:
        store: The store dict keyed by normalized LinkedIn profile URL.
        first: First name from contact_info.csv row.
        last: Last name from contact_info.csv row.

    Returns:
        Matching store key (normalized URL string) or None.
    """
    target = f"{first} {last}".lower().strip()
    matches = [
        key
        for key, rec in store.items()
        if f"{rec.get('first_name', '')} {rec.get('last_name', '')}".lower().strip() == target
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) == 0:
        # D-09: no connection found
        print(
            f"WARNING: no connection found for '{first} {last}'. Skipped.",
            file=sys.stderr,
            flush=True,
        )
        return None

    # D-07, D-08: ambiguous — multiple connections share the same name
    details = ", ".join(
        f"{key} ({store[key].get('company', 'unknown company')})"
        for key in matches
    )
    print(
        f"WARNING: {len(matches)} connections match '{first} {last}': {details}. "
        f"Skipped -- re-submit with URL to resolve.",
        file=sys.stderr,
        flush=True,
    )
    return None
