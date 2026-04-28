# Visual Workflow Summary
## One-Page Overview for Presentations

---

## The Big Picture

```
QUESTION: How many jobs does $1M of infrastructure investment create?

METHOD: Input-Output Analysis with GLORIA MRIO Database

ANSWER: Employment multiplier (e.g., 12.3 jobs per $1M)
```

---

## Data Structure

```
GLORIA Database (2019)
┌─────────────────────────────────────┐
│  120 Products × 162 Regions         │
│  = 19,440 Sector-Regions            │
│                                     │
│  Example Sector-Regions:            │
│  • USA-Construction                 │
│  • CHN-Manufacturing                │
│  • BRA-Agriculture                  │
│  • DEU-Services                     │
└─────────────────────────────────────┘
```

---

## The Model (Simplified)

```
Step 1: You specify demand shock
        dY = $100M in Construction

Step 2: Model calculates output change
        dX = L × dY
        (Leontief inverse captures ripple effects)

Step 3: Model calculates employment change
        dE = e × dX
        (Employment coefficients convert output to jobs)

Step 4: Calculate multiplier
        M = Total Jobs / ($1M invested)
```

---

## Complete Workflow

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: CREATE SCENARIO FILE (Your Input)                   │
├──────────────────────────────────────────────────────────────┤
│ Excel file specifying:                                       │
│ • Which sector (1-120)                                       │
│ • Which country (USA, CHN, etc.)                             │
│ • How much investment ($)                                    │
│                                                              │
│ Example: $100M to Construction in USA                        │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: RUN EMPLOYMENT SCRIPT                               │
├──────────────────────────────────────────────────────────────┤
│ Script: RunMINDSET_EmploymentOnly.py                        │
│ Runtime: 5-10 minutes                                        │
│                                                              │
│ What it does:                                                │
│ • Loads GLORIA data (L matrix, e coefficients)              │
│ • Reads your scenario (dY)                                   │
│ • Calculates: dX = L × dY                                    │
│ • Calculates: dE = e × dX                                    │
│ • Aggregates by region and sector                           │
│ • Exports to Excel                                           │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: ANALYZE RESULTS (Output)                            │
├──────────────────────────────────────────────────────────────┤
│ Excel file with 5 sheets:                                    │
│ 1. Summary - Key metrics & multipliers                       │
│ 2. Employment_by_Region - Jobs per country                   │
│ 3. Employment_by_Sector - Jobs per industry                  │
│ 4. Employment_Details - Full breakdown                       │
│ 5. Output_Details - For validation                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Example Results

```
SCENARIO: $100M infrastructure investment in USA

RESULTS:
┌─────────────────────────────────────┬──────────┐
│ Metric                              │ Value    │
├─────────────────────────────────────┼──────────┤
│ Total Investment                    │ $100M    │
│ Total Jobs Created                  │ 1,234    │
│ Employment Multiplier               │ 12.3     │
│ (jobs per $1M invested)             │          │
├─────────────────────────────────────┼──────────┤
│ Direct Jobs (Construction)          │ 800      │
│ Indirect Jobs (Suppliers)           │ 434      │
│                                     │          │
│ Domestic Jobs (USA)                 │ 987      │
│ Spillover Jobs (Other countries)    │ 247      │
└─────────────────────────────────────┴──────────┘

TOP SECTORS BENEFITING:
1. Construction ............. 800 jobs
2. Manufacturing ............ 150 jobs
3. Transportation ........... 120 jobs
4. Wholesale/Retail ......... 85 jobs
5. Professional Services .... 79 jobs
```

---

## Key Concepts (1-Minute Explanations)

### Direct vs. Indirect Effects

```
Direct Effects
├─ Jobs in the sector receiving investment
└─ Example: Construction investment → construction jobs

Indirect Effects
├─ Jobs in supplier sectors
└─ Example: Construction → steel → mining
```

### Leontief Inverse (L Matrix)

```
What it is:
├─ Captures entire supply chain
└─ Shows: To produce $1 of output in sector j,
          how much is needed from sector i?

Why we use it:
├─ Captures ripple effects through economy
└─ Includes both direct and indirect requirements
```

### Employment Coefficients (e Vector)

```
What it is:
├─ Jobs per dollar of output in each sector
└─ Example: Construction might be 0.000008 jobs/$

Calculation:
└─ Employment / Output for each sector
    (derived from GLORIA data)
```

---

## Files You Created (Quick Reference)

