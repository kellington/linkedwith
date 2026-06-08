#!/usr/bin/env python3
"""LinkedWith: Parse LinkedIn data export into enriched contact list."""

import argparse
import re
import sys
import zipfile
from pathlib import Path

from lib.config import CONTACT_INFO_PATH, HTML_OUTPUT_PATH, STORE_PATH
from lib.contacts import merge_contact_info
from lib.extractor import find_csv_in_zip
from lib.messages import apply_message_dates, parse_messages
from lib.parsers import parse_connections
from lib.renderer import render_html
from lib.store import load_store, merge_connections, save_store


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse LinkedIn data export ZIP into a JSON contact store."
    )
    parser.add_argument("zip_path", help="Path to LinkedIn data export ZIP file")
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    if not zip_path.exists():
        print(f"ERROR: File not found: {zip_path}", file=sys.stderr)
        return 1

    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        print(f"ERROR: Not a valid ZIP file: {zip_path}", file=sys.stderr)
        return 1

    with zf:
        # PARSE-01: find Connections.csv (D-08: exit if not found)
        csv_name = find_csv_in_zip(zf, "Connections.csv")
        if csv_name is None:
            print("ERROR: Connections.csv not found in ZIP.", file=sys.stderr)
            return 1

        # PARSE-02, PARSE-03, PARSE-04, PARSE-05: parse with BOM handling, preamble skip, URL normalization
        new_records = parse_connections(zf, csv_name)

        # MSG-01: find Messages.csv (non-fatal if absent)
        msg_csv_name = find_csv_in_zip(zf, "Messages.csv")
        if msg_csv_name is None:
            print(
                "WARNING: messages.csv not found in ZIP — skipping message dates",
                file=sys.stderr,
            )
            message_dates = {}
        else:
            message_dates = parse_messages(zf, msg_csv_name)

    # D-11: load existing store first, then merge
    existing = load_store(STORE_PATH)

    # ENRICH-04: capture existing keys before merge for change reporting
    existing_keys = set(existing.keys())

    store = merge_connections(existing, new_records)

    # MSG-01: apply message dates after merge
    apply_message_dates(store, message_dates)

    # ENRICH-01: merge contact_info if present
    if CONTACT_INFO_PATH.exists():
        merge_contact_info(store, CONTACT_INFO_PATH)

    save_store(store, STORE_PATH)

    # ENRICH-04: report connection changes
    added = set(store.keys()) - existing_keys
    removed = existing_keys - set(new_records.keys())
    if added:
        print(f"Added {len(added)} new connection(s).")
    if removed:
        print(f"{len(removed)} connection(s) no longer in LinkedIn export.")
    if not added and not removed:
        print("No connection changes since last import.")

    print(f"Parsed {len(new_records)} connections from {zip_path.name}")
    print(f"Store contains {len(store)} total connections")
    print(f"Saved to {STORE_PATH}")

    # HTML-01: generate self-contained HTML output
    m = re.search(r"(\d{2})-(\d{2})-(\d{4})", zip_path.name)
    linkedin_date = f"{m.group(3)}-{m.group(1)}-{m.group(2)}" if m else ""
    render_html(store, HTML_OUTPUT_PATH, linkedin_date=linkedin_date)
    print(f"HTML written to {HTML_OUTPUT_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
