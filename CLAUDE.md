# LinkedWith

## Sensitivity

Public repo; contact data is PII. Never commit exports, enriched data or
generated contact HTML; status pages and summaries stay aggregate-only (counts,
never names).

## METADATA
- LinkedIn does not provide an official "metadata page" detailing all export files and CSV column structures. Users typically explore the files manually after download.

Official Documentation
- The primary resource is LinkedIn's help page on downloading account data, which lists available files
- See @project/LinkedIn-metadata.md

- There is **no** official column level documentation
 - Self-discovery is expected—open CSVs in a spreadsheet tool to view headers like "Post Timestamp," "Text," "URL," or "First Name" in connections.
- Practical Tips: Extract the ZIP fully and review README.txt or file headers first.

## Project

**LinkedWith**

A personal LinkedIn data tool that parses exported LinkedIn data (ZIP download) into an enriched, sortable HTML contact list. It combines connection data with message history and user-provided contact info (email, phone, notes) into a single self-contained HTML page viewable on mobile via an HTML preview app.

**Core Value:** Turn frustrating LinkedIn data into a simple, sortable contact list enriched with interaction history and personal notes — accessible offline on any device.

### Constraints

- **Output format**: Single self-contained HTML file (no external dependencies, works offline)
- **Implementation**: Python script, wrapped as a Claude Skill for easy invocation
- **Data store**: Simple flat file (CSV or JSON) — no database
- **Input**: Standard LinkedIn data export ZIP format
- **Platform**: Must produce HTML viewable on iPhone via HTML Preview app

## Technology Stack

### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ (3.14.3 current stable) | Runtime | pandas 3.x requires Python >=3.11; 3.13+ recommended for stdlib improvements to zipfile/pathlib; no third-party runtime needed |
| zipfile (stdlib) | Built-in | Extract LinkedIn ZIP | Standard library, no install, handles ZipFile.open() for in-memory reads without extracting to disk — correct for this tool |
| csv (stdlib) | Built-in | Parse CSV files | Standard library; handles LinkedIn's UTF-8-sig BOM encoding when opened with `encoding="utf-8-sig"` — critical for correct column reads |
| json (stdlib) | Built-in | Flat file data store | Standard library; `json.dump()` / `json.load()` is the idiomatic Python pattern for simple key-value persistence with no DB overhead |
| Jinja2 | 3.1.6 (current) | HTML generation | Industry standard for Python HTML templating; `Environment.from_string()` enables inline template storage — no template files needed; supports loops, conditionals, filters; single dependency |

### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib (stdlib) | Built-in | File path handling | Use `Path` objects throughout — eliminates OS path separator bugs, cleaner than `os.path`, handles ZIP extraction paths correctly |
| datetime (stdlib) | Built-in | Date parsing and sorting | Parse "Connected On" and message timestamps for sort keys; `datetime.strptime()` handles LinkedIn's date formats |
| argparse (stdlib) | Built-in | CLI interface for script | Single ZIP input + optional flags; stdlib means zero extra dependencies; Claude Skill invokes via `python linkedwith.py <zip_path>` |

### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Dependency management and virtual environments | Fastest Python toolchain in 2025; replaces pip + venv; `uv run linkedwith.py` handles env automatically |
| ruff | Linting and formatting | Single tool replaces flake8 + black + isort; zero config by default; fast |

### What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| pandas | Overkill for two small CSVs; requires Python 3.11+; 30MB install; no benefit over stdlib csv for this data shape | stdlib `csv.DictReader` |
| jQuery / DataTables | Requires CDN or bundled JS; breaks offline/mobile constraint; ~90KB minified for table sorting that 30 lines of vanilla JS solves | Vanilla JS sort (inline in Jinja2 template) |
| SQLite / any DB | Adds schema migration complexity for a single-user flat-file tool | stdlib `json` |
| Flask / FastAPI | This tool generates a static file — no server needed | Jinja2 standalone |
| `open(file, encoding="utf-8")` for LinkedIn CSVs | LinkedIn exports ship with UTF-8 BOM. Using `utf-8` instead of `utf-8-sig` causes the BOM to appear in the first column header, silently breaking column lookups. | `open(file, encoding="utf-8-sig")` |

### Key Patterns
- Embed all CSS and JavaScript as `<style>` and `<script>` blocks inside the Jinja2 template — no external requests
- Embed the connections as a single JSON array (`const ROWS = [...]`) and draw the page client-side; the Jinja2 template holds only the shell
- Escape `<`, `>` and `&` as `\u` sequences in that JSON so no field can close the `<script>` block, and pass it through `|safe` (autoescape would otherwise mangle the JSON)
- Search, facet chips, year filter and sorting are vanilla JS over that array (no libraries); each row gets one prebuilt lowercased haystack so keystroke filtering never re-joins strings
- Two views over the same pipeline: cards (mobile) and a sortable table (desktop)
- Blank values always sort last, in both directions
- Default sort is "Connected On" descending
- Key each contact by their LinkedIn profile URL (unique, stable identifier)
- Merge new connections — update fields if changed, preserve user-added fields (email, phone, notes)
- Write updated store back atomically (write to `.tmp`, then rename)

## Project status

Run `/project-status` (global skill, `~/.claude/skills/project-status/`). Metadata
comes from the workspace README; repo config is below.

```yaml
name: LinkedWith
sensitivity: pii
never_read:
  - data/
  - output/
extra_sources:
  - README.md
  - project/ideas/*.md
palette: { primary: "#1e293b", accent: "#0077b5" }
custom_sections: |
  - Health = current pytest result (`uv run pytest --tb=no -q | tail -3`), never the last recorded count.
  - Data state: newest export zip in data/ by name and date only (`ls`), plus older zips as delete candidates; fresh ≤60 days, stale >90. No store contents.
  - Library modules table from `ls lib/`. Ideas from project/ideas/ framed "ideas, not commitments".
```

## Project Reference

### How to run (when a new export arrives)

1. **Request the export:** LinkedIn → Settings & Privacy → Data Privacy → Get a
   copy of your data → "Download larger data archive" (~15 min; messages can take
   longer). The "Basic" archive also has `Connections.csv` + `messages.csv`, which
   is enough.
2. **Drop the ZIP into `data/`:** `mv ~/Downloads/*_LinkedInDataExport_*.zip data/`
3. **Run:** `uv run python linkedwith.py data/<zip-filename>.zip` — or invoke the
   `/linkedwith` Claude Skill (`.claude/skills/linkedwith/`).
4. **Open the output:** `open output/LinkedWith.HTML` (Mac), or copy to iPhone and
   open in the "HTML Preview" app.

**Optional contact info:** edit `data/contact_info.csv` (columns: URL, First Name,
Last Name, Email, Phone, Notes; all optional per row). Match order: normalized URL
first, then case-insensitive First + Last name (skipped with a warning on 0 or 2+
matches). Re-run to merge; stored as `user_email` / `user_phone` / `user_notes`.

**Paths** (overridable via env, see `lib/config.py`): store `data/linkedwith.json`,
contact info `data/contact_info.csv`, output `output/LinkedWith.HTML`. All gitignored.

### Tests

`uv run pytest`

### Local preview tip

The Chrome tool can't open `file://` URLs. To eyeball a page, serve its folder with
`python3 -m http.server <free port> --bind 127.0.0.1` (8765 is often taken), then
stop the server and close the tab.

Constraints are under "Project → Constraints" above.