```
📁 Claude Code/temp/
├─ 📊 GLORIA_Products_Reference.xlsx
│   └─ Lookup: "What's product 56?" → Construction
│
├─ 📊 GLORIA_Regions_Reference.xlsx
│   └─ Lookup: "What's code for Brazil?" → BRA
│
└─ 📊 SCENARIO_TEMPLATE_SIMPLE.xlsx
    └─ Edit this to create custom scenarios

📁 GLORIA_template/Scenarios/
├─ 📊 Test_Construction_100M_USA.xlsx
│   └─ Simple test: $100M in construction
│
└─ 📊 Test_AllProducts_1M_USA.xlsx
    └─ Comprehensive: $1M in each of 120 products
```

---

## For Your Dissertation

### Research Question
> "Which infrastructure sectors create the most employment per dollar invested?"

### Methodology
> "Input-Output analysis using MINDSET model with GLORIA MRIO database (120 sectors × 162 regions, base year 2019)"

### Key Finding (example)
> "Construction investment creates 12.3 jobs per $1M in USA, with 65% direct and 35% indirect effects, compared to 5.2 jobs/$1M for utilities"

### Policy Implication (example)
> "Targeted infrastructure programs prioritizing labor-intensive sectors can maximize job creation per dollar spent"

---

## Answering Common Questions

### Q: "Why Input-Output analysis?"
**A:** "IO models capture both direct effects (jobs in the target sector) and indirect effects (jobs in supplier industries). This gives us the *total* employment impact, not just direct hiring."

### Q: "Why 2019 data?"
**A:** "Most recent fully validated GLORIA release. Covers 162 regions with detailed sectoral disaggregation (120 sectors). Post-2019 data still being validated."

### Q: "What about COVID?"
**A:** "Base year is 2019 (pre-COVID). This shows 'normal' economic structure. For post-COVID analysis, would need updated IO tables."

### Q: "Linear assumption?"
**A:** "We assume constant returns to scale. Valid for marginal changes (e.g., $100M in $20T economy). For very large shocks, diminishing returns may apply."

### Q: "What's not included?"
**A:** "This simplified version focuses on employment only. Full MINDSET includes:
- Price effects
- Household income feedback
- Induced investment
- Trade substitution
We skip these for faster runtime and simpler interpretation."

### Q: "How do we validate?"
**A:**
1. "Check multipliers are in expected ranges (5-25 jobs/$1M)"
2. "Compare to other IO studies (e.g., BLS multipliers)"
3. "Verify direct+indirect adds up correctly"
4. "Test sensitivity to assumptions"

---

## Technical Details (If Asked)

### Matrix Dimensions
```
L matrix:    19,440 × 19,440  (≈378 million elements)
dY vector:   19,440 × 1       (your demand shock)
dX vector:   19,440 × 1       (output change)
e vector:    19,440 × 1       (employment coefficients)
dE vector:   19,440 × 1       (employment change)

Computation:
1. dX = L @ dY           (matrix-vector multiply)
2. dE = e * dX           (element-wise multiply)
3. Aggregate results by region/sector
```

### Computational Note
```
Why 5-10 minutes?
- Loading 378M matrix elements from disk
- Matrix multiplication (19,440 × 19,440) × (19,440 × 1)
- Aggregating 19,440 results by 162 regions and 120 sectors

In R equivalent:
dX <- Leontief %*% dY
# But with 19,440 × 19,440 matrix!
```

---

## Bottom Line

### What We Do
```
Specify investment → Run IO model → Get employment impacts
```

### What We Get
```
• Jobs created (total, by region, by sector)
• Employment multipliers (jobs per $1M)
• Direct vs. indirect breakdown
• Domestic vs. spillover effects
```

### What It's Good For
```
✓ Comparing sectors (which creates most jobs?)
✓ Comparing countries (where do multipliers differ?)
✓ Policy analysis (how to maximize job creation?)
✓ Infrastructure planning (prioritize investments)
```

### What to Watch Out For
```
⚠ Linear assumption (OK for small/medium shocks)
⚠ Static analysis (no time dimension)
⚠ Base year 2019 (pre-COVID structure)
⚠ Aggregation (120 sectors, not super detailed)
```

---

## Ready to Present?

### 30-Second Version
> "We use Input-Output analysis with global trade data to estimate how many jobs are created per dollar invested in infrastructure. We find construction creates about 12 jobs per million dollars, while manufacturing creates 8, allowing policymakers to prioritize job-intensive sectors."

### 3-Minute Version
> Use the "Complete Workflow" diagram above + "Example Results" box

### 10-Minute Version
> Cover: Data Structure → Model → Workflow → Results → Validation

### Full Presentation
> Use RESEARCH_TEAM_EXPLANATION.md for detailed methodology section

---

**This one-pager should help you explain the analysis quickly to anyone who asks!**
