Copy and paste this prompt into Claude Cowork after selecting your LinkedIn data export folder. Also works in Claude Code.

---

## The Prompt

```
Analyze my LinkedIn data export and create a "Network Intelligence Dashboard" that surfaces insights LinkedIn's UI will never show me.

Before writing any code, read the files in my export folder and confirm:
- Connections.csv exists (note: has 3 junk header rows before actual headers)
- messages.csv exists
- Endorsement files exist (Received and Given)
- Recommendations files exist (Received and Given)
- Positions.csv exists

Print the file list and row counts, then proceed.

---

Implement these 6 analyses:

1. **Relationship Half-Life Analysis**
   - Model relationship decay: strength(t) = initial × 0.5^(t/half_life)
   - Base half-life: 180 days
   - Modifiers: +90 days if shared company history, +60 days if deep conversation (20+ messages), +30 days if mutual endorsements, -60 days if shallow contact (1-2 messages only)
   - Calculate current strength and days until "critical" (below 25% strength)
   - Flag relationships decaying fastest that are still worth saving (strength > 25%)

2. **Reciprocity Debt Ledger**
   - Score: Recommendations = 5 points, Endorsements = 1 point
   - Calculate net balance per person: (points received from them) - (points given to them)
   - Identify who owes me (I gave more, positive balance) vs who I owe (they gave more, negative balance)
   - Top 10 each direction

3. **"Who Would Vouch" Score**
   - Score = message_depth (count × 2, max 40) + recency_bonus (20 if <30 days, 10 if <90 days, 0 otherwise) + recommendation_bonus (20 per direction) + endorsement_bonus (10 per mutual) + shared_company_bonus (15 if worked together)
   - Rank all contacts by vouch score
   - These are true advocates, not just connections

4. **Conversation Resurrection Intelligence**
   - Scan message archive for dormant conversations (60-365 days since last message) containing:
     - "catch up" / "coffee" / "let's connect" → Category: "Catch-up Never Happened"
     - "could you help" / "advice" / "thoughts on" → Category: "They Asked For Help"
     - "happy to help" / "let me know if" → Category: "You Offered Help"
     - "new role" / "just started" / "excited to" → Category: "Career Transition"
   - Surface with natural re-engagement hooks based on category

5. **Network Archetype Classification**
   - Calculate scores:
     - Thought Leader: connections > 1500, average message depth < 5
     - Insider: top 3 companies represent > 40% of network
     - Connector: unique companies > 500, industries > 10
     - Climber: senior titles (VP+, Director, C-suite, Founder) > 30% of network
     - Builder: founders/entrepreneurs > 20% of network
   - Assign primary archetype based on highest score
   - Provide archetype-specific activation strategy

6. **Warm Path Analysis (Sample)**
   - Pick the company with most connections in my network
   - For that company: list direct connections, calculate their vouch scores
   - Identify potential bridges (people not at company but in same industry)
   - This demonstrates the warm path model; use the standalone Warm Path prompt for specific targets

---

**Output (5 artifacts):**

1. `Network_Intelligence_Dashboard.html`
   - Interactive HTML with dark theme (#0a0a0f background, #1a1a24 cards, #6366f1 accent)
   - Sections: Overview stats, Half-Life Status (sorted by urgency), Reciprocity Ledger, Top Vouchers, Resurrection Opportunities, Archetype Badge
   - Include actual data, not placeholders
   - Make it polished—go beyond basics with thoughtful data visualization

2. `Network_Intelligence_Framework.md`
   - Shareable document explaining the concepts and formulas
   - Useful for explaining to others what this analysis does

3. `network_analysis.py`
   - Reproducible Python script
   - Add comments explaining each section
   - User can re-run this quarterly to refresh analysis

4. `network_actions.csv`
   - Structured export for Notion/Sheets import
   - Columns: Name, Company, Title, Vouch Score, Decay Status, Days Until Critical, Category, Resurrection Hook, Last Contact, Status, Notes
   - "Status" and "Notes" columns should be empty (for user tracking)
   - Include all contacts with Vouch Score > 20 OR Decay Status = "Critical" OR has Resurrection opportunity
   - Sort by Days Until Critical (ascending), then Vouch Score (descending)

5. `network_summary.json`
   - Machine-readable summary: archetype, total connections, key stats
   - Useful for integrations or future analysis

---

**Technical notes:**
- Connections.csv has 3 header rows to skip before the actual column headers (First Name, Last Name, etc.)
- Parse dates carefully; use timezone-aware comparisons (pd.Timestamp.now(tz='UTC'))
- Current date should be used for all decay calculations
- If any file is missing, note it and continue with available data

```

---

## What You'll Get

| Artifact | Purpose | Format |
| --- | --- | --- |
| Dashboard | Visual overview, "wow moment" | HTML |
| Framework | Shareable explanation | Markdown |
| Script | Re-run capability | Python |
| Actions | Where work happens | CSV → Notion/Sheets |
| Summary | Integration/automation | JSON |

---

## Re-Run Workflow

**First run:** Analysis + dashboard (insight) + CSV (action table) + script (reproducibility)

**Future runs:**

1. Re-run `network_analysis.py` with fresh LinkedIn export
2. New CSV output diffs against your existing Notion/Sheets table
3. See what changed: new critical relationships, updated vouch scores, fresh resurrection opportunities

---

## Expected Files in LinkedIn Export

```
/LinkedIn_Export/
├── Connections.csv          ← Required
├── messages.csv             ← Required for depth analysis
├── Endorsement_Received_Info.csv
├── Endorsement_Given_Info.csv
├── Recommendations_Received.csv
├── Recommendations_Given.csv
├── Positions.csv            ← For shared company detection
└── [other files ignored]
```