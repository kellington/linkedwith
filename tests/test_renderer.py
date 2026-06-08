"""Tests for lib.renderer: render_html output correctness."""
import pytest
from pathlib import Path
from lib.renderer import render_html


def _make_store():
    """Build a minimal 3-record store dict for testing."""
    return {
        "linkedin.com/in/alice": {
            "first_name": "Alice",
            "last_name": "Smith",
            "url": "linkedin.com/in/alice",
            "company": "Acme Corp",
            "position": "Engineer",
            "connected_on": "2024-01-15",
            "most_recent_message": "2024-06-01",
            "user_email": "alice@example.com",
            "user_phone": "555-0101",
            "user_notes": "Met at conference",
        },
        "linkedin.com/in/bob": {
            "first_name": "Bob",
            "last_name": "O'Brien",
            "url": "linkedin.com/in/bob",
            "company": "AT&T",
            "position": "Manager",
            "connected_on": "2023-11-20",
            "most_recent_message": None,
            # No user_email, user_phone, user_notes keys at all
        },
        "linkedin.com/in/carol": {
            "first_name": "Carol",
            "last_name": "Jones",
            "url": "linkedin.com/in/carol",
            "company": "StartupCo",
            "position": "CEO",
            "connected_on": "2024-03-10",
            "most_recent_message": "2024-05-15",
            "user_email": "",
            "user_phone": "",
            "user_notes": "",
        },
    }


def test_render_creates_file(tmp_path):
    """render_html creates an HTML file at the given path."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    assert output.exists()


def test_html_contains_doctype(tmp_path):
    """Output starts with <!DOCTYPE html>."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert content.strip().startswith("<!DOCTYPE html>")


def test_all_nine_columns_present(tmp_path):
    """Output contains th elements for all 9 columns in correct order."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    columns = [
        "First Name",
        "Last Name",
        "Company",
        "Position",
        "Connected On",
        "Most Recent Message",
        "Email",
        "Phone",
        "Notes",
    ]
    for col in columns:
        assert col in content, f"Column '{col}' not found in HTML output"
    # Verify order
    positions = [content.index(col) for col in columns]
    assert positions == sorted(positions), "Columns not in correct order"


def test_sortable_headers(tmp_path):
    """Exactly 5 th elements have data-sortable attribute."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    # Count only th elements with data-sortable (not CSS rules which also contain it)
    assert content.count("<th data-sortable>") == 5


def test_non_sortable_headers(tmp_path):
    """Company, Position, Email, Phone th elements do NOT have data-sortable."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    # These should appear as plain th elements without data-sortable
    for col in ["Company", "Position", "Email", "Phone"]:
        # Find the th containing this column name
        idx = content.index(f"<th>{col}</th>")
        assert idx >= 0, f"<th>{col}</th> (non-sortable) not found"


def test_default_sort_js(tmp_path):
    """Script contains sort(4) call in window.onload (Connected On descending)."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "sort(4)" in content


def test_viewport_meta(tmp_path):
    """Output contains viewport meta tag for mobile rendering."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in content


def test_overflow_x(tmp_path):
    """Output contains overflow-x: auto for horizontal scroll on mobile."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "overflow-x: auto" in content or "overflow-x:auto" in content


def test_autoescape_special_chars(tmp_path):
    """Store with first_name containing apostrophe and company with & renders escaped."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    # Bob's last name O'Brien should be escaped
    assert "O&#39;Brien" in content, "Apostrophe in O'Brien should be HTML-escaped"
    assert "O'Brien" not in content, "Raw apostrophe should not appear in HTML"
    # Bob's company AT&T should be escaped
    assert "AT&amp;T" in content, "& in AT&T should be HTML-escaped"


def test_none_values_render_empty(tmp_path):
    """Store record missing user_email, user_phone, user_notes renders empty cells, not None."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "None" not in content, "String 'None' should not appear in rendered HTML"


def test_null_most_recent_message(tmp_path):
    """Store record with most_recent_message=None renders empty data-sort attribute value."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    # The data-sort attribute for Bob's most_recent_message=None should be empty, not "None"
    assert 'data-sort="None"' not in content


def test_no_external_urls(tmp_path):
    """Output does not contain http:// or https:// (no CDN, no external requests)."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "http://" not in content
    assert "https://" not in content


def test_inline_style_tag(tmp_path):
    """Output contains <style> and </style> tags."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "<style>" in content
    assert "</style>" in content


def test_inline_script_tag(tmp_path):
    """Output contains <script> and </script> tags."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "<script>" in content
    assert "</script>" in content


def test_atomic_write_no_tmp_leftover(tmp_path):
    """After render_html completes, no .tmp file remains alongside the output."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    assert not (tmp_path / "LinkedWith.HTML.tmp").exists()


def test_row_count(tmp_path):
    """Store with 3 records produces 3 <tr> elements in tbody."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    # Count <tr> inside tbody — simpler: count all <tr> minus 1 for thead
    # Actually count data rows by counting <td data-sort= occurrences / 5 sortable cols
    # Better: count occurrences of specific td pattern for first column
    tbody_start = content.index("<tbody>")
    tbody_end = content.index("</tbody>")
    tbody_content = content[tbody_start:tbody_end]
    assert tbody_content.count("<tr>") == 3


def test_sentinel_in_js(tmp_path):
    """Script contains the string 0000-00-00 (null-last sentinel for date sorting)."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "0000-00-00" in content


def test_connection_count_display(tmp_path):
    """Output contains the text '3 connections' for a 3-record store."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    content = output.read_text(encoding="utf-8")
    assert "3 connections" in content
