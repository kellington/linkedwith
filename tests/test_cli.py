"""End-to-end CLI tests for linkedwith.py.

Tests the full ZIP-to-JSON pipeline via subprocess invocation.
Uses tmp_path for all file operations — no pollution of project directory.
"""
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

# Project root is two levels up from tests/
PROJECT_ROOT = Path(__file__).parent.parent


def _run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run linkedwith.py CLI via uv run python, with output paths scoped to cwd."""
    cmd = [
        "uv", "run", "--project", str(PROJECT_ROOT),
        "python", str(PROJECT_ROOT / "linkedwith.py"),
    ] + args
    env = os.environ.copy()
    env["LINKEDWITH_STORE"] = str(cwd / "linkedwith.json")
    env["LINKEDWITH_HTML_OUTPUT"] = str(cwd / "LinkedWith.HTML")
    env["LINKEDWITH_CONTACT_INFO"] = str(cwd / "contact_info.csv")
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), env=env)


@pytest.fixture()
def sample_zip(tmp_path, sample_zip_path) -> Path:
    """Copy the session-scoped sample_export.zip into tmp_path for isolation."""
    dest = tmp_path / "sample_export.zip"
    dest.write_bytes(sample_zip_path.read_bytes())
    return dest


@pytest.fixture()
def empty_zip(tmp_path) -> Path:
    """ZIP that contains no Connections.csv."""
    dest = tmp_path / "bad.zip"
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("README.txt", "no connections here")
    return dest


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_zip_creates_store(sample_zip, tmp_path):
    """Running with a valid ZIP creates linkedwith.json in cwd."""
    result = _run_cli([str(sample_zip)], cwd=tmp_path)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstderr: {result.stderr}"
    store_path = tmp_path / "linkedwith.json"
    assert store_path.exists(), "linkedwith.json should be created in cwd"


def test_valid_zip_two_records(sample_zip, tmp_path):
    """Sample ZIP (3 rows, 1 no-URL) produces exactly 2 records."""
    _run_cli([str(sample_zip)], cwd=tmp_path)
    store = json.loads((tmp_path / "linkedwith.json").read_text())
    assert len(store) == 2, f"Expected 2 records, got {len(store)}"


def test_stdout_parsed_count(sample_zip, tmp_path):
    """stdout contains 'Parsed 2 connections' message."""
    result = _run_cli([str(sample_zip)], cwd=tmp_path)
    assert "Parsed 2 connections" in result.stdout, f"stdout: {result.stdout!r}"


def test_stdout_saved_path(sample_zip, tmp_path):
    """stdout contains 'Saved to' and references linkedwith.json."""
    result = _run_cli([str(sample_zip)], cwd=tmp_path)
    assert "Saved to" in result.stdout, f"stdout: {result.stdout!r}"
    assert "linkedwith.json" in result.stdout, f"stdout: {result.stdout!r}"


def test_store_is_valid_json(sample_zip, tmp_path):
    """linkedwith.json is parseable as JSON after a run."""
    _run_cli([str(sample_zip)], cwd=tmp_path)
    content = (tmp_path / "linkedwith.json").read_text()
    store = json.loads(content)  # raises if invalid
    assert isinstance(store, dict)


def test_store_record_has_expected_keys(sample_zip, tmp_path):
    """Records contain the expected connection fields."""
    _run_cli([str(sample_zip)], cwd=tmp_path)
    store = json.loads((tmp_path / "linkedwith.json").read_text())
    for record in store.values():
        for key in ("first_name", "last_name", "url", "company", "position", "connected_on"):
            assert key in record, f"Record missing key '{key}': {record}"


def test_store_keys_are_normalized_urls(sample_zip, tmp_path):
    """Store keys are normalized (no scheme, no trailing slash, lowercase)."""
    _run_cli([str(sample_zip)], cwd=tmp_path)
    store = json.loads((tmp_path / "linkedwith.json").read_text())
    for key in store:
        assert not key.startswith("http"), f"Key should not have scheme: {key!r}"
        assert not key.endswith("/"), f"Key should not have trailing slash: {key!r}"
        assert key == key.lower(), f"Key should be lowercase: {key!r}"


# ---------------------------------------------------------------------------
# Idempotency (D-11)
# ---------------------------------------------------------------------------

def test_idempotent_second_run_same_count(sample_zip, tmp_path):
    """Running twice with same ZIP produces same number of records."""
    _run_cli([str(sample_zip)], cwd=tmp_path)
    _run_cli([str(sample_zip)], cwd=tmp_path)
    store = json.loads((tmp_path / "linkedwith.json").read_text())
    assert len(store) == 2, f"Expected 2 records after re-run, got {len(store)}"


def test_idempotent_preserves_user_fields(sample_zip, tmp_path):
    """Re-running preserves user_ prefixed fields added to the store."""
    _run_cli([str(sample_zip)], cwd=tmp_path)
    # Manually inject a user_ field into the store
    store_path = tmp_path / "linkedwith.json"
    store = json.loads(store_path.read_text())
    first_key = next(iter(store))
    store[first_key]["user_notes"] = "met at conference"
    store_path.write_text(json.dumps(store))
    # Re-run
    _run_cli([str(sample_zip)], cwd=tmp_path)
    updated = json.loads(store_path.read_text())
    assert updated[first_key].get("user_notes") == "met at conference", (
        "user_notes should be preserved after re-run"
    )


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_zip_without_connections_exits_1(empty_zip, tmp_path):
    """ZIP with no Connections.csv exits with code 1."""
    result = _run_cli([str(empty_zip)], cwd=tmp_path)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"


def test_zip_without_connections_stderr_message(empty_zip, tmp_path):
    """ZIP with no Connections.csv reports 'Connections.csv not found' on stderr."""
    result = _run_cli([str(empty_zip)], cwd=tmp_path)
    assert "Connections.csv not found" in result.stderr, f"stderr: {result.stderr!r}"


def test_nonexistent_zip_exits_nonzero(tmp_path):
    """Nonexistent ZIP path exits with non-zero return code."""
    result = _run_cli([str(tmp_path / "ghost.zip")], cwd=tmp_path)
    assert result.returncode != 0, "Should fail for missing file"


def test_nonexistent_zip_stderr_message(tmp_path):
    """Nonexistent ZIP path prints an error message to stderr."""
    result = _run_cli([str(tmp_path / "ghost.zip")], cwd=tmp_path)
    assert result.stderr.strip() != "", "Should print error to stderr"


def test_no_args_exits_nonzero(tmp_path):
    """Running with no arguments exits with non-zero code."""
    result = _run_cli([], cwd=tmp_path)
    assert result.returncode != 0, "Should fail when no ZIP arg provided"


# ---------------------------------------------------------------------------
# Phase 2: Message integration and change reporting
# ---------------------------------------------------------------------------

def _make_zip_with_messages(dest: Path, connections_content: str, messages_content: str) -> Path:
    """Build a test ZIP containing both Connections.csv and messages.csv."""
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Connections.csv", connections_content.encode("utf-8"))
        zf.writestr("messages.csv", messages_content.encode("utf-8"))
    return dest


def _make_connections_csv(rows: list[tuple]) -> str:
    """Return Connections.csv content (BOM + preamble + header + rows).

    rows: list of (first, last, url, email, company, position, connected_on)
    """
    lines = [
        "\ufeff",
        "Notes:\n\n\n",
        "First Name,Last Name,URL,Email Address,Company,Position,Connected On\n",
    ]
    for first, last, url, email, company, position, connected_on in rows:
        lines.append(f"{first},{last},{url},{email},{company},{position},{connected_on}\n")
    return "".join(lines)


def _make_messages_csv(rows: list[tuple]) -> str:
    """Return messages.csv content (BOM + header + rows).

    rows: list of (conv_id, sender_url, date)
    """
    header = (
        "\ufeff"
        "CONVERSATION ID,CONVERSATION TITLE,FROM,SENDER PROFILE URL,"
        "TO,RECIPIENT PROFILE URLS,DATE,SUBJECT,CONTENT,FOLDER,ATTACHMENTS\n"
    )
    data_rows = "".join(
        f"{conv_id},,Sender,{sender_url},Rob,https://www.linkedin.com/in/rob,"
        f"{date},,,inbox,\n"
        for conv_id, sender_url, date in rows
    )
    return header + data_rows


def test_cli_parses_messages(tmp_path):
    """CLI run against a ZIP with messages.csv produces most_recent_message in the store."""
    # Connection whose URL matches a message sender
    conn_url = "https://www.linkedin.com/in/alicesmith/"
    connections = _make_connections_csv([
        ("Alice", "Smith", conn_url, "", "Corp", "Engineer", "15 Jan 2023"),
    ])
    messages = _make_messages_csv([
        ("conv-001", conn_url, "2026-01-15 10:00:00 UTC"),
    ])
    zip_path = _make_zip_with_messages(tmp_path / "test.zip", connections, messages)

    result = _run_cli([str(zip_path)], cwd=tmp_path)
    assert result.returncode == 0, f"Expected exit 0\nstderr: {result.stderr}"

    store = json.loads((tmp_path / "linkedwith.json").read_text())
    # Find alice's record
    alice_key = next((k for k in store if "alicesmith" in k), None)
    assert alice_key is not None, f"alicesmith key not found in store: {list(store.keys())}"
    assert store[alice_key].get("most_recent_message") == "2026-01-15", (
        f"Expected most_recent_message='2026-01-15', got {store[alice_key].get('most_recent_message')!r}"
    )


def test_cli_change_report_first_run(sample_zip, tmp_path):
    """First-run stdout contains 'Parsed N connections' but no removal message."""
    result = _run_cli([str(sample_zip)], cwd=tmp_path)
    assert result.returncode == 0
    assert "Parsed 2 connections" in result.stdout, f"stdout: {result.stdout!r}"
    assert "no longer in LinkedIn export" not in result.stdout, (
        f"First run should not report removals. stdout: {result.stdout!r}"
    )


def test_cli_change_report_with_additions(tmp_path):
    """Second run with more connections reports 'Added N new connection(s)'."""
    # First run: 2 connections
    zip1 = tmp_path / "run1.zip"
    conn1 = _make_connections_csv([
        ("Alice", "Smith", "https://www.linkedin.com/in/alicesmith/", "", "Corp", "Eng", "01 Jan 2023"),
        ("Bob", "Jones", "https://www.linkedin.com/in/bobjones/", "", "Inc", "Dev", "01 Feb 2023"),
    ])
    with zipfile.ZipFile(zip1, "w") as zf:
        zf.writestr("Connections.csv", conn1.encode("utf-8"))
    _run_cli([str(zip1)], cwd=tmp_path)

    # Second run: 3 connections (one new)
    zip2 = tmp_path / "run2.zip"
    conn2 = _make_connections_csv([
        ("Alice", "Smith", "https://www.linkedin.com/in/alicesmith/", "", "Corp", "Eng", "01 Jan 2023"),
        ("Bob", "Jones", "https://www.linkedin.com/in/bobjones/", "", "Inc", "Dev", "01 Feb 2023"),
        ("Carol", "Lee", "https://www.linkedin.com/in/carollee/", "", "Co", "PM", "01 Mar 2023"),
    ])
    with zipfile.ZipFile(zip2, "w") as zf:
        zf.writestr("Connections.csv", conn2.encode("utf-8"))
    result = _run_cli([str(zip2)], cwd=tmp_path)

    assert result.returncode == 0
    assert "Added 1 new connection(s)." in result.stdout, (
        f"Expected addition report. stdout: {result.stdout!r}"
    )


def test_cli_contact_info_merge(tmp_path, monkeypatch):
    """CLI auto-merges contact_info.csv from cwd into the store."""
    # Set up the ZIP
    conn = _make_connections_csv([
        ("Alice", "Smith", "https://www.linkedin.com/in/alicesmith/", "", "Corp", "Eng", "01 Jan 2023"),
    ])
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("Connections.csv", conn.encode("utf-8"))

    # Create contact_info.csv in tmp_path (will become cwd)
    contact_csv = tmp_path / "contact_info.csv"
    contact_csv.write_text(
        "URL,First Name,Last Name,Email,Phone,Notes\n"
        "https://www.linkedin.com/in/alicesmith/,Alice,Smith,alice@personal.com,+1-555-0100,Met at conf\n",
        encoding="utf-8",
    )

    result = _run_cli([str(zip_path)], cwd=tmp_path)
    assert result.returncode == 0, f"Expected exit 0\nstderr: {result.stderr}"

    store = json.loads((tmp_path / "linkedwith.json").read_text())
    alice_key = next((k for k in store if "alicesmith" in k), None)
    assert alice_key is not None
    assert store[alice_key].get("user_email") == "alice@personal.com", (
        f"user_email not merged: {store[alice_key]}"
    )


def test_cli_missing_messages_csv(sample_zip, tmp_path):
    """ZIP with no messages.csv exits 0 with a warning to stderr."""
    result = _run_cli([str(sample_zip)], cwd=tmp_path)
    assert result.returncode == 0, f"Expected exit 0\nstderr: {result.stderr}"
    assert "messages.csv not found in ZIP" in result.stderr, (
        f"Expected warning in stderr. stderr: {result.stderr!r}"
    )


def test_cli_produces_html_output(sample_zip, tmp_path):
    """Running with a valid ZIP creates LinkedWith.HTML in cwd."""
    result = _run_cli([str(sample_zip)], cwd=tmp_path)
    assert result.returncode == 0, f"Expected exit 0\nstderr: {result.stderr}"
    html_path = tmp_path / "LinkedWith.HTML"
    assert html_path.exists(), "LinkedWith.HTML should be created in cwd"
    assert "HTML written to" in result.stdout, f"stdout: {result.stdout!r}"
    content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content, "HTML file should contain DOCTYPE declaration"
    assert '<table id="contacts">' in content, "HTML file should contain contacts table"
    assert "data-sortable" in content, "HTML file should contain sortable column attributes"


def test_cli_user_fields_survive_reimport(tmp_path, monkeypatch):
    """ENRICH-03: user_email set via contact_info.csv survives a second run without contact_info.csv."""
    conn = _make_connections_csv([
        ("Alice", "Smith", "https://www.linkedin.com/in/alicesmith/", "", "Corp", "Eng", "01 Jan 2023"),
    ])
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("Connections.csv", conn.encode("utf-8"))

    # First run WITH contact_info.csv to set user_email
    contact_csv = tmp_path / "contact_info.csv"
    contact_csv.write_text(
        "URL,First Name,Last Name,Email,Phone,Notes\n"
        "https://www.linkedin.com/in/alicesmith/,Alice,Smith,alice@personal.com,,\n",
        encoding="utf-8",
    )
    _run_cli([str(zip_path)], cwd=tmp_path)

    # Remove contact_info.csv before second run
    contact_csv.unlink()

    # Second run WITHOUT contact_info.csv
    result = _run_cli([str(zip_path)], cwd=tmp_path)
    assert result.returncode == 0

    store = json.loads((tmp_path / "linkedwith.json").read_text())
    alice_key = next((k for k in store if "alicesmith" in k), None)
    assert alice_key is not None
    assert store[alice_key].get("user_email") == "alice@personal.com", (
        f"user_email should survive re-import. Got: {store[alice_key].get('user_email')!r}"
    )
