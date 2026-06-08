"""Tests for lib.parsers.parse_connections"""
import zipfile
import pytest
from lib.parsers import parse_connections


def test_parse_returns_two_records(sample_zip_path):
    """parse_connections returns 2 records (Bob NoURL is skipped)."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    assert len(result) == 2


def test_parse_keys_are_normalized_urls(sample_zip_path):
    """Keys are normalized LinkedIn URLs."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    assert "linkedin.com/in/johndoe" in result
    assert "linkedin.com/in/janesmith" in result


def test_parse_john_doe_fields(sample_zip_path):
    """John Doe record has correct field values."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    record = result["linkedin.com/in/johndoe"]
    assert record["first_name"] == "John"
    assert record["last_name"] == "Doe"
    assert record["url"] == "https://www.linkedin.com/in/johndoe/"
    assert record["email"] == "john@example.com"
    assert record["company"] == "Acme Corp"
    assert record["position"] == "Engineer"
    assert record["connected_on"] == "2023-01-15"


def test_parse_jane_smith_fields(sample_zip_path):
    """Jane Smith record: date conversion, empty email as empty string."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    record = result["linkedin.com/in/janesmith"]
    assert record["connected_on"] == "2021-12-29"
    assert record["email"] == ""  # empty string, not None
    assert record["email"] is not None


def test_parse_meta_source(sample_zip_path):
    """Both records have _meta.source == 'linkedin_export'."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    for key, record in result.items():
        assert record["_meta"]["source"] == "linkedin_export"


def test_bob_nourl_skipped(sample_zip_path):
    """Bob NoURL (no profile URL) is not in the result."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    # No key that would match Bob NoURL
    for key in result:
        assert "bob" not in key.lower()


def test_bob_nourl_warning_to_stderr(sample_zip_path, capsys):
    """Skipping Bob NoURL emits a WARNING to stderr."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        parse_connections(zf, "Connections.csv")
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "Bob" in captured.err
    assert "NoURL" in captured.err


def test_no_bom_corruption(sample_zip_path):
    """First Name column is accessible — BOM did not corrupt the header."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    # If BOM corrupted header, first_name would be empty or missing
    assert result["linkedin.com/in/johndoe"]["first_name"] != ""
    assert "\ufeff" not in result["linkedin.com/in/johndoe"].get("first_name", "")


def test_preamble_lines_not_in_result(sample_zip_path):
    """Preamble content ('Notes:') does not appear as a record key or field value."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = parse_connections(zf, "Connections.csv")
    for key in result:
        assert "notes" not in key.lower()
    for record in result.values():
        assert record["first_name"] not in ("Notes:", "")
