# LinkedIn Simple Report

A simple tool to let me get more out of LinkedIn data.  At some point it might incldue a full database and an app - but for now, want something simple

### Data
Before any of this works, you need your data. LinkedIn buries the export option, so here's the path: Settings & Privacy → Data Privacy → Get a copy of your data → select “Download larger data archive” → request the archive. LinkedIn says it takes 24 hours; in my experience it's closer to 15 minutes for the initial files, though the full message history can take longer. You'll get a zip file with CSVs covering connections, messages, endorsements, recommendations, positions, skills, and profile data. That's your raw material.

### Contact Info
  URL, First Name, Last Name, Email, Phone, Notes

  All columns are optional per-row. Matching works in priority order:

  1. URL (preferred) — normalized LinkedIn profile URL, e.g. https://www.linkedin.com/in/johndoe/
  2. Name fallback — case-insensitive First Name + Last Name match (skipped with a warning if 0 or 2+ matches found)

  The merged fields land in the store as user_email, user_phone, and user_notes — these survive re-imports even when contact_info.csv is absent.


  ### Running Direct

 ```
 python linkedwith.py data/LinkedIn/Complete_LinkedInDataExport_05-24-2026.zip.zip
 ```
