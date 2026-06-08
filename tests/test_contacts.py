"""Unit tests for lib/contacts.py merge_contact_info and _find_by_name functions."""
import pytest

from lib.contacts import merge_contact_info


# ---------------------------------------------------------------------------
# Helper: write a contact_info.csv file to tmp_path
# ---------------------------------------------------------------------------

def _write_csv(tmp_path, content: str, filename: str = "contact_info.csv"):
    """Write CSV content to a file in tmp_path and return the Path."""
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    return path


HEADER = "URL,First Name,Last Name,Email,Phone,Notes\n"


# ---------------------------------------------------------------------------
# Helper: build a minimal store dict (matching the store.py record structure)
# ---------------------------------------------------------------------------

def _store(*records):
    """Build a store dict from (norm_url, first, last, company) tuples."""
    store = {}
    for norm_url, first, last, company in records:
        store[norm_url] = {
            "first_name": first,
            "last_name": last,
            "company": company,
            "url": f"https://{norm_url}/",
        }
    return store


# ---------------------------------------------------------------------------
# Test 1: URL match — row with URL sets user_email, user_phone, user_notes
# ---------------------------------------------------------------------------

def test_merge_by_url_sets_user_fields(tmp_path):
    """Row with URL sets user_email, user_phone, user_notes on matching store record."""
    store = _store(("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"))
    csv_path = _write_csv(
        tmp_path,
        HEADER + "https://www.linkedin.com/in/johndoe/,John,Doe,john@personal.com,+1-555-0100,Met at PyCon\n",
    )

    result = merge_contact_info(store, csv_path)

    assert result["linkedin.com/in/johndoe"]["user_email"] == "john@personal.com"
    assert result["linkedin.com/in/johndoe"]["user_phone"] == "+1-555-0100"
    assert result["linkedin.com/in/johndoe"]["user_notes"] == "Met at PyCon"


# ---------------------------------------------------------------------------
# Test 2: URL match — URL is normalized before lookup (trailing slash, case)
# ---------------------------------------------------------------------------

def test_merge_url_normalized_before_lookup(tmp_path):
    """URL with trailing slash and mixed case is normalized before store lookup."""
    store = _store(("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"))
    csv_path = _write_csv(
        tmp_path,
        HEADER + "https://www.LinkedIn.com/in/JohnDoe/,,,john@normalized.com,,\n",
    )

    result = merge_contact_info(store, csv_path)

    assert result["linkedin.com/in/johndoe"]["user_email"] == "john@normalized.com"


# ---------------------------------------------------------------------------
# Test 3: Name fallback — row with no URL but matching name sets user fields
# ---------------------------------------------------------------------------

def test_merge_name_fallback_exact_match(tmp_path):
    """Row with no URL falls back to First+Last name match and sets user fields."""
    store = _store(("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"))
    csv_path = _write_csv(
        tmp_path,
        HEADER + ",John,Doe,john@fallback.com,,\n",
    )

    result = merge_contact_info(store, csv_path)

    assert result["linkedin.com/in/johndoe"]["user_email"] == "john@fallback.com"


# ---------------------------------------------------------------------------
# Test 4: Name fallback — case-insensitive match ("john doe" matches "John Doe")
# ---------------------------------------------------------------------------

def test_merge_name_fallback_case_insensitive(tmp_path):
    """Name matching is case-insensitive: 'john doe' matches store record 'John Doe'."""
    store = _store(("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"))
    csv_path = _write_csv(
        tmp_path,
        HEADER + ",john,doe,john@lowercase.com,,\n",
    )

    result = merge_contact_info(store, csv_path)

    assert result["linkedin.com/in/johndoe"]["user_email"] == "john@lowercase.com"


# ---------------------------------------------------------------------------
# Test 5: Zero name matches — warning printed to stderr, row skipped
# ---------------------------------------------------------------------------

def test_merge_zero_name_matches_warns_and_skips(tmp_path, capsys):
    """Zero name matches: warning contains 'no connection found for' and row is skipped."""
    store = _store(("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"))
    csv_path = _write_csv(
        tmp_path,
        HEADER + ",Jane,Unknown,jane@test.com,,\n",
    )

    result = merge_contact_info(store, csv_path)

    captured = capsys.readouterr()
    assert "no connection found for" in captured.err
    assert "Jane Unknown" in captured.err
    assert "Skipped" in captured.err
    # No user_email set on existing record
    assert "user_email" not in result["linkedin.com/in/johndoe"]


# ---------------------------------------------------------------------------
# Test 6: Ambiguous name — 2 connections with same name, warning printed, row skipped
# ---------------------------------------------------------------------------

