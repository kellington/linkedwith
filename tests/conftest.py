"""Session-scoped fixture: creates tests/fixtures/sample_export.zip if it does not exist."""
import io
import zipfile
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_ZIP = FIXTURES_DIR / "sample_export.zip"

# Connections.csv content with UTF-8 BOM + 3 preamble lines + header + 3 data rows
CONNECTIONS_CSV_CONTENT = (
    "\ufeff"  # UTF-8 BOM
    "Notes:\n"
    "\n"
    "\n"
    "First Name,Last Name,URL,Email Address,Company,Position,Connected On\n"
    "John,Doe,https://www.linkedin.com/in/johndoe/,john@example.com,Acme Corp,Engineer,15 Jan 2023\n"
    "Jane,Smith,https://LinkedIn.com/in/JaneSmith,,Smith LLC,CEO,29 Dec 2021\n"
    "Bob,NoURL,,,NoCompany,Intern,01 Mar 2024\n"
)

# messages.csv content with UTF-8 BOM + header + test data rows (no preamble).
# Includes: two messages from same sender (different dates), one LinkedIn Member row
# (empty sender URL), and one group conversation row.
# BOM is \ufeff in the string literal; encode with utf-8 (not utf-8-sig) to avoid double BOM.
MESSAGES_CSV_CONTENT = (
    "\ufeff"  # UTF-8 BOM
    "CONVERSATION ID,CONVERSATION TITLE,FROM,SENDER PROFILE URL,"
    "TO,RECIPIENT PROFILE URLS,DATE,SUBJECT,CONTENT,FOLDER,ATTACHMENTS\n"
    # Two messages from Alice (different dates — max should be 2026-01-15)
    "conv-001,,Alice Smith,https://www.linkedin.com/in/alicesmith/,"
    "Rob,https://www.linkedin.com/in/rob,2026-01-15 10:00:00 UTC,,,archived,\n"
    "conv-003,,Alice Smith,https://www.linkedin.com/in/alicesmith/,"
    "Rob,https://www.linkedin.com/in/rob,2025-12-01 08:00:00 UTC,,,archived,\n"
    # LinkedIn Member row (empty SENDER PROFILE URL) — should be silently skipped
    "conv-002,,LinkedIn Member,,Rob,https://www.linkedin.com/in/rob,"
    "2025-06-01 12:00:00 UTC,,,archived,\n"
    # Group conversation: Bob sends to multiple recipients
    "conv-004,,Bob Jones,https://www.linkedin.com/in/bobjones/,"
    "Rob;Carol,https://www.linkedin.com/in/rob;https://www.linkedin.com/in/carol,"
    "2026-02-10 09:30:00 UTC,,,inbox,\n"
)


@pytest.fixture(scope="session", autouse=True)
def create_sample_export_zip():
    """Create sample_export.zip fixture with BOM, preamble, and 3 data rows."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_ZIP.exists():
        buf = io.BytesIO(CONNECTIONS_CSV_CONTENT.encode("utf-8-sig"))
        # We encoded to utf-8-sig which would double-encode the BOM — use raw bytes instead
        raw_bytes = CONNECTIONS_CSV_CONTENT.encode("utf-8")
        with zipfile.ZipFile(SAMPLE_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Connections.csv", raw_bytes)
    return SAMPLE_ZIP


@pytest.fixture(scope="session")
def sample_zip_path(create_sample_export_zip):
    return SAMPLE_ZIP


@pytest.fixture(scope="session")
def sample_zip_with_messages(create_sample_export_zip):
    """Return path to a ZIP containing both Connections.csv and messages.csv.

    The ZIP is created once per test session and stored in the fixtures directory.
    Both files include the UTF-8 BOM encoded via utf-8 (not utf-8-sig) to avoid
    double-BOM — matches the established conftest.py pattern.
    """
    zip_path = FIXTURES_DIR / "sample_export_with_messages.zip"
    if not zip_path.exists():
        conn_bytes = CONNECTIONS_CSV_CONTENT.encode("utf-8")
        msg_bytes = MESSAGES_CSV_CONTENT.encode("utf-8")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Connections.csv", conn_bytes)
            zf.writestr("messages.csv", msg_bytes)
    return zip_path
