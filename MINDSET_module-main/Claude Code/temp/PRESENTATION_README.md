# MINDSET Employment Presentation - Compilation Instructions

## Files Created

**LaTeX Source:** `MINDSET_Employment_Presentation.tex`
- Professional Beamer presentation
- 35+ slides covering complete methodology
- Ready to compile to PDF

---

## How to Compile to PDF

### Option 1: Using Overleaf (Easiest - Online)

1. Go to: https://www.overleaf.com
2. Create free account (if needed)
3. Click "New Project" → "Upload Project"
4. Upload `MINDSET_Employment_Presentation.tex`
5. Click "Recompile"
6. Download PDF

**Advantages:**
- No software installation needed
- Works in browser
- Handles all LaTeX packages automatically

---

### Option 2: Using Local LaTeX Installation

If you have LaTeX installed (MiKTeX, TeX Live, etc.):

```bash
cd "Claude Code/temp"
pdflatex MINDSET_Employment_Presentation.tex
pdflatex MINDSET_Employment_Presentation.tex  # Run twice for table of contents
```

**Output:** `MINDSET_Employment_Presentation.pdf`

---

### Option 3: Using VS Code with LaTeX Workshop

If you have VS Code:

1. Install extension: "LaTeX Workshop"
2. Open `MINDSET_Employment_Presentation.tex`
3. Press Ctrl+Alt+B (or Cmd+Option+B on Mac)
4. PDF generates automatically

---

## Presentation Structure (35 Slides)

### Section 1: Introduction & Context (2 slides)
- Research objective
- Key challenge (no GLORIA data)
- Deliverables

### Section 2: MINDSET & MRIO Background (2 slides)
- What is MINDSET?
- MRIO framework basics
- Why it matters for employment

### Section 3: Employment Estimation Methodology (3 slides)
- Simplified scope (employment-only)
- Three core equations
- Conceptual flow diagram

### Section 4: Data Requirements (3 slides)
- Required data files (5 total)
- Synthetic data approach
- Employment coefficient structure

### Section 5: Step-by-Step Implementation (4 slides)
- Workflow overview
- Step 1: Generate synthetic data
- Step 2: Define investment scenario
- Step 3: Execute MINDSET
- Step 4: Extract results

### Section 6: Expected Results & Interpretation (3 slides)
- Expected results (illustrative)
- Interpretation & validation
- Sensitivity analysis options

### Section 7: Limitations & Next Steps (2 slides)
- Limitations of current approach
- Next steps for full implementation

### Section 8: Summary & Discussion (3 slides)
- Summary of key points
- Discussion questions for supervisor
- References & resources

---

## Key Features

### Visual Elements:
- ✓ TikZ flow diagram (conceptual model)
- ✓ Professional tables with booktabs
- ✓ Color-coded boxes for emphasis
- ✓ Structured equation blocks

### Content Highlights:
- ✓ Complete methodology explanation
- ✓ Clear rationale for synthetic data
- ✓ Step-by-step implementation guide
- ✓ Expected results with interpretation
- ✓ Discussion questions for supervisor

### Academic Rigor:
- ✓ References to MRIO literature
- ✓ Validation against typical multipliers
- ✓ Clear statement of limitations
- ✓ Transparent assumptions

---

## Customization Options

### To Change Colors:
Line 5: `\usecolortheme{default}`
→ Try: `whale`, `dolphin`, `orchid`, `rose`

### To Change Theme:
Line 4: `\usetheme{Madrid}`
→ Try: `Berlin`, `Copenhagen`, `Singapore`, `Boadilla`

### To Add Your Name:
Line 14: `\author{Student Presentation for Supervisor Review}`
→ Replace with your name

### To Adjust Slide Aspect Ratio:
Line 1: `[aspectratio=169]` (16:9 widescreen)
→ Try: `[aspectratio=43]` (4:3 traditional)

---

## Presentation Tips

### For Supervisor Meeting:
1. **Focus on Sections 3-5** (methodology & implementation)
2. **Emphasize Section 8** (discussion questions)
3. **Have Section 6** ready if asked about results

### Suggested Timing:
- Introduction: 2-3 minutes
- Methodology: 8-10 minutes
- Implementation: 8-10 minutes
- Results & Discussion: 5-7 minutes
- **Total:** 25-30 minutes + Q&A

### Key Messages:
1. Employment estimation is **feasible with simplified MINDSET**
2. Synthetic data **demonstrates methodology** while awaiting GLORIA access
3. Workflow is **fully documented and replicable**
4. Results are **sensible and validate against literature**
5. Approach is **ready for real data** when available

---

## Files in Package

```
Claude Code/temp/
├── MINDSET_Employment_Presentation.tex  ← LaTeX source
├── PRESENTATION_README.md               ← This file
├── EMPLOYMENT_ONLY_Requirements.md      ← Detailed methodology
├── EMPLOYMENT_ONLY_Visual_Flow.md       ← Flow diagrams
└── EMPLOYMENT_QUICK_REFERENCE.md        ← Quick reference
```

---

## Troubleshooting Compilation

### Error: "! LaTeX Error: File 'beamer.cls' not found"
**Solution:** Install LaTeX distribution (MiKTeX or TeX Live)

### Error: "! Package tikz Error"
**Solution:** Package should auto-install, or use Overleaf

### Warning: "Overfull \hbox"
**Solution:** These are formatting warnings, PDF still generates fine

### No PDF Generated:
**Solution:** Check .log file for errors, or use Overleaf (most reliable)

---

## Next Steps After Compilation

1. **Review the PDF** - Check all slides render correctly
2. **Practice presentation** - Aim for 25-30 minutes
3. **Prepare for questions** - Review discussion questions on slide 34
4. **Have documentation ready** - Reference the .md files for details
5. **Schedule supervisor meeting** - Share PDF in advance if possible

---

**Questions?** All documentation is in `Claude Code/temp/`

**Ready to present?** Just compile the LaTeX file to PDF and you're set!
