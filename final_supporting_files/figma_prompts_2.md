# Figma Wireframe Prompts -- AuditWatch SAR Generator

Paste these prompts into Figma AI, Uizard, or any AI wireframe tool to generate screens for each page of the application.

---

## Screen 1: Login Page

```
Design a login page for a financial compliance application called "AuditWatch".

Layout:
- Centered card on a dark navy background (#0a0a1a)
- Card has slight glassmorphism effect with rounded corners
- App title "AuditWatch" at top in white, subtitle "SAR Narrative Generator" in muted gray
- Two input fields: Username (text) and Password (password), with subtle borders
- A "Sign In" button, full-width, solid blue (#3b82f6)
- Below the button: small text "Role-based access: Analyst | Reviewer | Admin"
- No images, no logos, no emojis
- Clean, corporate, banking-grade aesthetic

Colors: Dark navy background, white text, blue accent, gray borders
Font: Inter or similar sans-serif
```

---

## Screen 2: Input Case Page

```
Design a case input page for a SAR narrative generator.

Layout:
- Left sidebar (220px) with navigation items: Input Case, Review Narrative, Audit Trail, Export, Architecture. Active item highlighted with blue accent bar.
- Sidebar also shows: logged-in user info, role badge, pipeline mode toggle (Direct/Multi-Agent)

Main content area:
- Header: "Input Case" in bold
- Dropdown: "Select Sample Case" with 3 options (case_001_structuring, case_002_layering, case_003_50lakhs)
- Large JSON text area (monospace font, 20+ rows, dark background with syntax-highlighted text)
- Row of action buttons below the textarea:
  - "Validate JSON" (outlined, gray)
  - "Generate SAR Narrative" (filled, blue, larger)
- Status area below buttons showing validation result (green success or red error text)

Colors: Dark theme, navy sidebar, dark gray main area, blue buttons
Font: Inter for UI, JetBrains Mono for code/JSON
```

---

## Screen 3: Review Narrative Page

```
Design a narrative review page for a compliance SAR report.

Layout:
- Same sidebar as Screen 2
- Main content split into two columns (70/30):

Left column (70%):
- Section header: "Generated SAR Narrative"
- Case ID badge and typology badge at top
- Five expandable sections with Roman numerals:
  I. Summary of Suspicious Activity
  II. Account and Customer Information
  III. Description of Suspicious Activity
  IV. Explanation of Suspicion
  V. Conclusion and Recommendation
- Each section shows formatted paragraph text
- "Approve Narrative" button at bottom (green)

Right column (30%):
- "Analysis Summary" card:
  - Risk Score: circular gauge showing 78/100
  - Confidence breakdown: 3 horizontal progress bars (Pattern: 85%, Template: 72%, Regulatory: 90%)
  - Transaction stats: total volume, count, date range
- "Detected Patterns" card:
  - Bulleted list of red flags (e.g., "Structuring: 15 transactions below INR 1,00,000")
  - Each with a severity indicator dot (red/orange/yellow)
- "Compliance Check" card:
  - Checklist items with check/x icons:
    [check] Customer identified
    [check] Transaction period specified
    [check] Suspicious patterns documented
    [check] Regulatory references included
    [check] Recommendation provided

Colors: Dark theme, green for approved items, red for flags, blue accent
```

---

## Screen 4: Audit Trail Page

```
Design an audit trail page showing pipeline execution steps.

Layout:
- Same sidebar
- Main area:
  - Header: "Audit Trail" with case ID
  - Vertical timeline visualization:
    - Each step is a card connected by a vertical line
    - Steps: Input Parsing > Pattern Detection > RAG Retrieval > Typology Classification > Narrative Generation > Audit Logging
    - Each card shows: step name, timestamp, duration (e.g., "0.23s"), status badge (completed/in-progress/failed)
    - Expandable details per step showing data accessed and reasoning
  - Export buttons at bottom: "Export JSON", "Export CSV"

Colors: Dark theme, blue timeline line, green status badges, white cards with dark borders
```

---

## Screen 5: Export Page

```
Design an export page for downloading SAR reports in multiple formats.

Layout:
- Same sidebar
- Main area:
  - Header: "Export Report"
  - Four export cards in a 2x2 grid:
    1. PDF card: icon of document, "Download PDF", description "Formatted SAR report with sections and metadata"
    2. JSON card: icon of code brackets, "Download JSON", description "Structured data for system integration"
    3. CSV card: icon of spreadsheet, "Download CSV", description "Transaction summary for analysis"
    4. TXT card: icon of text file, "Download TXT", description "Plain text narrative for email/filing"
  - Each card has a download button
  - Preview section below showing first 500 chars of narrative

Colors: Dark theme, each card has subtle icon tint (blue/green/orange/gray)
```

---

## Screen 6: Architecture Page

```
Design a system architecture viewer page.

Layout:
- Same sidebar
- Main area with two tabs: "MCP Tool Servers" and "A2A Agents"

MCP tab:
- Three server cards in a row:
  1. Transaction Analyzer (3 tools listed)
  2. SAR Template Engine (3 tools listed)
  3. Audit Trail Manager (3 tools listed)
- Each card shows: server name, version, tool list with descriptions

A2A tab:
- Pipeline flow diagram showing:
  Coordinator Agent -> Data Enrichment Agent -> Typology Agent -> Narrative Agent -> Audit Agent
- Agent cards below with skills list
- Message trace log showing JSON-RPC messages between agents

Colors: Dark theme, cards with subtle borders, blue accent for active elements
```

---

## Screen 7: Settings Page (Admin Only)

```
Design a settings/configuration page for admin users.

Layout:
- Same sidebar
- Main area:
  - Header: "Settings" with admin badge
  - Two-column layout:
    - LLM Settings: model name, temperature slider, max tokens, base URL
    - Database Settings: type (SQLite), path
  - Security Settings section:
    - PII Anonymization toggle (on/off)
    - Max Input Length display
  - All fields are read-only display (not editable in UI, changed via config)

Colors: Dark theme, muted text, organized table layout
```

---

## Design System Notes

For all screens:

- Background: #0a0a1a (near-black navy)
- Card background: #1a1a2e with 1px border #2a2a3e
- Primary text: #ffffff
- Secondary text: #a0a0b0
- Accent blue: #3b82f6
- Success green: #22c55e
- Danger red: #ef4444
- Warning amber: #f59e0b
- Font: Inter (UI), JetBrains Mono (code)
- Border radius: 8px for cards, 6px for buttons
- No emojis anywhere -- use minimal geometric icons only
