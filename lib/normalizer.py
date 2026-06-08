"""URL normalization for LinkedIn profile URLs.

Provides a single canonical form used as the store key throughout all phases.
"""
import re


def normalize_linkedin_url(url: str) -> str:
    """Return canonical form of a LinkedIn profile URL for use as a store key.

    Pipeline: strip whitespace, lowercase, strip scheme + www., strip trailing slash.

    Examples:
        normalize_linkedin_url("https://www.linkedin.com/in/johndoe/") == "linkedin.com/in/johndoe"
        normalize_linkedin_url("http://LinkedIn.com/in/JohnDoe") == "linkedin.com/in/johndoe"
        normalize_linkedin_url("") == ""
    """
    if not url:
        return ""
    url = url.strip().lower()
    url = re.sub(r'^https?://(www\.)?', '', url)
    url = url.rstrip('/')
    return url
