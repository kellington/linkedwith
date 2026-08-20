"""Tests for lib.renderer: render_html output correctness.

The page is data-driven — rows are embedded as a JSON array and drawn by the
inline script — so most assertions parse that array back out rather than
scraping markup.
"""
import json

from lib.renderer import _json_for_script, _rows_from_store, render_html


def _make_store():
    """Build a minimal 3-record store dict for testing."""
    return {
        "linkedin.com/in/alice": {
            "first_name": "Alice",
            "last_name": "Smith",
            "url": "https://www.linkedin.com/in/alice",
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
            "url": "https://www.linkedin.com/in/bob",
            "company": "AT&T",
            "position": "Manager",
            "connected_on": "2023-11-20",
            "most_recent_message": None,
            # No user_email, user_phone, user_notes keys at all
        },
        "linkedin.com/in/carol": {
            "first_name": "Carol",
            "last_name": "Jones",
            "url": "https://www.linkedin.com/in/carol",
            "company": "StartupCo",
            "position": "CEO",
            "connected_on": "2024-03-10",
            "most_recent_message": "2024-05-15",
            "email": "carol@linkedin-supplied.com",
            "user_email": "",
            "user_phone": "",
            "user_notes": "",
        },
    }


def _render(tmp_path, store=None, **kwargs):
    """Render a store and return the HTML text."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(store if store is not None else _make_store(), output, **kwargs)
    return output.read_text(encoding="utf-8")


def _embedded_rows(html):
    """Parse the ROWS array back out of the inline script.

    json.dumps emits no newlines, so the assignment is exactly one line.
    """
    line = next(ln for ln in html.splitlines() if ln.startswith("const ROWS = "))
    return json.loads(line[len("const ROWS = "):].rstrip(";"))


# --- file mechanics -------------------------------------------------------

def test_render_creates_file(tmp_path):
    """render_html creates an HTML file at the given path."""
    output = tmp_path / "LinkedWith.HTML"
    render_html(_make_store(), output)
    assert output.exists()


def test_html_contains_doctype(tmp_path):
    """Output starts with <!DOCTYPE html>."""
    assert _render(tmp_path).strip().startswith("<!DOCTYPE html>")


def test_atomic_write_no_tmp_leftover(tmp_path):
    """After render_html completes, no .tmp file remains alongside the output."""
    render_html(_make_store(), tmp_path / "LinkedWith.HTML")
    assert not (tmp_path / "LinkedWith.HTML.tmp").exists()


def test_empty_store_renders(tmp_path):
    """A store with no records still produces a valid page with an empty array."""
    html = _render(tmp_path, store={})
    assert _embedded_rows(html) == []
    assert "0 connections" in html.replace("\n", " ")


# --- self-contained / offline --------------------------------------------

def test_inline_style_tag(tmp_path):
    """Output contains <style> and </style> tags."""
    html = _render(tmp_path)
    assert "<style>" in html and "</style>" in html


def test_inline_script_tag(tmp_path):
    """Output contains <script> and </script> tags."""
    html = _render(tmp_path)
    assert "<script>" in html and "</script>" in html


def test_no_external_resource_loads(tmp_path):
    """Nothing is fetched from the network — no CDN, no stylesheet, no image, no XHR.

    Profile/mailto/tel hrefs are links the user taps, not loads, so they are fine;
    this guards the offline constraint, which is about requests the page makes.
    """
    html = _render(tmp_path)
    for forbidden in ["<link", "<img", "<script src", "src=", "@import", "fetch(",
                      "XMLHttpRequest", "//cdn", "googleapis"]:
        assert forbidden not in html, f"external resource reference found: {forbidden}"


def test_only_linkedin_urls_present(tmp_path):
    """The only absolute URLs in the file are the connections' own profile links."""
    html = _render(tmp_path)
    for chunk in html.split("https://")[1:]:
        assert chunk.startswith("www.linkedin.com/in/"), f"unexpected URL: https://{chunk[:40]}"
    assert "http://" not in html


def test_viewport_meta(tmp_path):
    """Output contains viewport meta tag for mobile rendering."""
    html = _render(tmp_path)
    assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html


# --- embedded data --------------------------------------------------------

def test_all_rows_embedded(tmp_path):
    """A 3-record store embeds 3 rows."""
    assert len(_embedded_rows(_render(tmp_path))) == 3


def test_row_fields(tmp_path):
    """Each row carries the fields the UI draws and sorts on."""
    rows = {r["first"]: r for r in _embedded_rows(_render(tmp_path))}
    alice = rows["Alice"]
    assert alice == {
        "first": "Alice", "last": "Smith", "company": "Acme Corp",
        "position": "Engineer", "connected": "2024-01-15", "msg": "2024-06-01",
        "email": "alice@example.com", "phone": "555-0101",
        "notes": "Met at conference", "url": "https://www.linkedin.com/in/alice",
    }


