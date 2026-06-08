# LinkedIn Network Analysis — Quick Start Guide

## How This System Works

This isn't just a one-time analysis. It's a workflow:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FIRST RUN                                   │
│                                                                     │
│   LinkedIn Export → Analysis Prompt → Dashboard (insight)           │
│                                      → CSV (action table)           │
│                                      → Script (reproducibility)     │
│                                                                     │
│   You see your network clearly. You import CSV to Notion/Sheets.   │
│   You have a place to track who you've reached out to.             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       RECURRING RUNS                                │
│                                                                     │
│   Fresh Export → Re-run Script → New CSV                           │
│                                                                     │
│   Diff new CSV against your existing table:                        │
│   - Who's newly critical? (relationship decayed)                   │
│   - Who's newly warm? (recent conversation)                        │
│   - New resurrection opportunities?                                │
│                                                                     │
│   Update your table. Repeat quarterly.                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       ON-DEMAND: WARM PATH                          │
│                                                                     │
│   "I want to reach [Company]"                                       │
│                                                                     │
│   Warm Path Prompt → Ranked paths with reasoning                   │
│                    → Add results to your action table              │
│                                                                     │
│   Use whenever you have a specific target.                         │
└─────────────────────────────────────────────────────────────────────┘

```

---

## Step 1: Get Your LinkedIn Data

LinkedIn buries the export option. Here's the path:

**Settings & Privacy → Data Privacy → Get a copy of your data → Select "Download larger data archive" → Request archive**

LinkedIn says 24 hours; usually it's 15 minutes for the initial files. Full message history can take longer.

You'll get a zip with CSVs covering connections, messages, endorsements, recommendations, positions, and more. That's your raw material.

---

## Step 2: Choose Your Path

### Option A: Cowork (Recommended)

**Best for:** Full analysis in one session, no timeout risk, context persists for follow-up queries.

1. Open Claude Cowork
2. Select your unzipped LinkedIn export folder
3. Paste the **Full Analysis Prompt** (`Network Intelligence Analysis.md`)
4. Wait 3-5 minutes for all 6 analyses to complete
5. Get: HTML dashboard + CSV action table + Python script + JSON summary
6. To query a specific company later, just ask in the same conversation—context carries forward

### Option B: ChatGPT (Two-Part)

**Best for:** If you don't have Cowork access. Requires two separate chats.

**Part 1:**

1. Upload 4 files: `Connections.csv`, `Endorsement_Received_Info.csv`, `Endorsement_Given_Info.csv`, `Positions.csv`
2. Paste the **Part 1 Prompt**
3. Get: Reciprocity ledger, network archetype, company concentration, senior contacts
4. Download the CSV

**Part 2 (new chat):**

1. Upload 2 files: `messages.csv`, `Connections.csv`
2. Paste the **Part 2 Prompt**
3. Get: Relationship depth, resurrection opportunities, vouch scores
4. Download the CSV

**After both parts:**

- Merge the two CSVs on the Name column
- Import to Notion/Sheets

**Note on timeouts:** If you have years of message history, Part 2 may timeout. Ask ChatGPT to "process in batches of 1000 conversations and aggregate."

---

## Step 3: Set Up Your Action Table

Import your CSV to wherever you track work: Notion, Google Sheets, Airtable, your CRM.

**Key columns for tracking:**

| Column | Source | Purpose |
| --- | --- | --- |
| Name | Analysis | Who |
| Company | Analysis | Where |
| Vouch Score | Analysis | How strong the relationship is |
| Decay Status | Analysis | Urgency flag |
| Days Until Critical | Analysis | When to act |
| Category | Analysis | Resurrection type / archetype match |
| Hook | Analysis | What to say |
| Last Contact | Analysis | When you last talked |
| **Status** | You | Not started / Reached out / Responded / Meeting scheduled |
| **Notes** | You | Your tracking notes |

The last two columns are blank in the export—they're for you.

---

## Step 4: Use the Warm Path Prompt

When you have a specific target company:

1. Paste the **Warm Path Prompt** with your target company and domain keywords
2. Get ranked paths with reasoning (not just names—*why* each person is relevant)
3. Add the results to your action table, tagged with the target company
4. Track your outreach in the Status column

---

## What Each Prompt Does

| Prompt | Environment | Analyses | Output |
| --- | --- | --- | --- |
| **Full Analysis** | Cowork | All 6 + warm path demo | Dashboard, CSV, Script, JSON |
| **Part 1** | ChatGPT | Reciprocity, Archetype, Concentration, Seniors | Dashboard, CSV |
| **Part 2** | ChatGPT | Depth, Resurrection, Vouch | Dashboard, CSV |
| **Warm Path** | Both | Relevance + warmth scoring for specific target | Ranked paths, CSV |

---

## Expected Files in LinkedIn Export

```
/LinkedIn_Export/
├── Connections.csv          ← Required (has 3 junk header rows)
├── messages.csv             ← Required for depth analysis
├── Endorsement_Received_Info.csv
├── Endorsement_Given_Info.csv
├── Recommendations_Received.csv
├── Recommendations_Given.csv
├── Positions.csv            ← For shared company detection
├── Profile.csv
├── Skills.csv
├── Invitations.csv
└── Company Follows.csv

```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
| --- | --- | --- |
| "No connections found" | Header rows not detected | Tell Claude/ChatGPT to "scan for the row containing 'First Name' and use that as header" |
| Timezone errors | Comparing tz-naive and tz-aware datetimes | Use `pd.Timestamp.now(tz='UTC')` |
| Missing recommendations | User has none | Analysis shows empty sections—that's fine |
| Company column empty | LinkedIn export quirk | Shared company detection will be limited |
| ChatGPT timeout | Large messages.csv | Process in batches: "Analyze first 1000 conversations, then next 1000" |

---

## Extending This Work

### Re-running Quarterly

1. Export fresh LinkedIn data
2. In Cowork: Re-run `network_analysis.py` with new export folder
3. In ChatGPT: Re-upload and re-run both prompts
4. Diff new CSV against your existing action table
5. Update decay statuses, add new resurrection opportunities

### Future Prompt Ideas

- **Introduction Request Generator** — Given a target person, draft the optimal ask to your best bridge
- **Conference Optimizer** — Given an attendee list, rank who to prioritize meeting
- **Content Strategy from Network** — What topics does your network engage with? (requires post data, not in standard export)
- **Competitive Intelligence** — Who in your network connects to competitors?

### Data Enrichments

The analysis could be richer with:

- LinkedIn post engagement data (not in standard export)
- Calendar data (meeting history)
- Email data (deeper conversation signals)
- Company data APIs (funding stage, headcount, industry)

---

## The Prompts

- `Network Intelligence Analysis.md` — Full Cowork prompt
- `ChatGPT Part 1.md` — Core metrics (no messages)
- `ChatGPT Part 2.md` — Message analysis
- `Warm Path Discovery.md` — Target company query

Export your data tonight, run the analysis tomorrow, and by end of week you'll see your network the way LinkedIn never wanted you to.