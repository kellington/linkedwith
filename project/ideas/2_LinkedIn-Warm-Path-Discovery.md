# LinkedIn Warm Path Discovery

Find your best paths to a target company by weighing both **relevance** (how likely they know someone there) and **warmth** (how strong your relationship is).

Works in both Cowork and ChatGPT.

---

## Files to Upload

- `Connections.csv`
- `messages.csv`

**If you've already run the full Network Intelligence analysis:** You can skip uploading and reference the existing session context (Cowork only). Just paste the prompt with your target company.

---

## Prompt Template

Replace `[TARGET COMPANY]` and `[DOMAIN]` with your target.

```
Find my warmest AND most relevant paths to [TARGET COMPANY]. I uploaded my LinkedIn connections and messages.

[TARGET COMPANY] is in the [DOMAIN] space.

Domain keywords for matching: [LIST 5-8 KEYWORDS — e.g., "AI, machine learning, robotics, automation, computer vision" or "fintech, payments, banking, financial services, credit" or "healthcare, biotech, clinical trials, medical devices"]

---

**STEP 1 — Parse data:**

- Connections.csv: Has junk header rows. Find the row with "First Name" and use that as header.
- messages.csv: Group by CONVERSATION ID. Get message count and last message date per person.

Print:
- Total connections
- Direct connections at [TARGET COMPANY] (exact company name match)
- Connections in [DOMAIN] space (keyword match on title or company)

---

**STEP 2 — Calculate scores:**

For each connection, calculate two independent scores:

### Relevance Score (0-100): How likely do they know someone at [TARGET COMPANY]?

| Signal | Points | Rationale |
|--------|--------|-----------|
| Works at [TARGET COMPANY] | +40 | Direct connection |
| Previously worked at [TARGET COMPANY] | +30 | Alumni network |
| Title contains domain keywords | +35 | Same professional field |
| Company is in same space | +25 | Industry proximity |
| Founder/CEO/Investor title | +20 | Sees deal flow, knows other founders |
| Senior title (VP+, Director, Head of, C-suite) | +10 | Broader professional network |
| Tech role at large company | +5 | Weak signal—large companies have broad reach |

Cap at 100.

### Warmth Score (0-60): How strong is your relationship?

| Signal | Points |
|--------|--------|
| Message count × 2 | Max 40 |
| Last message < 30 days | +20 |
| Last message 30-90 days | +10 |
| Last message > 90 days | +0 |

### Combined Score

Weighting depends on company type:

**For NICHE companies** (startups, <500 employees, not household names):
- Combined = (Relevance × 0.7) + (Warmth × 0.3)
- Rationale: Fewer paths exist, so relevance matters more—you need someone who actually knows someone there.

**For LARGE companies** (Google, Amazon, Meta, Microsoft, big banks, etc.):
- Combined = (Relevance × 0.5) + (Warmth × 0.5)
- Rationale: Many paths exist, so warmth differentiates—you need someone who will actually respond.

Default to NICHE weighting unless [TARGET COMPANY] is clearly a large, well-known company.

---

**STEP 3 — Find and rank paths:**

### Tier 1: Direct Connections (at [TARGET COMPANY])

List anyone whose Company field contains [TARGET COMPANY].

Show:
- Name, Title
- Warmth Score, Relevance Score (should be ≥40), Combined Score
- Flag if no message history: "⚠️ Cold connection—no prior messages"

### Tier 2: Domain-Relevant Bridges (best indirect paths)

People NOT at [TARGET COMPANY] but with Relevance Score ≥ 25.

Rank by Combined Score. Show top 10 with:
- Name, Title, Company
- Relevance Score, Warmth Score, Combined Score
- **WHY they're relevant** (1-2 sentences explaining the connection logic)

Good explanation examples:
- "CEO of another [DOMAIN] startup—likely shares investors or attends same conferences"
- "Former [TARGET COMPANY] engineer—has alumni network inside the company"
- "VC who invests in [DOMAIN]—may have portfolio connections to [TARGET COMPANY]"

Bad explanation examples:
- "Senior role (broad network)" ← Too generic
- "Works in tech" ← Not specific enough

### Tier 3: Warm but Uncertain

People with Warmth Score ≥ 40 but Relevance Score < 25.

Show top 5 with caveat: "Strong relationship but unclear connection to [TARGET COMPANY]. Worth asking directly if they know anyone in [DOMAIN] space."

---

**STEP 4 — Flag resurrection opportunities:**

From Tier 1 and Tier 2, identify people where:
- Last message was 60-365 days ago
- Had 5+ messages total (real relationship, not drive-by)

For each, write a specific re-engagement suggestion tied to their relevance:
- "Reconnect about [DOMAIN]—mention you're exploring opportunities in the space"
- "Follow up on your last conversation and segue to [TARGET COMPANY] interest"

---

**STEP 5 — Output:**

### Text Summary

**🎯 Paths to [TARGET COMPANY]**

**Direct Connections:** [List with warmth flags, or "None found"]

**Best Bridges (Domain-Relevant):**
For each of top 5, write: "[Name] ([Title] at [Company]) — [1-sentence connection logic]"

**Warm but Unverified:** [List with caveat]

**Resurrection Opportunities:** [List with hooks]

**Confidence Assessment:**
- HIGH: Direct connections exist with message history
- MEDIUM: Domain-relevant bridges exist
- LOW: Only warm-but-uncertain paths

**Recommended First Step:** [Specific action based on what was found]

### CSV Export (optional)

File: `warm_paths_[TARGET COMPANY].csv`

Columns:
- Name
- Company
- Title
- Tier (1/2/3)
- Relevance Score
- Warmth Score
- Combined Score
- Why Relevant
- Resurrection Hook (if applicable)
- Status (blank)
- Notes (blank)

Sort by Tier ascending, then Combined Score descending.

```

---

## Example Usage

### For a startup (Dactyl AI):

```
Find my warmest AND most relevant paths to Dactyl AI. I uploaded my LinkedIn connections and messages.

Dactyl AI is in the robotics/AI space.

Domain keywords: AI, robotics, automation, computer vision, machine learning, manipulation, hardware startups

```

### For a large company (Stripe):

```
Find my warmest AND most relevant paths to Stripe. I uploaded my LinkedIn connections and messages.

Stripe is in the fintech/payments space.

Domain keywords: fintech, payments, developer tools, financial infrastructure, banking APIs, commerce

```

---

## Using This with Prior Analysis

If you ran the full Network Intelligence analysis first:

1. Your Vouch Scores are already calculated
2. In Cowork: Reference them directly ("Use the vouch scores from earlier")
3. In ChatGPT: Re-upload files (no persistent state between chats)

The Warm Path prompt's Warmth Score is a simplified version of Vouch Score. If you have full Vouch Scores, they're more accurate.

---

## Adding Results to Your Action Table

If you're maintaining a Notion/Sheets action table from the Network Intelligence analysis:

1. Run Warm Path for your target company
2. Download the CSV
3. Add new rows for anyone not already in your table
4. Tag them with the target company for filtering
5. Use the "Why Relevant" column to remember the connection logic