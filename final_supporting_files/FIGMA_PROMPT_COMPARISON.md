# Figma Prompt Comparison & Recommendation

## Overview
You have 3 different Figma prompt files. Here's a detailed comparison to help you choose the best one.

---

## File Comparison

### 1. `figma_prompts_2.md` (Project Files)
**Location:** `project_files/figma_prompts_2.md`

**Pros:**
- ✅ **Most recent and aligned with current codebase**
- ✅ Uses correct project name: "AuditWatch" (matches README.md)
- ✅ **7 complete screens** with detailed layouts
- ✅ Includes exact color codes from the actual app.py CSS
- ✅ Matches the actual UI implementation (6 pages + login)
- ✅ Clean, structured format with code blocks
- ✅ Includes design system notes at the end
- ✅ No emojis in the prompts (professional)
- ✅ Specific font recommendations (Inter, JetBrains Mono)
- ✅ Dark theme matching the actual app (#0a0a1a background)

**Cons:**
- ⚠️ Less detailed on component specifications
- ⚠️ Shorter descriptions per screen

**Best For:**
- Quick wireframe generation
- Matching the actual implemented UI
- Modern AI wireframe tools (Figma AI, Uizard, v0.dev)

---

### 2. `figma-prompt.txt` (Supporting Files)
**Location:** `supporting_files/figma-prompt.txt`

**Pros:**
- ✅ **Most comprehensive and detailed**
- ✅ Includes ASCII art layout diagrams
- ✅ Detailed component specifications (spacing, typography, buttons)
- ✅ Includes loading states, toasts, error alerts
- ✅ Responsive design considerations (desktop/tablet/mobile)
- ✅ Accessibility guidelines (WCAG AA)
- ✅ Export instructions included
- ✅ Professional banking-grade aesthetic focus

**Cons:**
- ⚠️ Uses older project name: "SAR Narrative Generator" (generic)
- ⚠️ Only 4 main screens (missing some pages)
- ⚠️ Color scheme different from actual implementation
- ⚠️ Lighter theme (#F9FAFB background) vs actual dark theme

**Best For:**
- Working with human designers
- Comprehensive design system creation
- Traditional Figma design workflow
- Detailed component library creation

---

### 3. `figma_prompts_1.txt` (Supporting Files)
**Location:** `supporting_files/figma_prompts_1.txt`

**Pros:**
- ✅ **Most creative and feature-rich**
- ✅ Includes dashboard with charts and visualizations
- ✅ Advanced features: chat interface, tracked changes, calendar view
- ✅ Detailed audit trail visualization
- ✅ Alert management screen
- ✅ Dark theme with specific color codes
- ✅ Includes wireframe vs prototype notes

**Cons:**
- ⚠️ Uses wrong project name: "ScribeAI" (outdated)
- ⚠️ Includes features NOT in current implementation (dashboard, chat, calendar)
- ⚠️ More complex than actual MVP
- ⚠️ May confuse designers with extra features

**Best For:**
- Future feature planning
- Pitch deck / presentation mockups
- Showing potential enhancements
- Hackathon demo with "wow factor"

---

## Detailed Comparison Table

| Feature | figma_prompts_2.md | figma-prompt.txt | figma_prompts_1.txt |
|---------|-------------------|------------------|---------------------|
| **Project Name** | ✅ AuditWatch | ⚠️ Generic | ❌ ScribeAI |
| **Screens** | 7 screens | 4 screens | 6 screens |
| **Theme** | ✅ Dark (#0a0a1a) | ⚠️ Light (#F9FAFB) | ✅ Dark (#0D1117) |
| **Matches Code** | ✅ Yes | ⚠️ Partial | ❌ No |
| **Detail Level** | Medium | High | High |
| **ASCII Diagrams** | ❌ No | ✅ Yes | ❌ No |
| **Component Specs** | Basic | ✅ Detailed | Medium |
| **Accessibility** | Basic | ✅ WCAG AA | Basic |
| **Responsive** | Basic | ✅ Detailed | Basic |
| **Extra Features** | ❌ No | ❌ No | ⚠️ Yes (not in MVP) |
| **AI Tool Ready** | ✅ Yes | ⚠️ Partial | ✅ Yes |
| **Format** | Markdown | Plain text | Plain text |

---

## Recommendation

### 🏆 **WINNER: `figma_prompts_2.md`**

**Why?**
1. **Matches your actual codebase** - Uses "AuditWatch" name
2. **Covers all 7 screens** - Login + 6 main pages
3. **Correct color scheme** - Dark theme matching app.py CSS
4. **AI-tool optimized** - Clean format for Figma AI, Uizard, v0.dev
5. **Most recent** - Located in project_files (not supporting_files)

### When to Use Each File:

#### Use `figma_prompts_2.md` when:
- ✅ Creating wireframes for the current MVP
- ✅ Using AI wireframe tools (Figma AI, Uizard, v0.dev)
- ✅ Need quick mockups for hackathon demo
- ✅ Want to match the actual implemented UI

#### Use `figma-prompt.txt` when:
- ✅ Working with professional designers
- ✅ Need detailed component specifications
- ✅ Creating a comprehensive design system
- ✅ Need accessibility and responsive guidelines
- ✅ Building a component library

#### Use `figma_prompts_1.txt` when:
- ✅ Planning future features (dashboard, chat, calendar)
- ✅ Creating pitch deck mockups
- ✅ Showing potential enhancements to stakeholders
- ✅ Need "wow factor" for presentations
- ⚠️ BUT: Update "ScribeAI" to "AuditWatch" first!

---

## How to Use the Recommended File

### Option 1: Figma AI (Built-in)
1. Open Figma
2. Create new file
3. Select a frame (Desktop 1440x900)
4. Click "Generate with AI" or use Figma AI plugin
5. Copy-paste ONE screen prompt at a time from `figma_prompts_2.md`
6. Iterate and refine

### Option 2: Uizard (AI Wireframe Tool)
1. Go to uizard.io
2. Create new project
3. Choose "Generate from text"
4. Paste the full prompt for one screen
5. Generate and customize
6. Export to Figma

### Option 3: v0.dev (Vercel AI)
1. Go to v0.dev
2. Paste screen prompt
3. Generate React component
4. Copy design to Figma manually
5. Useful for getting exact spacing/layout

### Option 4: Traditional Figma Design
1. Use `figma-prompt.txt` as a design brief
2. Share with designer
3. Designer creates from specifications
4. More time but higher quality

---

## Quick Start: Best Prompt for Each Screen

### Screen 1: Login Page
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

### Screen 2: Input Case Page
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

*(Continue with remaining screens from figma_prompts_2.md)*

---

## Pro Tips

### For AI Tools:
1. **One screen at a time** - Don't paste all 7 screens at once
2. **Iterate** - Generate, review, refine prompt, regenerate
3. **Be specific** - Add more details if AI misses something
4. **Use examples** - Reference similar apps (Stripe Dashboard, Linear, etc.)

### For Human Designers:
1. **Share the full file** - Give them `figma-prompt.txt` for complete specs
2. **Provide screenshots** - Run the actual app and screenshot each page
3. **Share color codes** - Extract from app.py CSS (already in prompts)
4. **Iterate together** - Review drafts and refine

### For Hackathon Demo:
1. **Use `figma_prompts_2.md`** - Matches your actual app
2. **Generate quickly** - Use Uizard or Figma AI for speed
3. **Focus on 3-4 key screens** - Login, Input, Review, Audit Trail
4. **Add screenshots** - Mix wireframes with actual app screenshots

---

## Color Palette Reference (from actual app.py)

```css
--primary: #1a237e;
--primary-light: #3949ab;
--accent: #0288d1;
--success: #2e7d32;
--warning: #ef6c00;
--danger: #c62828;
--bg-dark: #0a0a1a;
--bg-card: #131328;
--text-primary: #e0e0e0;
--text-secondary: #9e9e9e;
--border: #2a2a4a;
```

---

## Final Recommendation

**For your hackathon:**

1. **Use `figma_prompts_2.md`** as your primary source
2. **Generate 4 key screens:**
   - Login (Screen 1)
   - Input Case (Screen 2)
   - Review Narrative (Screen 3)
   - Audit Trail (Screen 4)
3. **Tool:** Use Uizard or Figma AI for speed
4. **Time:** 30-60 minutes total
5. **Export:** PNG images at 2x resolution for presentation

**Result:** Professional wireframes that match your actual implementation, perfect for demo and documentation.

---

## Need Help?

If you need to modify any prompts:
1. Keep the dark theme (#0a0a1a)
2. Keep "AuditWatch" as the name
3. Keep the 7-screen structure
4. Add more detail if AI tool needs it
5. Reference the actual app.py CSS for exact colors

Good luck with your Figma designs! 🎨
