# File Usage Guide - What to Use Where

## Quick Reference

| Purpose | File to Use | Location |
|---------|-------------|----------|
| **Hackathon Presentation** | `slide_contents.md` | `project_files/` |
| **Figma Wireframes** | `figma_prompts_2.md` | `project_files/` |
| **Setup Instructions** | `SETUP.md` or `how_to_run.md` | `project_files/` |
| **Code Quality Report** | `CODE_QUALITY_AUDIT.md` | `project_files/` |
| **Hardware Requirements** | `VRAM_REQUIREMENTS.md` | `project_files/` |
| **Project Overview** | `README.md` | `project_files/` |
| **Architecture Diagrams** | `architecture_diagrams.md` | `project_files/` |

---

## For Hackathon Submission

### 1. Presentation Slides (PowerPoint/Google Slides)

**Use:** `project_files/slide_contents.md`

**What it contains:**
- Problem statement
- Solution overview
- Impact metrics (73% time reduction)
- Tech stack explanation
- Architecture (MCP + A2A)
- Demo flow
- Scalability plan

**How to use:**
1. Open your PowerPoint/Google Slides
2. Copy content from each section
3. Add visuals (diagrams, screenshots)
4. Present!

**Update needed:** Change "8GB+ VRAM" to "6GB+ VRAM" in the scalability section

---

### 2. Methodology Slide (Architecture Diagrams)

**Use:** `project_files/architecture_diagrams.md`

**What it contains:**
- System architecture diagram (Mermaid format)
- Data flow diagram
- Component interaction diagram
- MCP server architecture
- A2A agent architecture

