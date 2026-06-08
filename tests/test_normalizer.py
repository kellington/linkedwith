"""Tests for lib.normalizer.normalize_linkedin_url"""
import pytest
from lib.normalizer import normalize_linkedin_url


def test_https_www_trailing_slash():
    assert normalize_linkedin_url("https://www.linkedin.com/in/johndoe/") == "linkedin.com/in/johndoe"


def test_http_mixed_case():
    assert normalize_linkedin_url("http://LinkedIn.com/in/JohnDoe") == "linkedin.com/in/johndoe"


def test_no_scheme_trailing_slash():
    assert normalize_linkedin_url("linkedin.com/in/johndoe/") == "linkedin.com/in/johndoe"


def test_empty_string():
    assert normalize_linkedin_url("") == ""


def test_whitespace_stripped():
    assert normalize_linkedin_url("  https://www.linkedin.com/in/test  ") == "linkedin.com/in/test"


def test_https_no_www():
    assert normalize_linkedin_url("https://linkedin.com/in/testuser/") == "linkedin.com/in/testuser"


def test_no_trailing_slash_no_scheme():
    assert normalize_linkedin_url("linkedin.com/in/notrailingslash") == "linkedin.com/in/notrailingslash"


def test_idempotent():
    url = "linkedin.com/in/johndoe"
    assert normalize_linkedin_url(url) == normalize_linkedin_url(normalize_linkedin_url(url))
