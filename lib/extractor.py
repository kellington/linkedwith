"""ZIP file handling: case-insensitive CSV lookup and BOM-safe open.

Handles LinkedIn export ZIPs which may use varying filename capitalizations
across export versions (e.g. Connections.csv vs connections.csv).
"""
import io
import zipfile


def find_csv_in_zip(zf: zipfile.ZipFile, target_name: str) -> str | None:
    """Return the exact ZipInfo name matching target_name case-insensitively.

    Handles CSVs nested in subdirectories (e.g. 'export_data/Connections.csv').
    Returns None if no match is found.

    Args:
        zf: Open ZipFile object.
        target_name: Filename to search for (e.g. "Connections.csv").

    Returns:
        Exact name string from zf.namelist(), or None.
    """
    target_lower = target_name.lower()
    for name in zf.namelist():
        basename = name.lower().split('/')[-1]
        if basename == target_lower:
            return name
    return None


def open_csv_in_zip(zf: zipfile.ZipFile, csv_name: str) -> io.TextIOWrapper:
    """Open a CSV inside a ZIP with utf-8-sig encoding (BOM-safe).

    utf-8-sig automatically strips the UTF-8 BOM (\xef\xbb\xbf) that LinkedIn
    includes at the start of all exported CSV files. Without this, the BOM
    appears as \ufeff in the first column header, silently breaking lookups.

    Args:
        zf: Open ZipFile object.
        csv_name: Exact name of the CSV within the ZIP (from find_csv_in_zip).

    Returns:
        TextIOWrapper ready for line iteration or csv.DictReader.
    """
    return io.TextIOWrapper(zf.open(csv_name), encoding="utf-8-sig")
