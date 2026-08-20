# AI + Process

## Project Snapshot
*What the project is, who it is for, and what problem it addresses.*

A simple tool to let me get more out of LinkedIn data. At some point it might include a
full database and an app — but for now, I want something simple.

LinkedIn lets you export your data as a ZIP of CSVs, then abandons you there. LinkedWith
parses that export into a single self-contained HTML page: every connection, enriched with
when I last exchanged messages with them, plus my own email/phone/notes. One file, works
offline, readable on the phone.

## The AI Approach
*The practical reasons AI tools or agents were included in this project.*

This is just a Claude (Agent) skill that manages some local files. The work is small,
fiddly and infrequent — exactly the kind of thing worth automating but not worth spending
a weekend on. Running it as a skill means "refresh my contacts" is one instruction, not a
remembered sequence of commands.

## How AI Supported the Work
*Where AI helped with planning, design, coding, analysis, testing, documentation, or review.*

- Generated the parsing scripts (ZIP extraction, CSV quirks, URL normalisation)
- Merges data and creates the HTML
- Wrote the test suite — 96 tests covering parsing, merge behaviour, and rendering
- Rebuilt the HTML output (2026-08-19) after I said the first version was ugly and had no
  functionality: search, filter chips, sorting, card and table views
- Drove a real browser to check the rebuilt page actually worked, rather than trusting the
  generated source

## Where Human Judgment Mattered
*The decisions, corrections, constraints, and tradeoffs that required experience and direction.*

- Interactive — it is a tool meant to create something I can use. I am the only user, so
  "does this feel right in my hand" is the acceptance test
- Pointing at a working example rather than describing what I wanted. I had built a
  contacts page in another project and liked its search and filtering; "make it like that"
  carried more signal than any amount of specification
- Calling the first output ugly. It passed every test and did what was asked. That is
  precisely the gap a person has to close

## Key Process Decisions
*The important choices that shaped scope, architecture, data, workflow, user experience, or delivery.*

- **One self-contained HTML file.** No server, no CDN, no database. It has to open on a
  phone with no signal. This constraint decided most of the rest
- **Flat JSON store, keyed by profile URL.** LinkedIn-sourced fields get overwritten on
  re-import; my own fields (email, phone, notes) never do
- **Merge, don't replace.** A connection that drops out of a later export stays in the
  store and gets reported, rather than silently vanishing
- **Data-driven page, not generated markup.** The rows embed as a JSON array and the page
  draws itself. One filter/sort pipeline feeds both the card and table views, so a new
  facet is a few lines rather than a template rewrite
- **Stdlib over libraries.** Jinja2 is the only dependency. No pandas, no DataTables

## Quality and Confidence Checks
*How the work was reviewed, tested, validated, simplified, or improved.*

- 96 automated tests, run on every change
- Rendering tests parse the embedded JSON back out rather than asserting on markup, so
  they survive a redesign — the old tests asserted the exact table HTML and all had to be
  rewritten when the page changed
- An injection test: a connection whose notes contain `</script>` must not break the page
- The rebuilt page was loaded in a real browser and exercised — search, chips, sorting,
  both views, mobile width, dark mode — not just generated and eyeballed

## What Worked Well
*The AI-assisted patterns or workflows that produced useful results.*

- **Show, don't specify.** Handing over a working artifact I already liked and saying
  "like this, for this data" produced a better result faster than a written brief
- **Blunt feedback.** "It is ugly and has no functionality" was more useful than a
  polite list of tweaks
- **Testing in the real environment.** Three genuine bugs — a blank page, headers painting
  behind rows, a table sliding under the header — were invisible in the source and obvious
  in the browser

## What Needed Caution
*Where AI was weak, misleading, incomplete, overconfident, or required close supervision.*

- **Correct is not the same as usable.** The first version satisfied every requirement and
  every test, and was still not a thing I wanted to open
- **Generated output can look right and be broken.** The HTML was well-formed and rendered
  a blank white page — the escaping was wrong in a way no amount of reading the file would
  have revealed
- **Tests can pin down the wrong thing.** Assertions on exact markup made the test suite an
  obstacle to improving the page rather than a safety net for it
- **Watch what a test actually protects.** One rule banned every external URL in the name
  of working offline; it would also have blocked tappable profile links, which cost
  nothing offline. The rule needed narrowing to what it was really for

## Reusable Lessons
*What could be applied to other projects, teams, or client situations.*

- Point at an example you like. It is the highest-bandwidth instruction available
- Say it plainly when the output is not good enough. The correction is cheap; living with
  a mediocre tool is not
- Test the behaviour, not the markup — assert on the data and the outcome, so the surface
  can be redesigned without a test rewrite
- Make the agent use the thing it built, in the environment it will run in
- When a test blocks a good change, ask what it was protecting before deleting it

## Current Status and Next Steps
*What is complete, what remains, and where the project could go next.*

Working and in use. Latest run against the 2026-08-18 export: 761 connections, 96/96 tests
passing. The HTML has search, facet filters (messaged / has notes / has contact details),
a connection-year filter, four sort orders, and card and table views.

Next: pull LinkedWith data into the contact-merge project, so LinkedIn connections and
everything else land in one contact list instead of two.

## Bottom Line
*The short version: what this project demonstrates about using AI responsibly and practically.*

A small personal tool, built quickly, that I actually use. The interesting part is not the
parsing — it is that the first version was correct and unusable, and the fix was me saying
so and pointing at something better. AI closed the distance fast; deciding the distance
existed was the human job.

**LAST UPDATE:** 2026-08-19