**How to use:**
1. Copy Mermaid code
2. Paste into [mermaid.live](https://mermaid.live) or [eraser.io](https://eraser.io)
3. Export as PNG/SVG
4. Add to presentation

**For your methodology slide, include:**
- Architecture Diagram ✅ (from this file)
- Flow Chart ✅ (from this file)
- Wireframes ✅ (generate from `figma_prompts_2.md`)

---

### 3. Wireframes/UI Mockups

**Use:** `project_files/figma_prompts_2.md`

**What it contains:**
- 7 screen prompts (Login, Input, Review, Audit, Export, Architecture, Settings)
- Exact color codes matching your app
- Layout descriptions

**How to use:**
1. Go to [uizard.io](https://uizard.io) or use Figma AI
2. Copy ONE screen prompt at a time
3. Generate wireframe
4. Export as PNG
5. Add to presentation

**Recommended screens for presentation:**
- Screen 1: Login (shows security)
- Screen 2: Input Case (shows ease of use)
- Screen 3: Review Narrative (shows output quality)
- Screen 4: Audit Trail (shows compliance)

---

## For Documentation

### 1. Project README (GitHub/Submission Portal)

**Use:** `project_files/README.md`

**What it contains:**
- Project overview
- Quick start guide
- Architecture summary
- Tech stack
- Demo flow
- Testing instructions

**Update needed:** Change "8GB+ VRAM" to "6GB+ VRAM" in Prerequisites section

---

### 2. Setup Instructions (For Judges/Reviewers)

**Use:** `project_files/SETUP.md` OR `project_files/how_to_run.md`

**Difference:**
- `SETUP.md` - Comprehensive (system requirements, troubleshooting, deployment)
- `how_to_run.md` - Quick start (5-minute setup)

**Recommendation:** Use `how_to_run.md` for hackathon (simpler)

---

### 3. Hardware Requirements (Technical Details)

**Use:** `project_files/VRAM_REQUIREMENTS.md` (NEW - just created)

**What it contains:**
- VRAM requirements by model
- Hardware recommendations
- How to switch models for 4GB VRAM
- Performance comparison
- Troubleshooting

**When to use:**
- Judges ask about hardware requirements
- Technical Q&A session
- Deployment planning discussions

---

## For Code Review/Quality Assessment

### 1. Code Quality Report

**Use:** `project_files/CODE_QUALITY_AUDIT.md`

**What it contains:**
- Line-by-line code audit
- Zero AI slop detected
- Security assessment
- Test coverage (43 tests, 100% pass)
- Production readiness: 95%

**When to use:**
- Judges ask about code quality
- Technical review session
- "Is this production-ready?" questions

---

### 2. Figma vs App Comparison

**Use:** `project_files/APP_VS_FIGMA_COMPARISON.md`

**What it contains:**
- Proof that Figma prompts match actual app
- Feature-by-feature comparison
- Color scheme verification

**When to use:**
- Judges ask "Did you actually build this?"
- Proving design-to-implementation accuracy
- Internal reference only (don't present this)

---

## For Specific Questions

### "How does it work?" (Architecture)

**Use:**
1. `project_files/architecture_diagrams.md` - Visual diagrams
2. `project_files/README.md` - Architecture section
3. `project_files/slide_contents.md` - Slide 5 (Architecture)

---

### "What's the tech stack?" (Technology)

**Use:**
1. `project_files/slide_contents.md` - Slide 3 (Tech Stack)
2. `project_files/README.md` - Tech Stack section

**Key points:**
- Python + Streamlit (UI)
- Ollama + Llama 3.1 8B (local LLM)
- ChromaDB (vector DB)
- SQLite (audit storage)
- All open-source, zero licensing cost

---

### "What are the hardware requirements?" (Deployment)

**Use:**
1. `project_files/VRAM_REQUIREMENTS.md` - Detailed guide
2. `project_files/slide_contents.md` - Slide 7 (Scalability)

**Key points:**
- Minimum: 6GB VRAM (RTX 3060)
- Alternative: 4GB VRAM with smaller models
- Optimal: 8GB+ VRAM (RTX 3070)

---

### "How do I run it?" (Demo)

**Use:**
1. `project_files/how_to_run.md` - Quick start (5 minutes)
2. `project_files/SETUP.md` - Comprehensive setup

**Quick demo steps:**
1. `pip install -r requirements.txt`
2. `ollama pull llama3.1:8b`
3. `streamlit run src/ui/app.py`
4. Login as `admin` / `auditwatch2026`
5. Select sample case → Generate

---

### "Is the code production-ready?" (Quality)

**Use:**
1. `project_files/CODE_QUALITY_AUDIT.md` - Full audit report
2. `project_files/README.md` - Testing section

**Key points:**
- Zero AI slop detected
- 43 tests, 100% pass rate
- Zero syntax errors
- Production readiness: 95%
- Only issue: Naming inconsistency (AuditWatch vs ScribeAI)

---

### "What's the impact?" (Business Value)

**Use:**
1. `project_files/slide_contents.md` - Slide 2 (Impact Metrics)

**Key metrics:**
- 73% reduction in analyst time (5.5 hours → 90 minutes)
- 100% audit coverage
- Zero data leakage (fully offline)
- Consistent narrative quality

---

## Files to IGNORE (Internal Use Only)

❌ **Don't use these for presentation:**

1. `supporting_files/figma-prompt.txt` - Wrong design (light theme)
2. `supporting_files/figma_prompts_1.txt` - Wrong name (ScribeAI)
3. `project_files/FIGMA_PROMPT_COMPARISON.md` - Internal comparison
4. `project_files/APP_VS_FIGMA_COMPARISON.md` - Internal verification
5. `.kiro/specs/` - Development specs only

---

## Presentation Checklist

### Slides (PowerPoint/Google Slides)
- [ ] Copy content from `slide_contents.md`
- [ ] Add architecture diagram from `architecture_diagrams.md`
- [ ] Generate 4 wireframes from `figma_prompts_2.md`
- [ ] Update "8GB+ VRAM" to "6GB+ VRAM"
- [ ] Add screenshots of actual app

### Demo Preparation
- [ ] Follow `how_to_run.md` to set up
- [ ] Test with sample case (case_003_50lakhs)
- [ ] Prepare backup: screenshots if live demo fails

### Documentation
- [ ] Update `README.md` with correct VRAM requirement
- [ ] Ensure `SETUP.md` is accurate
- [ ] Have `CODE_QUALITY_AUDIT.md` ready for technical questions

### Q&A Preparation
- [ ] Read `VRAM_REQUIREMENTS.md` for hardware questions
- [ ] Review `CODE_QUALITY_AUDIT.md` for code quality questions
- [ ] Know the impact metrics from `slide_contents.md`

---

## Quick File Locations

```
project_files/
├── slide_contents.md              ← Presentation content
├── figma_prompts_2.md             ← Wireframe generation
├── architecture_diagrams.md       ← System diagrams
├── README.md                      ← Project overview
├── SETUP.md                       ← Comprehensive setup
├── how_to_run.md                  ← Quick start guide
├── CODE_QUALITY_AUDIT.md          ← Code quality report
├── VRAM_REQUIREMENTS.md           ← Hardware guide (NEW)
├── FIGMA_PROMPT_COMPARISON.md     ← Internal: Which Figma file to use
├── APP_VS_FIGMA_COMPARISON.md     ← Internal: App vs Figma verification
└── FILE_USAGE_GUIDE.md            ← This file

supporting_files/
├── figma-prompt.txt               ❌ Don't use (wrong design)
├── figma_prompts_1.txt            ❌ Don't use (wrong name)
└── [other files]                  ← Reference only
```

---

## Summary: What to Use When

### For Hackathon Presentation:
1. **Slides:** `slide_contents.md`
2. **Diagrams:** `architecture_diagrams.md`
3. **Wireframes:** `figma_prompts_2.md`

### For Demo:
1. **Setup:** `how_to_run.md`
2. **Troubleshooting:** `SETUP.md`

### For Q&A:
1. **Hardware:** `VRAM_REQUIREMENTS.md`
2. **Code Quality:** `CODE_QUALITY_AUDIT.md`
3. **Architecture:** `README.md` + `architecture_diagrams.md`

### For Submission:
1. **Main README:** `README.md`
2. **Setup Guide:** `SETUP.md` or `how_to_run.md`

---

## Need Help?

**Question:** "Which file should I use for [X]?"

**Answer:** Check the Quick Reference table at the top of this document!

Good luck with your hackathon! 🚀