def test_merge_ambiguous_name_warns_and_skips(tmp_path, capsys):
    """Ambiguous name (2 matches): warning contains count, both URLs, companies, 'Skipped'."""
    store = {}
    store["linkedin.com/in/johnsmith1"] = {
        "first_name": "John",
        "last_name": "Smith",
        "company": "Acme Corp",
        "url": "https://linkedin.com/in/johnsmith1/",
    }
    store["linkedin.com/in/johnsmith2"] = {
        "first_name": "John",
        "last_name": "Smith",
        "company": "Globex",
        "url": "https://linkedin.com/in/johnsmith2/",
    }
    csv_path = _write_csv(
        tmp_path,
        HEADER + ",John,Smith,john@ambiguous.com,,\n",
    )

    result = merge_contact_info(store, csv_path)

    captured = capsys.readouterr()
    assert "2" in captured.err
    assert "John Smith" in captured.err
    assert "Acme Corp" in captured.err
    assert "Globex" in captured.err
    assert "Skipped" in captured.err
    assert "re-submit with URL to resolve" in captured.err
    # No user_email set on either record
    assert "user_email" not in result["linkedin.com/in/johnsmith1"]
    assert "user_email" not in result["linkedin.com/in/johnsmith2"]


# ---------------------------------------------------------------------------
# Test 7: Blank CSV cell does NOT overwrite existing user field
# ---------------------------------------------------------------------------

def test_merge_blank_csv_cell_does_not_overwrite(tmp_path):
    """Blank CSV cell for Email does not overwrite existing user_email in store."""
    store = _store(("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"))
    store["linkedin.com/in/johndoe"]["user_email"] = "old@mail.com"
    csv_path = _write_csv(
        tmp_path,
        # Email is blank — should NOT overwrite the existing user_email
        HEADER + "https://www.linkedin.com/in/johndoe/,John,Doe,,,Met at conference\n",
    )

    result = merge_contact_info(store, csv_path)

    assert result["linkedin.com/in/johndoe"]["user_email"] == "old@mail.com"
    # Notes should have been set from the non-empty Notes cell
    assert result["linkedin.com/in/johndoe"]["user_notes"] == "Met at conference"


# ---------------------------------------------------------------------------
# Test 8: URL present means name columns are ignored (D-04)
# ---------------------------------------------------------------------------

def test_merge_url_takes_precedence_over_name(tmp_path):
    """When URL is present, name columns are ignored — URL is used exclusively (D-04)."""
    store = {}
    store["linkedin.com/in/correcturl"] = {
        "first_name": "Different",
        "last_name": "Name",
        "company": "Some Corp",
        "url": "https://linkedin.com/in/correcturl/",
    }
    # Row has URL pointing to 'correcturl' but name columns say "John Doe" (no match by name)
    csv_path = _write_csv(
        tmp_path,
        HEADER + "https://www.linkedin.com/in/correcturl/,John,Doe,john@test.com,,\n",
    )

    result = merge_contact_info(store, csv_path)

    # URL match succeeds even though name doesn't match any record
    assert result["linkedin.com/in/correcturl"]["user_email"] == "john@test.com"


# ---------------------------------------------------------------------------
# Test 9: URL not in store — warning printed, row skipped
# ---------------------------------------------------------------------------

def test_merge_url_not_in_store_warns_and_skips(tmp_path, capsys):
    """URL present but not found in store: warning printed and row skipped."""
    store = _store(("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"))
    csv_path = _write_csv(
        tmp_path,
        HEADER + "https://www.linkedin.com/in/unknownperson/,,,test@test.com,,\n",
    )

    result = merge_contact_info(store, csv_path)

    captured = capsys.readouterr()
    assert "not found in store" in captured.err or "WARNING" in captured.err
    # The existing johndoe record should be unmodified
    assert "user_email" not in result["linkedin.com/in/johndoe"]


# ---------------------------------------------------------------------------
# Test 10: Multiple rows in CSV processed correctly
# ---------------------------------------------------------------------------

def test_merge_multiple_rows(tmp_path):
    """Multiple rows in CSV each update their respective store records."""
    store = _store(
        ("linkedin.com/in/johndoe", "John", "Doe", "Acme Corp"),
        ("linkedin.com/in/janesmith", "Jane", "Smith", "Smith LLC"),
    )
    csv_path = _write_csv(
        tmp_path,
        HEADER
        + "https://www.linkedin.com/in/johndoe/,John,Doe,john@test.com,,\n"
        + "https://www.linkedin.com/in/janesmith/,Jane,Smith,jane@test.com,+1-555-9999,Former colleague\n",
    )

    result = merge_contact_info(store, csv_path)

    assert result["linkedin.com/in/johndoe"]["user_email"] == "john@test.com"
    assert result["linkedin.com/in/janesmith"]["user_email"] == "jane@test.com"
    assert result["linkedin.com/in/janesmith"]["user_phone"] == "+1-555-9999"
    assert result["linkedin.com/in/janesmith"]["user_notes"] == "Former colleague"
