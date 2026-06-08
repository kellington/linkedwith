"""Tests for lib.extractor: find_csv_in_zip, open_csv_in_zip"""
import io
import zipfile
from pathlib import Path

import pytest

from lib.extractor import find_csv_in_zip, open_csv_in_zip


def test_find_csv_in_zip_case_exact(sample_zip_path):
    """Finds Connections.csv with exact case."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = find_csv_in_zip(zf, "Connections.csv")
    assert result is not None
    assert result.lower().endswith("connections.csv")


def test_find_csv_in_zip_case_lower(tmp_path):
    """Finds connections.csv (lowercase) via case-insensitive lookup."""
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("connections.csv", "First Name\nJohn\n")
    with zipfile.ZipFile(zip_path) as zf:
        result = find_csv_in_zip(zf, "Connections.csv")
    assert result == "connections.csv"


def test_find_csv_in_zip_case_upper(tmp_path):
    """Finds CONNECTIONS.CSV (uppercase) via case-insensitive lookup."""
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("CONNECTIONS.CSV", "First Name\nJohn\n")
    with zipfile.ZipFile(zip_path) as zf:
        result = find_csv_in_zip(zf, "Connections.csv")
    assert result == "CONNECTIONS.CSV"


def test_find_csv_in_zip_subdirectory(tmp_path):
    """Finds CSV in a subdirectory."""
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("export_data/Connections.csv", "First Name\nJohn\n")
    with zipfile.ZipFile(zip_path) as zf:
        result = find_csv_in_zip(zf, "Connections.csv")
    assert result == "export_data/Connections.csv"


def test_find_csv_in_zip_returns_none(sample_zip_path):
    """Returns None when target CSV is not in ZIP."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        result = find_csv_in_zip(zf, "NonExistent.csv")
    assert result is None


def test_open_csv_in_zip_returns_text_wrapper(sample_zip_path):
    """open_csv_in_zip returns a TextIOWrapper."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        csv_name = find_csv_in_zip(zf, "Connections.csv")
        wrapper = open_csv_in_zip(zf, csv_name)
    assert isinstance(wrapper, io.TextIOWrapper)


def test_open_csv_in_zip_no_bom_in_first_line(sample_zip_path):
    """First line from open_csv_in_zip does not start with BOM character."""
    with zipfile.ZipFile(sample_zip_path) as zf:
        csv_name = find_csv_in_zip(zf, "Connections.csv")
        wrapper = open_csv_in_zip(zf, csv_name)
        first_line = wrapper.readline()
    assert not first_line.startswith("\ufeff"), f"BOM found in first line: {repr(first_line)}"
