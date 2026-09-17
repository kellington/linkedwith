---
description: Generate a dated HTML status page (project/status/status-YYYY-MM-DD.html) summarising linkedwith — what it does, how to run it, last-used data, current test status, and any next-step ideas worth considering.
---

Generate a project status HTML report for linkedwith.

## What to read first (do all reads in parallel)

1. `README.md` — purpose, how to run, contact_info.csv format
2. `CLAUDE.md` — full project context: tech stack, constraints, key patterns, what NOT to use
3. `project/diary/` — list files, read all diary entries (a few short entries)
4. Run `git log --oneline -8` for recent commits
5. Run `ls -la data/*.zip 2>/dev/null || echo "no export found"` to find export ZIPs (they live directly in `data/`; names often end `.zip.zip`; pick the newest by the MM-DD-YYYY in the name)
6. Run `ls lib/` to confirm which library modules exist
7. Run `cd /Users/rob/Documents/GitHub/Rob/linkedwith && uv run pytest --tb=no -q 2>&1 | tail -3` to check current test count/status
8. Run `python3 -c "import json;d=json.load(open('data/linkedwith.json'));r=[v for v in d.values() if isinstance(v,dict)];print(len(r),'connections',sum(1 for x in r if x.get('most_recent_message')),'messaged',sum(1 for x in r if x.get('user_email') or x.get('user_phone') or x.get('user_notes')),'user-enriched')"` for store counts

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
- Status badge: derive from test results — green "N/N Tests Passing" if clean (N from pytest), amber if degraded
- Current date
- Palette: LinkedIn blue `#0077b5` + slate `#1e293b` + green `#16a34a` — clean, minimal

### 2. Snapshot pills
- Language: Python 3.13+ (uv managed)
- Output: `output/LinkedWith.HTML` — self-contained, offline, iPhone-compatible
- Tests: derive from pytest output (was 96/96 at 2026-09-17)
- Last data export: derive from `ls data/*.zip` — show the zip filename and its date
- Last code change: derive from `git log --oneline -1`

### 3. Purpose — One Paragraph
From CLAUDE.md:
"LinkedWith parses a LinkedIn data export ZIP into an enriched, sortable HTML contact list. It combines connections, message history, and user-provided contact info (email, phone, notes) into a single self-contained HTML page — viewable offline and on iPhone via an HTML Preview app. The goal: turn frustrating LinkedIn data into a simple contact list enriched with interaction history and personal notes."

### 4. What It Builds

A single-column description of what one run produces:
- Reads `Connections.csv`, `messages.csv` from the LinkedIn ZIP
- Merges `data/contact_info.csv` (user's own email/phone/notes)
- Writes `data/linkedwith.json` — the enriched data store (persists across runs)
- Generates `output/LinkedWith.HTML` — inline CSS/JS, no internet required, light/dark aware

Page features (check `lib/renderer.py` / README in case they changed): search (multi-word AND, highlighted, `/` to focus), filter chips *Messaged* / *Notes* / *Email / phone*, connection-year dropdown, **Cards** view (phone) and **Table** view (sortable, sticky header), blanks sort last.

Table-view columns (verify against `COLS` in `lib/renderer.py`):
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

**Step 2: Drop the ZIP into `data/`**
```
mv ~/Downloads/*_LinkedInDataExport_*.zip data/
```

**Step 3: Run**
```bash
uv run python linkedwith.py data/<zip-filename>.zip
```
or equivalently:
```bash
python linkedwith.py data/<zip-filename>.zip
```

**Step 4: Open the output**
```
open output/LinkedWith.HTML   # Mac
```
Or copy to iPhone and open with "HTML Preview" app.

Also mention `/linkedwith` (Claude Skill) and show the last-run command with the actual newest ZIP name. Note the "Basic" archive also contains `Connections.csv` + `messages.csv` — enough for this tool.

**Optional: Add contact info**
Edit `data/contact_info.csv` (columns: URL, First Name, Last Name, Email, Phone, Notes). All columns optional per row. Match order: normalized URL first, then case-insensitive First + Last name (skipped with warning on 0 or 2+ matches). Re-run to merge; stored as `user_email` / `user_phone` / `user_notes`.

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

Derive from `ls data/*.zip` and the store counts (step 8):
- Latest export ZIP: name and implied date
- Connections / messaged / user-enriched counts; store + HTML last-written time
- List older ZIPs still in `data/` (candidates to delete)
- Note if the export is recent (within 60 days) or stale (over 90 days)

If no data found, show: "No LinkedIn export found in data/ — download from linkedin.com/mypreferences/d/download-my-data before running."

### 8. Next-step Ideas (optional)
Pull from `project/ideas/` — there are a few idea files about more advanced network analysis. Summarize as a short list of potential improvements:

From the ideas files:
- **Relationship decay scoring** — model how connections go "cold" over time (half-life model based on message frequency, shared history)
- **Reciprocity debt ledger** — flag who you owe a message vs. who owes you
- **Warm path discovery** — find mutual connections to reach a target person
- **Network intelligence dashboard** — 6-analysis prompt for deeper one-time analysis runs
- **Feed contact-merge** — pull LinkedWith data into the contact-merge project (diary 2026-08-19)

Also scan recent diary entries for any newer ideas.

Frame these as "ideas, not commitments" — the current version is the useful thing; these are enhancements if a business use case emerges.

### 9. Known Constraints
From CLAUDE.md — keep this as a permanent reference:

- **iPhone output**: HTML must be self-contained — no CDN, no external fonts, no external JS. Break this and it stops working on mobile.
- **UTF-8 BOM**: LinkedIn exports use UTF-8-sig encoding. Always open CSVs with `encoding="utf-8-sig"` or column lookups silently break.
- **Incremental updates**: Re-running preserves user-added fields (email, phone, notes) — the store is append/merge, not replace.
- **"No longer in LinkedIn export" message**: Informational only — contacts are not deleted from the store even if they've disappeared from LinkedIn.
- **No database**: Flat JSON store is intentional — no schema migrations, no DB overhead for a personal single-user tool.
- **Public repo**: `data/`, `output/`, `*.zip`, `*.csv` are git-ignored. Never commit exports or generated HTML (audited clean 2026-09-10).

### 10. Footer
"Generated YYYY-MM-DD · LinkedWith · Personal Python utility · derived from README.md, CLAUDE.md, diary, git log, pytest, data/"

## Visual style

- Background: `#f9fafb`; cards: white with `1px solid #e5e7eb` and light shadow
- Palette: LinkedIn blue `#0077b5`, slate `#1e293b`, green `#16a34a`, amber `#d97706`
- Header: slim slate bar with blue accent — clean, utility feel
- Test status pill: green if passing, amber if degraded — derived from actual pytest output
- "How to Run" section: code block style, prominent — this is the most-used workflow
- Library modules table: compact, grey — reference only
- Next-step ideas: small amber-left-border card — aspirational, not committed
- Constraints: red-left-border cards — real gotchas worth remembering
- Keep the page compact — this is a run-when-needed utility, not a product
- Must work at phone width: 16px gutters, `overflow-x: auto` on `pre` and tables, two-column grids collapse to one

## Rules

- Write the file directly — do not ask for confirmation first
- Run pytest to get the actual current test count — don't assume the last count is still correct
- Check `ls data/*.zip` to find the actual export filename — don't hardcode it
- The "How to Run" section is the most valuable thing on the page — make it clear and complete
- `file://` URLs can't be opened by the Chrome tool — to eyeball the page, serve `project/status/` with `python3 -m http.server <free port> --bind 127.0.0.1` (8765 is often taken), then stop the server and close the tab
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
