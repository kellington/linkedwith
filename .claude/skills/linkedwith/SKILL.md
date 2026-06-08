---
name: linkedwith
description: "Run the LinkedWith pipeline: parse a LinkedIn data export ZIP, merge contact info, and generate a sortable HTML contact list (LinkedWith.HTML). Use when the user wants to process their LinkedIn data, update their contacts, or regenerate the HTML output."
---

# LinkedWith

## When to Use

- User says "run linkedwith" or asks to process their LinkedIn data
- User provides a path to a LinkedIn data export ZIP file
- User wants to update or regenerate LinkedWith.HTML

## Instructions

1. **Get the ZIP path** — if the user has not provided a path, auto-detect the latest export:
   ```
   python -c "
   import re
   from pathlib import Path
   files = list(Path('/Users/rob/Documents/GitHub/Rob/linkedwith/data/LinkedIn').glob('*.zip'))
   def date_key(f):
       m = re.search(r'(\d{2})-(\d{2})-(\d{4})', f.name)
       return (m.group(3), m.group(1), m.group(2)) if m else ('0','0','0')
   print(max(files, key=date_key))
   "
   ```
   Use the printed path as `<zip_path>`. If no ZIP is found, ask the user for the path.

2. **Run the pipeline:**
   ```
   uv run --project /Users/rob/Documents/GitHub/Rob/linkedwith python /Users/rob/Documents/GitHub/Rob/linkedwith/linkedwith.py <zip_path>
   ```
   Replace `<zip_path>` with the path the user provided. `uv run` ensures the virtual environment with Jinja2 is active.

3. **Report results** — show the full stdout output, which includes:
   - Connection changes (added/removed/no changes)
   - Number of connections parsed
   - Store path
   - HTML output path

4. **Confirm output location** — tell the user:
   - `data/linkedwith.json` — the data store (updated with new connection data)
   - `output/LinkedWith.HTML` — the sortable contact list (open in any browser, or transfer to iPhone and open in HTML Preview app)

### Notes

- If `data/contact_info.csv` exists, it is automatically merged — no extra flag needed.
- Re-running with a newer LinkedIn export is safe: existing user data (email, phone, notes) is preserved.
- `output/LinkedWith.HTML` is fully self-contained — no internet connection required for viewing.
