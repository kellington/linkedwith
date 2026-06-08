"""Connections.csv parser with preamble skip, BOM handling, and URL normalization.

Handles known LinkedIn CSV format quirks:
- UTF-8 BOM at file start (via open_csv_in_zip with utf-8-sig encoding)
- 3 preamble lines before the real header (dynamic detection by scanning for 'First Name')
- LinkedIn date format '15 Jan 2023' (not ISO 8601)
- Missing profile URL records are skipped with a warning to stderr (D-06)
"""
import csv
import sys
from datetime import datetime

from lib.extractor import open_csv_in_zip
from lib.normalizer import normalize_linkedin_url


def parse_connections(zf, csv_name: str) -> dict:
    """Parse Connections.csv from an open ZIP into a store dict keyed by normalized URL.

    Handles UTF-8 BOM (via open_csv_in_zip), dynamic preamble skip (scan for
    'First Name'), LinkedIn date format ('%d %b %Y' -> ISO 8601), and
    missing URL skip (D-06 — records without a URL cannot be joined to anything).

    Args:
        zf: Open zipfile.ZipFile object.
        csv_name: Exact name of the CSV within the ZIP (from find_csv_in_zip).

    Returns:
        Dict keyed by normalized profile URL, each value a connection record dict.

    Raises:
        ValueError: If no header row containing 'First Name' is found.
    """
    store = {}
    text = open_csv_in_zip(zf, csv_name)

    # Dynamic preamble detection per PARSE-03: scan lines until we find the header.
    # LinkedIn exports include 3 preamble lines ("Notes:", blank, blank) before the
    # real header. Dynamic detection is robust to preamble length changes.
    header_line = None
    for line in text:
        if "First Name" in line:
            header_line = line
            break

    if header_line is None:
        raise ValueError(
            "Connections.csv has no recognizable header row containing 'First Name'"
        )

    # Parse the header line to get fieldnames, then use DictReader on remaining lines.
    fieldnames = next(csv.reader([header_line]))
    reader = csv.DictReader(text, fieldnames=fieldnames)

    for row in reader:
        url_raw = row.get("URL", "").strip()
        norm_url = normalize_linkedin_url(url_raw)

        if not norm_url:
            # D-06: skip records with no URL, warn to stderr so user is informed
            first = row.get("First Name", "").strip()
            last = row.get("Last Name", "").strip()
            print(
                f"WARNING: skipping record with no URL: {first} {last}",
                file=sys.stderr,
                flush=True,
            )
            continue

        # D-07: records with other missing fields are kept (those fields are nullable)
        connected_on_raw = row.get("Connected On", "").strip()
        try:
            # LinkedIn uses '15 Jan 2023' format — not ISO 8601
            connected_on = datetime.strptime(connected_on_raw, "%d %b %Y").strftime(
                "%Y-%m-%d"
            )
        except ValueError:
            connected_on = None

        store[norm_url] = {
            "first_name": row.get("First Name", "").strip(),
            "last_name": row.get("Last Name", "").strip(),
            "url": url_raw,
            "email": row.get("Email Address", "").strip(),
            "company": row.get("Company", "").strip(),
            "position": row.get("Position", "").strip(),
            "connected_on": connected_on,
            "_meta": {"source": "linkedin_export"},
        }

    return store
