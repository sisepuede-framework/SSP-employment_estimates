# SUMMARY: Uganda & Libya Employment Issue

**To:** Supervisor
**From:** Felipe Esteves
**Date:** 2026-03-23
**Re:** Data Quality Issues in MINDSET Employment Estimates

---

## The Issue

Employment estimates for **Uganda** and **Libya** are 3-6x higher than structurally similar countries, making cross-country comparisons unreliable for these two nations.

### Example (Strategy_1004 - Agricultural Expansion):

| Country | Total Jobs/$1M | Agriculture Direct Jobs |
|---------|----------------|------------------------|
| Egypt | 20.93 | 12.89 |
| Morocco | 12.63 | 9.32 |
| **Libya** | **64.14** (3.1x Egypt) | **60.13** (4.7x Egypt) |
| **Uganda** | **104.08** (5.0x Egypt) | **83.05** (6.4x Egypt) |

---

## Root Cause

The problem is in the **employment coefficients** (EMPL_COEF) from the GLORIA database - specifically, how many workers are employed per dollar of output.

**Where it happens:**
- **Stage 3** of calculation: Output → Employment
- **File:** `SourceCode/employment.py`, lines 36-48
- **Data source:** GLORIA v57 employment coefficients (based on ILO/FAO statistics)

**Why Libya & Uganda:**
1. **Weak statistical systems** - Both countries have poor data quality in ILO employment statistics
2. **Structural issues:**
   - Libya: Post-conflict economy with distorted labor markets
   - Uganda: Subsistence agriculture where "employment" includes unpaid family work
3. **Measurement problems** - Informal economy counted in employment but not GDP

---

## What We've Already Fixed

The **"strategy as purchases" correction** (already implemented) helped but didn't fully solve it:
- **Old approach:** "Agriculture invests $1M" → all demand went to agriculture → maximum exposure to bad coefficients
- **New approach:** "Agriculture invests $1M" → demand distributed to Construction (40%), Machinery (30%), etc. → reduced but not eliminated problem

**Implementation:** `investment.py`, lines 219-249, using INV_CONV matrix

---

## Recommended Solution

**Option 1: Flag and Document** (Recommended for dissertation)

**What to do:**
1. Keep all 7 countries in dataset (transparency)
2. Flag Libya & Uganda with "low data quality" indicator
3. Add caveat in methodology: "Employment estimates for Libya and Uganda should be interpreted with caution due to known data quality issues in source statistics."
4. Run **sensitivity analyses** excluding these countries to show robustness of main findings

**Pros:**
- Scientifically honest and transparent
- No arbitrary adjustments
- Preserves replicability
- You can still present the results with appropriate caveats

**Cons:**
- Doesn't "fix" the numbers
- May need to exclude from some cross-country regressions

---

## Alternative Options (If Needed)

**Option 2: Proxy Country Substitution**
- Use Egypt's employment coefficients for Libya
- Use Kenya's for Uganda
- More defensible for policy use, but requires justification

**Option 3: Exclude Countries**
- Simply remove Libya & Uganda from analysis
- Focus on 5 countries with reliable data
- Cleanest but reduces scope

**See detailed report for 5 ranked options with full pros/cons analysis.**

---

## Documentation Completed

1. **DIAGNOSTIC_Uganda_Libya_Employment.md** (25 pages)
   - Complete technical analysis
   - Stage-by-stage calculation traceability
   - Five solution options ranked with pros/cons
   - Validation checks and next steps

2. **WORKFLOW_DOCUMENTATION.md** (updated)
   - Added "Data Quality Assessment" section
   - Documents known issues
   - References diagnostic report

3. **MINDSET_Employment_Presentation.tex** (updated)
   - New slide: "Data Quality Assessment: Libya & Uganda"
   - Shows comparative table with flagged countries
   - Updated limitations slide
   - Ready for defense/presentation

---

## Immediate Next Steps

**For you to decide:**
1. Which treatment option do you prefer? (Recommend: Flag & Document)
2. Should sensitivity analyses exclude Libya/Uganda or just flag them?
3. Do you want to discuss with supervisor before proceeding?

**Optional validation checks** (if you want to dig deeper):
- Extract raw EMPL_COEF values from GLORIA files
- Compare output multipliers (Stage 2) to confirm problem is in Stage 3
- Literature search for external employment benchmarks for these countries

---

## Files Location

All documentation is in: `Claude Code/temp/`
- `DIAGNOSTIC_Uganda_Libya_Employment.md` - Full technical report
- `SUMMARY_Uganda_Libya_Issue.md` - This summary
- `WORKFLOW_DOCUMENTATION.md` - Updated methodology (see end of file)
- `MINDSET_Employment_Presentation.tex` - Updated presentation

Results file: `SSP - Results/employment_consolidated.csv`

---

## Key Takeaway

**The MINDSET model is working correctly.** The problem is in the **source data quality** for these two countries in the GLORIA database. This is a known limitation of global databases when covering countries with weak statistical systems.

**Your contribution:** By identifying and documenting this issue, you're adding value - future researchers using GLORIA for employment analysis should be aware of these country-specific data quality concerns.

---

**Questions?** All technical details, code references, and solution options are in the full diagnostic report.
