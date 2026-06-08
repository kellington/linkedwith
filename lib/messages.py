"""Messages.csv parser returning {normalized_url: iso_date} dict.

Provides the most recent message date per sender by scanning all rows.
Messages.csv has NO preamble — the header is on line 1 (verified against real export).

Key verified facts about messages.csv:
- Column names are ALL CAPS: SENDER PROFILE URL, DATE
- DATE format: "2026-02-13 00:23:08 UTC" — strip " UTC", parse with %Y-%m-%d %H:%M:%S
- "LinkedIn Member" rows have empty SENDER PROFILE URL — skip silently (not a warning)
- Both direct and group messages handled: SENDER PROFILE URL is the sole join key
- File is named "messages.csv" (lowercase) in real exports — find_csv_in_zip handles this
"""
import csv
import sys
import zipfile
from datetime import datetime

from lib.extractor import open_csv_in_zip
from lib.normalizer import normalize_linkedin_url


def parse_messages(zf: zipfile.ZipFile, csv_name: str) -> dict:
    """Return {normalized_url: iso_date} with the most recent message date per sender.

    Scans every row in messages.csv. For each row with a non-empty SENDER PROFILE URL,
    normalizes the URL and tracks the maximum date seen per normalized URL.

    Args:
        zf: Open zipfile.ZipFile object.
        csv_name: Exact name of the CSV within the ZIP (from find_csv_in_zip).

    Returns:
        Dict mapping normalized LinkedIn profile URL to ISO date string ("YYYY-MM-DD").
        Senders with no messages are absent from the dict (not keyed with None).
    """
    most_recent: dict[str, str] = {}
    text = open_csv_in_zip(zf, csv_name)
    reader = csv.DictReader(text)

    for row in reader:
        sender_url_raw = row.get("SENDER PROFILE URL", "").strip()
        date_raw = row.get("DATE", "").strip()

        if not sender_url_raw:
            # LinkedIn Member rows (deleted/anonymous accounts) have empty SENDER PROFILE URL
            # Skip silently — these are known LinkedIn export behavior, not an error
            continue

        if not date_raw:
            continue

        norm_url = normalize_linkedin_url(sender_url_raw)
        if not norm_url:
            continue

        # DATE format: "2026-02-13 00:23:08 UTC" — strip " UTC" suffix, then parse
        date_str = date_raw.replace(" UTC", "")
        try:
            iso_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date().isoformat()
        except ValueError:
            print(
                f"WARNING: could not parse message date: {date_raw!r}",
                file=sys.stderr,
                flush=True,
            )
            continue

        # ISO 8601 dates sort lexicographically == chronologically
        # "2026-01-15" > "2025-12-01" is True, so string comparison is correct
        if norm_url not in most_recent or iso_date > most_recent[norm_url]:
            most_recent[norm_url] = iso_date

    return most_recent


def apply_message_dates(store: dict, message_dates: dict) -> dict:
    """Update most_recent_message field on store records.

    Sets most_recent_message to None for connections with no messages.
    Only updates connections already in the store — unknown senders are ignored.

    Args:
        store: Connection store dict (modified in place).
        message_dates: Dict from parse_messages: {normalized_url: iso_date}.

    Returns:
        The updated store dict.
    """
    for key in store:
        store[key].setdefault("most_recent_message", None)
    for norm_url, iso_date in message_dates.items():
        if norm_url in store:
            store[norm_url]["most_recent_message"] = iso_date
    return store
