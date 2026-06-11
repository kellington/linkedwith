---
description: Generate a dated HTML status page (project/status/status-YYYY-MM-DD.html) summarising linkedwith — what it does, how to run it, last-used data, current test status, and any v1.1 ideas worth considering.
---

Generate a project status HTML report for linkedwith.

## What to read first (do all reads in parallel)

1. `README.md` — purpose, how to run, contact_info.csv format
2. `CLAUDE.md` — full project context: tech stack, constraints, key patterns, what NOT to use
3. `project/diary/` — list files, read all diary entries (a few short entries)
4. Run `git log --oneline -8` for recent commits
5. Run `ls data/LinkedIn/ 2>/dev/null || echo "no data dir"` to find the current export ZIP
6. Run `ls lib/` to confirm which library modules exist
7. Run `cd /Users/rob/Documents/GitHub/Rob/linkedwith && python -m pytest --tb=no -q 2>/dev/null | tail -3` to check current test count/status

## Output

Create a single self-contained HTML file at:

```
project/status/status-YYYY-MM-DD.html
```

where `YYYY-MM-DD` is today's date. No external dependencies — all CSS and SVG inline.

## Section order and content

The page answers: "What does this tool do, how do I run it, and is it still working?"

### 1. Header bar
- Tool name: **LinkedWith**
- Tagline: Turn LinkedIn exports into a sortable, offline-ready contact list
- Type badge: "Personal Utility — Run When Needed"
- Status badge: derive from test results — green "86/86 Tests Passing" if clean, amber if degraded
- Current date
- Palette: LinkedIn blue `#0077b5` + slate `#1e293b` + green `#16a34a` — clean, minimal

### 2. Snapshot pills
- Language: Python 3.13+ (uv managed)
- Output: `output/LinkedWith.HTML` — self-contained, offline, iPhone-compatible
- Tests: derive from pytest output (was 86/86 at last known state)
- Last data export: derive from `ls data/LinkedIn/` — show the zip filename and its date
- Last code change: derive from `git log --oneline -1`

### 3. Purpose — One Paragraph
From CLAUDE.md:
"LinkedWith parses a LinkedIn data export ZIP into an enriched, sortable HTML contact list. It combines connections, message history, and user-provided contact info (email, phone, notes) into a single self-contained HTML page — viewable offline and on iPhone via an HTML Preview app. The goal: turn frustrating LinkedIn data into a simple contact list enriched with interaction history and personal notes."

### 4. What It Builds

