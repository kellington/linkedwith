"""Tests for lib.store: load_store, save_store, merge_connections"""
import json
import pytest
from pathlib import Path
from lib.store import load_store, save_store, merge_connections


def test_load_store_nonexistent(tmp_path):
    """load_store returns empty dict when file does not exist."""
    result = load_store(tmp_path / "missing.json")
    assert result == {}


def test_save_and_load_roundtrip(tmp_path):
    """save_store then load_store returns identical data."""
    store_path = tmp_path / "linkedwith.json"
    data = {
        "linkedin.com/in/johndoe": {
            "first_name": "John",
            "last_name": "Doe",
            "url": "https://www.linkedin.com/in/johndoe/",
            "email": "john@example.com",
            "company": "Acme Corp",
            "position": "Engineer",
            "connected_on": "2023-01-15",
            "_meta": {"source": "linkedin_export"},
        }
    }
    save_store(data, store_path)
    loaded = load_store(store_path)
    assert loaded == data


def test_save_no_tmp_file_remains(tmp_path):
    """No .json.tmp file should exist after save_store completes."""
    store_path = tmp_path / "linkedwith.json"
    save_store({"key": "value"}, store_path)
    tmp_file = tmp_path / "linkedwith.json.tmp"
    assert not tmp_file.exists()


def test_merge_connections_upsert_new(tmp_path):
    """merge_connections adds new records that don't exist yet."""
    existing = {}
    new_records = {
        "linkedin.com/in/newuser": {
            "first_name": "New",
            "last_name": "User",
            "url": "https://linkedin.com/in/newuser",
            "email": "",
            "company": "Corp",
            "position": "Dev",
            "connected_on": "2024-01-01",
            "_meta": {"source": "linkedin_export"},
        }
    }
    result = merge_connections(existing, new_records)
    assert "linkedin.com/in/newuser" in result
    assert result["linkedin.com/in/newuser"]["first_name"] == "New"


def test_merge_connections_updates_linkedin_fields():
    """merge_connections updates LinkedIn-sourced fields on existing records."""
    existing = {
        "linkedin.com/in/johndoe": {
            "first_name": "John",
            "last_name": "Doe",
            "url": "https://www.linkedin.com/in/johndoe/",
            "email": "",
            "company": "Old Company",
            "position": "Old Position",
            "connected_on": "2023-01-15",
            "_meta": {"source": "linkedin_export"},
        }
    }
    new_records = {
        "linkedin.com/in/johndoe": {
            "first_name": "John",
            "last_name": "Doe",
            "url": "https://www.linkedin.com/in/johndoe/",
            "email": "",
            "company": "New Company",
            "position": "New Position",
            "connected_on": "2023-01-15",
            "_meta": {"source": "linkedin_export"},
        }
    }
    result = merge_connections(existing, new_records)
    assert result["linkedin.com/in/johndoe"]["company"] == "New Company"
    assert result["linkedin.com/in/johndoe"]["position"] == "New Position"


def test_merge_connections_preserves_user_fields():
    """merge_connections never overwrites user_ prefixed fields."""
    existing = {
        "linkedin.com/in/johndoe": {
            "first_name": "John",
            "last_name": "Doe",
            "url": "https://www.linkedin.com/in/johndoe/",
            "email": "",
            "company": "Acme",
            "position": "Engineer",
            "connected_on": "2023-01-15",
            "_meta": {"source": "linkedin_export"},
            "user_phone": "+1-555-0100",
            "user_notes": "Met at conference",
            "user_email": "john.private@gmail.com",
        }
    }
    new_records = {
        "linkedin.com/in/johndoe": {
            "first_name": "John",
            "last_name": "Doe",
            "url": "https://www.linkedin.com/in/johndoe/",
            "email": "",
            "company": "New Corp",
            "position": "Manager",
            "connected_on": "2023-01-15",
            "_meta": {"source": "linkedin_export"},
        }
    }
    result = merge_connections(existing, new_records)
    assert result["linkedin.com/in/johndoe"]["user_phone"] == "+1-555-0100"
    assert result["linkedin.com/in/johndoe"]["user_notes"] == "Met at conference"
    assert result["linkedin.com/in/johndoe"]["user_email"] == "john.private@gmail.com"
    assert result["linkedin.com/in/johndoe"]["company"] == "New Corp"
