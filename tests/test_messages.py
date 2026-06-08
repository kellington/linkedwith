"""Unit tests for lib/messages.py parse_messages function."""
import io
import zipfile

import pytest

from lib.extractor import find_csv_in_zip
from lib.messages import parse_messages


# ---------------------------------------------------------------------------
# Helper: build an in-memory ZIP containing messages.csv
# ---------------------------------------------------------------------------

def _make_zip(csv_content: str) -> zipfile.ZipFile:
    """Return an open ZipFile (in-memory) with messages.csv written as utf-8 bytes.

    The BOM (\ufeff) must be part of csv_content string literal, and we encode
    with utf-8 (NOT utf-8-sig) to avoid double-BOM — matches conftest.py pattern.
    """
    raw_bytes = csv_content.encode("utf-8")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("messages.csv", raw_bytes)
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


HEADER = (
    "\ufeff"  # UTF-8 BOM
    "CONVERSATION ID,CONVERSATION TITLE,FROM,SENDER PROFILE URL,"
    "TO,RECIPIENT PROFILE URLS,DATE,SUBJECT,CONTENT,FOLDER,ATTACHMENTS\n"
)


# ---------------------------------------------------------------------------
# Test 1: 3 messages from 2 senders -> dict with 2 keys, each ISO date string
# ---------------------------------------------------------------------------

def test_parse_messages_two_senders():
    """3 messages from 2 different senders returns dict with 2 keys."""
    content = (
        HEADER
        + "conv-001,,Alice,https://www.linkedin.com/in/alicesmith/,Rob,https://www.linkedin.com/in/rob,2026-01-15 10:00:00 UTC,,,archived,\n"
        + "conv-002,,Bob,https://www.linkedin.com/in/bobsmith/,Rob,https://www.linkedin.com/in/rob,2026-01-16 09:00:00 UTC,,,archived,\n"
        + "conv-001,,Alice,https://www.linkedin.com/in/alicesmith/,Rob,https://www.linkedin.com/in/rob,2025-12-01 08:00:00 UTC,,,archived,\n"
    )
    zf = _make_zip(content)
    csv_name = find_csv_in_zip(zf, "messages.csv")
    result = parse_messages(zf, csv_name)

    assert len(result) == 2
    assert "linkedin.com/in/alicesmith" in result
    assert "linkedin.com/in/bobsmith" in result
    # Values are ISO date strings
    assert isinstance(result["linkedin.com/in/alicesmith"], str)
    assert isinstance(result["linkedin.com/in/bobsmith"], str)


# ---------------------------------------------------------------------------
# Test 2: same sender with multiple messages -> max date wins
# ---------------------------------------------------------------------------

def test_parse_messages_max_date_per_sender():
    """Same sender with messages on 2026-01-15 and 2025-12-01 returns '2026-01-15'."""
    content = (
        HEADER
        + "conv-001,,Alice,https://www.linkedin.com/in/alicesmith/,Rob,https://www.linkedin.com/in/rob,2026-01-15 10:00:00 UTC,,,archived,\n"
        + "conv-003,,Alice,https://www.linkedin.com/in/alicesmith/,Rob,https://www.linkedin.com/in/rob,2025-12-01 08:00:00 UTC,,,archived,\n"
    )
    zf = _make_zip(content)
    csv_name = find_csv_in_zip(zf, "messages.csv")
    result = parse_messages(zf, csv_name)

    assert result["linkedin.com/in/alicesmith"] == "2026-01-15"


# ---------------------------------------------------------------------------
# Test 3: LinkedIn Member row (empty sender URL) is silently skipped
# ---------------------------------------------------------------------------

def test_parse_messages_skips_linkedin_member_rows():
    """Row with empty SENDER PROFILE URL ('LinkedIn Member') is silently skipped."""
    content = (
        HEADER
        + "conv-002,,LinkedIn Member,,Rob,https://www.linkedin.com/in/rob,2025-06-01 12:00:00 UTC,,,archived,\n"
    )
    zf = _make_zip(content)
    csv_name = find_csv_in_zip(zf, "messages.csv")
    result = parse_messages(zf, csv_name)

    assert result == {}


# ---------------------------------------------------------------------------
# Test 4: DATE format "2026-02-13 00:23:08 UTC" parsed to "2026-02-13"
# ---------------------------------------------------------------------------

def test_parse_messages_date_format():
    """DATE format '2026-02-13 00:23:08 UTC' is parsed correctly to '2026-02-13'."""
    content = (
        HEADER
        + "conv-004,,Alice,https://www.linkedin.com/in/alicesmith/,Rob,https://www.linkedin.com/in/rob,2026-02-13 00:23:08 UTC,,,archived,\n"
    )
    zf = _make_zip(content)
    csv_name = find_csv_in_zip(zf, "messages.csv")
    result = parse_messages(zf, csv_name)

    assert result["linkedin.com/in/alicesmith"] == "2026-02-13"


# ---------------------------------------------------------------------------
# Test 5: URLs normalized before keying (trailing slash, case)
# ---------------------------------------------------------------------------

def test_parse_messages_url_normalization():
    """URLs are normalized before keying: 'https://www.linkedin.com/in/AliceSmith/' -> 'linkedin.com/in/alicesmith'."""
    content = (
        HEADER
        + "conv-005,,Alice,https://www.linkedin.com/in/AliceSmith/,Rob,https://www.linkedin.com/in/rob,2026-01-15 10:00:00 UTC,,,archived,\n"
    )
    zf = _make_zip(content)
    csv_name = find_csv_in_zip(zf, "messages.csv")
    result = parse_messages(zf, csv_name)

    assert "linkedin.com/in/alicesmith" in result
    # Capital-case key should NOT be present
    assert "linkedin.com/in/AliceSmith" not in result
    assert "linkedin.com/in/AliceSmith/" not in result


# ---------------------------------------------------------------------------
# Test 6: group conversation messages handled (each sender gets their date updated)
# ---------------------------------------------------------------------------

def test_parse_messages_group_conversation():
    """Group conversation: multiple senders each get their max date tracked independently."""
    content = (
        HEADER
        # Alice sends in a group (TO has multiple recipients)
        + "conv-006,,Alice,https://www.linkedin.com/in/alicesmith/,Rob;Carol,https://www.linkedin.com/in/rob;https://www.linkedin.com/in/carol,2026-02-01 10:00:00 UTC,,,archived,\n"
        # Bob also sends in the same group conversation
        + "conv-006,,Bob,https://www.linkedin.com/in/bobsmith/,Rob;Carol,https://www.linkedin.com/in/rob;https://www.linkedin.com/in/carol,2026-02-02 11:00:00 UTC,,,archived,\n"
    )
    zf = _make_zip(content)
    csv_name = find_csv_in_zip(zf, "messages.csv")
    result = parse_messages(zf, csv_name)

    assert result.get("linkedin.com/in/alicesmith") == "2026-02-01"
    assert result.get("linkedin.com/in/bobsmith") == "2026-02-02"


# ---------------------------------------------------------------------------
# Test 7: empty CSV (header only) returns empty dict
# ---------------------------------------------------------------------------

def test_parse_messages_empty_csv():
    """CSV with header only returns empty dict."""
    content = HEADER
    zf = _make_zip(content)
    csv_name = find_csv_in_zip(zf, "messages.csv")
    result = parse_messages(zf, csv_name)

    assert result == {}