A single-column description of what one run produces:
- Reads `Connections.csv`, `messages.csv` from the LinkedIn ZIP
- Merges `data/contact_info.csv` (user's own email/phone/notes)
- Writes `data/linkedwith.json` — the enriched data store (persists across runs)
- Generates `output/LinkedWith.HTML` — 9-column sortable table, inline CSS/JS, no internet required

Columns in the output HTML:
| Column | Source |
|---|---|
| First Name | connections |
| Last Name | connections |
| Company | connections |
| Position | connections |
| Connected On | connections — default sort descending |
| Most Recent Message | messages |
| Email | contact_info.csv |
| Phone | contact_info.csv |
| Notes | contact_info.csv |

### 5. How to Run (quick reference)

This is the most important section for this utility — what to do when a new export arrives.

**Step 1: Download fresh LinkedIn data**
- Settings & Privacy → Data Privacy → Get a copy of your data → "Download larger data archive"
- Takes ~15 minutes for initial files; message history can take longer

**Step 2: Drop the ZIP into `data/LinkedIn/`**
```
mv ~/Downloads/Complete_LinkedInDataExport_*.zip data/LinkedIn/
```

**Step 3: Run**
```bash
uv run python linkedwith.py data/LinkedIn/<zip-filename>.zip
```
or equivalently:
```bash
python linkedwith.py data/LinkedIn/<zip-filename>.zip
```

**Step 4: Open the output**
```
open output/LinkedWith.HTML   # Mac
```
Or copy to iPhone and open with "HTML Preview" app.

**Optional: Add contact info**
Edit `data/contact_info.csv` (columns: URL, First Name, Last Name, Email, Phone, Notes). URL is the preferred match key. Re-run to merge.

**Tests:**
```bash
uv run pytest
```

### 6. Library Modules
Derive from `ls lib/` output. Describe each briefly:

| Module | Role |
|---|---|
| `extractor.py` | Unzip and read LinkedIn export files |
| `parsers.py` | Parse Connections.csv and messages.csv |
| `normalizer.py` | Normalize profile URLs, names, dates |
| `messages.py` | Derive most-recent-message date per connection |
| `contacts.py` | Merge contact_info.csv with store |
| `store.py` | Read/write linkedwith.json atomically |
| `renderer.py` | Jinja2 template → LinkedWith.HTML |
| `config.py` | Configuration constants |

### 7. Current Data State

Derive from `ls data/LinkedIn/`:
- Latest export ZIP: name and implied date
- Note if the export is recent (within 60 days) or stale (over 90 days)

If no data found, show: "No LinkedIn export found in data/LinkedIn/ — download from linkedin.com/mypreferences/d/download-my-data before running."

### 8. V1.1 Ideas (optional next steps)
Pull from `project/ideas/` — there are a few idea files about more advanced network analysis. Summarize as a short list of potential improvements:

From the ideas files:
- **Relationship decay scoring** — model how connections go "cold" over time (half-life model based on message frequency, shared history)
- **Reciprocity debt ledger** — flag who you owe a message vs. who owes you
- **Warm path discovery** — find mutual connections to reach a target person
- **Network intelligence dashboard** — 6-analysis prompt for deeper one-time analysis runs

Frame these as "ideas, not commitments" — v1.0 is the useful thing; these are enhancements if a business use case emerges.

### 9. Known Constraints
From CLAUDE.md — keep this as a permanent reference:

- **iPhone output**: HTML must be self-contained — no CDN, no external fonts, no external JS. Break this and it stops working on mobile.
- **UTF-8 BOM**: LinkedIn exports use UTF-8-sig encoding. Always open CSVs with `encoding="utf-8-sig"` or column lookups silently break.
- **Incremental updates**: Re-running preserves user-added fields (email, phone, notes) — the store is append/merge, not replace.
- **"No longer in LinkedIn export" message**: Informational only — contacts are not deleted from the store even if they've disappeared from LinkedIn.
- **No database**: Flat JSON store is intentional — no schema migrations, no DB overhead for a personal single-user tool.

### 10. Footer
"Generated YYYY-MM-DD · LinkedWith · Personal Python utility · derived from README.md, CLAUDE.md, diary, git log"

## Visual style

- Background: `#f9fafb`; cards: white with `1px solid #e5e7eb` and light shadow
- Palette: LinkedIn blue `#0077b5`, slate `#1e293b`, green `#16a34a`, amber `#d97706`
- Header: slim slate bar with blue accent — clean, utility feel
- Test status pill: green if passing, amber if degraded — derived from actual pytest output
- "How to Run" section: code block style, prominent — this is the most-used workflow
- Library modules table: compact, grey — reference only
- V1.1 ideas: small amber-left-border card — aspirational, not committed
- Constraints: red-left-border cards — real gotchas worth remembering
- Keep the page compact — this is a run-when-needed utility, not a product

## Rules

- Write the file directly — do not ask for confirmation first
- Run pytest to get the actual current test count — don't assume 86/86 is still correct
- Check `ls data/LinkedIn/` to find the actual export filename — don't hardcode it
- The "How to Run" section is the most valuable thing on the page — make it clear and complete
- After writing the file, confirm the path and list the sections included

## Also write STATUS-SUMMARY.md

After writing the HTML file, write (or overwrite) a summary file at `project/status/STATUS-SUMMARY.md` (create the directory if it doesn't exist).

Use this exact format — YAML frontmatter only, no markdown body:

```
---
name: LinkedWith
tagline: <one sentence — what this project is, derived from the files you just read>
group: Utilities
profile: Utility
priority: 11
status: <one sentence — the most important thing about current state right now>
generated: <today's date YYYY-MM-DD>
---
```

- `tagline`: purpose of the project — stable, changes rarely
- `status`: current state — stable/active/last run date
- Overwrite every run — no date suffix, always one file
