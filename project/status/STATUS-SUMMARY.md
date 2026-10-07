---
name: LinkedWith
tagline: "A personal Python utility that parses a LinkedIn data export ZIP into an enriched, searchable, offline-ready HTML contact list combining connections, message history, and user-added contact info."
group: Utilities
profile: Utility
priority: 17
status: "Stable, run-when-needed — 96/96 tests passing (2026-10-06); last refresh 2026-09-20 from the 2026-09-19 export (781 connections, 180 messaged). Open: noisy no-URL warnings, 23 dropped-out connections and one duplicate key sit silently in the store."
generated: 2026-10-06
questions_for_rob:
  - question: "A committed diary entry names one contact in this public repo. Scrub the line only, or also rewrite git history?"
    blocks: "PII stays visible on GitHub until scrubbed; history rewrite needs a force-push."
    asked: 2026-10-06
  - question: "OK to delete the three older export zips in data/ (newest one kept)?"
    blocks: "Nothing blocked; local PII copies just accumulate."
    asked: 2026-10-06
---
