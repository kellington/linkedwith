# LinkedIn Analysis

A simple tool to let me get more out of LinkedIn data.  At some point it might incldue a full database and an app - but for now, want something simple

Using GSD framework with Claude Code - to create a simple skill


## Initial IDEA:

Why Every Cold Application You Send Is a Waste of Time (And What Actually Works)
https://youtu.be/AoA9h3TjxE0?si=GqgZHg_aHt-_J4cd

https://natesnewsletter.substack.com/p/cold-applications-have-a-2-response?r=1z4sm5&utm_campaign=post&utm_medium=web

### Nate's Plan
see:
- project/ideas for prompts
- https://network-intelligence.lovable.app for interactive app


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
 python linkedwith.py data/Complete_LinkedInDataExport_02-21-2026.zip.zip
 ```
 