def test_missing_user_fields_become_empty_strings(tmp_path):
    """A record with no user_* keys at all renders empty strings, never None."""
    rows = {r["first"]: r for r in _embedded_rows(_render(tmp_path))}
    bob = rows["Bob"]
    assert bob["email"] == "" and bob["phone"] == "" and bob["notes"] == ""


def test_null_most_recent_message_becomes_empty(tmp_path):
    """most_recent_message=None becomes "" so the JS blanks-last sort sees a falsy value."""
    rows = {r["first"]: r for r in _embedded_rows(_render(tmp_path))}
    assert rows["Bob"]["msg"] == ""


def test_no_literal_none_in_output(tmp_path):
    """The string 'None' never leaks into the rendered page."""
    assert "None" not in _render(tmp_path)


def test_user_email_preferred_over_linkedin_email(tmp_path):
    """user_email wins when set; the LinkedIn-supplied address is the fallback."""
    rows = {r["first"]: r for r in _embedded_rows(_render(tmp_path))}
    assert rows["Alice"]["email"] == "alice@example.com"
    # Carol's user_email is blank, so the LinkedIn address shows instead.
    assert rows["Carol"]["email"] == "carol@linkedin-supplied.com"


def test_special_chars_survive_round_trip(tmp_path):
    """Apostrophes and ampersands reach the browser as their original characters."""
    rows = {r["first"]: r for r in _embedded_rows(_render(tmp_path))}
    assert rows["Bob"]["last"] == "O'Brien"
    assert rows["Bob"]["company"] == "AT&T"


def test_angle_brackets_escaped_in_json(tmp_path):
    """<, > and & are emitted as \\u escapes so no data can close the script block."""
    html = _render(tmp_path)
    assert "\\u0026" in html, "& should be \\u0026-escaped inside the ROWS array"
    rows_line = next(ln for ln in html.splitlines() if ln.startswith("const ROWS = "))
    assert "&" not in rows_line and "<" not in rows_line and ">" not in rows_line


def test_script_close_in_data_cannot_break_out(tmp_path):
    """A note containing </script> is escaped, not emitted literally."""
    store = _make_store()
    payload = "</script><script>alert('xss')</script>"
    store["linkedin.com/in/alice"]["user_notes"] = payload
    html = _render(tmp_path, store)
    # Exactly one closing script tag — the real one.
    assert html.count("</script>") == 1
    rows = {r["first"]: r for r in _embedded_rows(html)}
    assert rows["Alice"]["notes"] == payload


def test_json_for_script_escapes():
    """_json_for_script neutralises the three characters that can end a script block."""
    out = _json_for_script([{"x": "a<b>c&d"}])
    assert out == '[{"x": "a\\u003cb\\u003ec\\u0026d"}]'


def test_rows_from_store_handles_empty_record():
    """A record with no fields at all yields a fully-blank row rather than KeyErrors."""
    row = _rows_from_store({"k": {}})[0]
    assert set(row) == {"first", "last", "company", "position", "connected",
                        "msg", "email", "phone", "notes", "url"}
    assert all(v == "" for v in row.values())


# --- UI controls ----------------------------------------------------------

def test_search_input_present(tmp_path):
    """The page has the search box the filter pipeline reads from."""
    html = _render(tmp_path)
    assert 'id="q"' in html and 'type="search"' in html


def test_filter_and_sort_controls_present(tmp_path):
    """Facet chips, the year filter, the sort menu and the view toggle all render."""
    html = _render(tmp_path)
    for control in ['id="chips"', 'id="year"', 'id="sort"', 'id="views"',
                    'data-v="cards"', 'data-v="table"']:
        assert control in html, f"missing control: {control}"


def test_facets_defined(tmp_path):
    """The three facets are wired up in the script."""
    html = _render(tmp_path)
    for facet in ["msg:", "notes:", "contact:"]:
        assert facet in html
    for label in ["Messaged", "Notes", "Email / phone"]:
        assert label in html


def test_table_columns_present(tmp_path):
    """Every table column is declared, in order."""
    html = _render(tmp_path)
    columns = ["First", "Last", "Company", "Position", "Connected",
               "Last message", "Email", "Phone", "Notes"]
    positions = [html.index("t: '" + c + "'") for c in columns]
    assert positions == sorted(positions), "table columns not in expected order"


def test_default_sort_is_connected_newest(tmp_path):
    """The page opens sorted by connection date, newest first."""
    html = _render(tmp_path)
    assert "key: 'connected', dir: -1" in html


def test_connection_count_display(tmp_path):
    """Output shows the total connection count."""
    html = " ".join(_render(tmp_path).split())
    assert '<b id="shown">3</b> of 3 connections' in html


def test_linkedin_date_shown_when_given(tmp_path):
    """The source export date appears in the subtitle when supplied."""
    assert "LinkedIn data from 2026-08-18" in _render(tmp_path, linkedin_date="2026-08-18")


def test_linkedin_date_omitted_when_blank(tmp_path):
    """No dangling subtitle fragment when no export date is known."""
    assert "LinkedIn data from" not in _render(tmp_path)
