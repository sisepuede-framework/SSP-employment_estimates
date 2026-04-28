# Employment Impact Analysis Methodology
## Technical Documentation for Research Team

**Document Purpose:** Explain the MINDSET employment analysis workflow, data structure, and methodology

**Author:** [Your Name]
**Date:** March 2026
**For:** Dissertation research team and committee

---

## 1. Overview

### What We're Doing

We are using the **MINDSET model** to estimate employment impacts of infrastructure investments using a Multi-Regional Input-Output (MRIO) framework based on the **GLORIA database**.

**Core Question:** How many jobs are created per dollar invested in different economic sectors?

**Key Output:** Employment multipliers (jobs per $1M invested) for 120 economic sectors across 162 regions.

---

## 2. Data Structure

### GLORIA Database (v57, 2019)

The GLORIA (Global Resource Input-Output Assessment) database is a comprehensive MRIO dataset that captures:

| Dimension | Count | Description |
|-----------|-------|-------------|
| **Products/Sectors** | 120 | Economic activities (agriculture, manufacturing, construction, services) |
| **Regions** | 162 | Countries and regional aggregates |
| **Sector-Regions** | 19,440 | Unique combinations (120 × 162) |
| **Base Year** | 2019 | Most recent fully parsed data |

**Example Sector-Regions:**
- USA-Construction
- CHN-Manufacturing
- BRA-Agriculture
- DEU-Services

Each sector-region has:
- Input-output coefficients (technical requirements)
- Employment coefficients (jobs per unit of output)
- Trade linkages with all other sector-regions

### Key Matrices

1. **Leontief Inverse (L):** 19,440 × 19,440 matrix
   - Captures direct + indirect production requirements
   - Element L[i,j] = total output from sector i needed for one unit of final demand in sector j
   - Used to calculate: **dX = L × dY**

2. **Employment Coefficients (e):** 19,440 × 1 vector
   - Jobs per dollar of output for each sector-region
   - Derived from GLORIA employment data
   - Used to calculate: **dE = e × dX**

---

## 3. Methodology

### Theoretical Framework

Our analysis is based on the **Leontief Input-Output Model:**

```
System of equations:
X = AX + Y

Where:
- X = total output vector (production)
- A = technical coefficients matrix (input requirements)
- Y = final demand vector (consumption, investment, exports)

Solution:
X = (I - A)^(-1) × Y
X = L × Y

Where L = (I - A)^(-1) is the Leontief inverse
```

### Employment Extension

We extend the standard IO model to employment:

```
Employment equation:
E = e × X

Where:
- E = employment vector
- e = employment coefficient vector (diagonal matrix)
- X = output vector

Changes due to demand shock:
dE = e × dX
dE = e × L × dY

Where:
- dY = change in final demand (our investment shock)
- dX = change in output
- dE = change in employment
```

### Employment Multiplier

```
Employment Multiplier = Total Jobs Created / Investment ($M)

M_employment = Σ(dE) / (dY / 1,000,000)

Interpretation:
- M = 10 means: $1M investment creates 10 jobs
- M = 15 means: $1M investment creates 15 jobs
- Higher multiplier = more job-intensive sector
```

---

## 4. Workflow Process

### Step 1: Define Scenario (Input)

**What:** Create Excel file specifying demand shocks

**Format:**
| Column | Description | Example |
|--------|-------------|---------|
| Producing country ISO* | Country producing | USA |
| Consuming country ISO* | Country consuming | USA |
| Product code* | Sector (1-120) | 56 (Construction) |
| FD code* | Demand category | FD_4 (Investment) |
| Value* | Amount (USD) | 100,000,000 |
| Type* | Value type | abs-b (absolute) |

**Example Scenarios:**

**Scenario A: Single Sector Test**
```
USA → USA → Product 56 (Construction) → $100M
```
Tests: Infrastructure investment employment impact

**Scenario B: Cross-Sector Comparison**
```
USA → USA → Product 1 → $1M
USA → USA → Product 2 → $1M
...
USA → USA → Product 120 → $1M
```
Tests: Which sectors create most jobs per dollar

**Scenario C: Cross-Country Comparison**
```
USA → USA → Product 56 → $100M
CHN → CHN → Product 56 → $100M
BRA → BRA → Product 56 → $100M
```
Tests: How employment multipliers differ by country

### Step 2: Run Employment Model

**Script:** `RunMINDSET_EmploymentOnly.py`

**What it does:**

1. **Load GLORIA data** (L matrix, e coefficients, country/sector lists)
2. **Load scenario file** (extract dY vector)
3. **Calculate output changes:**
   ```python
   dX = L @ dY  # Matrix multiplication
   ```
4. **Calculate employment changes:**
   ```python
   dE = e * dX  # Element-wise multiplication
   ```
5. **Aggregate results** (by region, by sector)
6. **Calculate multipliers**
7. **Export to Excel**

**Runtime:** 5-10 minutes (loads 19,440 × 19,440 = 378M elements)

### Step 3: Analyze Results (Output)

**Output:** Excel file with 5 sheets

**1. Summary Sheet**
- Total investment
- Total jobs created
- Employment multiplier
- Output multiplier

**2. Employment_by_Region**
- Jobs created in each country
- Sorted by impact
- Shows: Domestic + spillover effects

**3. Employment_by_Sector**
- Jobs created in each industry
- Sorted by impact
- Shows: Direct + indirect effects

**4. Employment_Details**
- Full 19,440-row breakdown
- Every sector-region combination
- For detailed analysis

**5. Output_Details**
- Output changes (dX)
- For validation and diagnostics

---

## 5. Key Concepts

### Direct vs. Indirect Effects

**Direct effects:**
- Jobs in the sector receiving the investment
- Example: Construction investment → construction jobs

**Indirect effects:**
- Jobs in upstream supplier sectors
- Example: Construction investment → steel jobs → mining jobs

**The Leontief inverse captures BOTH automatically**

### Domestic vs. Spillover Effects

**Domestic effects:**
- Jobs created in the country receiving investment
- Example: USA investment → USA jobs

**Spillover effects:**
- Jobs created in other countries through trade linkages
- Example: USA investment → imports from China → Chinese jobs

**GLORIA captures international trade linkages**

### Final Demand Categories

| Code | Category | Description |
|------|----------|-------------|
| FD_1 | Household consumption | Consumer purchases |
| FD_2 | NPISH | Non-profit institutions |
| FD_3 | Government spending | Public sector |
| **FD_4** | **Investment** | **Capital formation (our focus)** |
| FD_5 | Inventory changes | Stock adjustments |
| FD_6 | Valuables | Precious metals, art |

**We use FD_4** for infrastructure investment scenarios.

---

## 6. Data Files Created

### Reference Files (for lookup)

**1. GLORIA_Products_Reference.xlsx**
- All 120 products with codes and names
- Use when: Creating scenarios, interpreting results
- Example: "What's product 56?" → Construction

**2. GLORIA_Regions_Reference.xlsx**
- All 162 regions with ISO codes and names
- Use when: Specifying countries in scenarios
- Example: "What's the code for Brazil?" → BRA

**3. SCENARIO_TEMPLATE_SIMPLE.xlsx**
- Editable template with examples
- Use when: Creating custom scenarios
- Edit and save to GLORIA_template/Scenarios/

### Ready-to-Run Scenarios

**4. Test_Construction_100M_USA.xlsx**
- Simple test: $100M in construction
- Purpose: Verify model works
- Expected result: ~12-15 jobs/$1M (typical for construction)

**5. Test_AllProducts_1M_USA.xlsx**
- Comprehensive: $1M in each of 120 products
- Purpose: Compare all sectors
- Expected result: Ranking of sectors by employment intensity

---

## 7. Validation and Checks

### Expected Ranges

**Employment Multipliers (jobs/$1M):**
- **Low (5-10):** Capital-intensive sectors (heavy manufacturing, utilities)
- **Medium (10-15):** Construction, light manufacturing
- **High (15-25):** Labor-intensive services (health, education, retail)

**Output Multipliers:**
- **Typical range:** 1.5 - 2.5
- Interpretation: $1 of final demand → $1.50-$2.50 total output
- Below 1.5: Low backward linkages
- Above 2.5: High integration (check for errors)

### Validation Steps

1. **Check totals:**
   - Does employment sum across regions match total?
   - Does output sum across sectors match?

2. **Check reasonableness:**
   - Are multipliers in expected ranges?
   - Do results make economic sense?

3. **Compare to literature:**
   - How do our multipliers compare to other IO studies?
   - Are results consistent with known employment intensities?

4. **Sensitivity analysis:**
   - Test different investment amounts (linear assumption)
   - Test different sectors (compare results)
   - Test different countries (compare multipliers)

---

## 8. Limitations and Assumptions

### Model Assumptions

1. **Linear technology**
   - Constant returns to scale
   - Fixed input-output coefficients
   - No capacity constraints

2. **Static analysis**
   - Single time period
   - No dynamic effects
   - No investment-induced productivity changes

3. **Demand-driven**
   - Assumes supply is elastic
   - No supply constraints
   - Prices held constant

4. **Employment-only focus**
   - Skips price effects
   - Skips household income feedback
   - Skips induced investment
   - Faster runtime, simpler interpretation

### Data Limitations

1. **Base year: 2019**
   - Pre-COVID structure
   - May not reflect current technology
   - Trade patterns may have changed

2. **Aggregation**
   - 120 sectors (less detailed than some IO tables)
   - Regional aggregates (not all countries separate)

3. **Employment coefficients**
   - Based on GLORIA employment satellite accounts
   - May not capture informal employment
   - Averages across heterogeneous firms

---

## 9. Interpretation Guide

### For Your Dissertation

**Research Question:**
"Which infrastructure sectors create the most employment per dollar invested?"

**Methodology:**
"We use the MINDSET model with GLORIA MRIO data to estimate employment multipliers for 120 sectors using Leontief input-output analysis."

**Key Finding (example):**
"Construction investment creates an average of 12.3 jobs per $1M invested in the USA, with 65% direct effects and 35% indirect effects in supplier industries."

**Policy Implication (example):**
"Labor-intensive sectors like construction generate more employment per dollar than capital-intensive sectors like utilities (5.2 jobs/$1M), suggesting targeted infrastructure programs can maximize job creation."

### For Research Team Discussions

**Question 1: "Why 120 sectors?"**
Answer: "GLORIA aggregation level balances detail with computational feasibility. More disaggregated data exists but increases runtime significantly."

**Question 2: "Why 2019 data?"**
Answer: "Most recent fully validated GLORIA release. Post-2019 data still being processed and validated."

**Question 3: "Does this include wages/income?"**
Answer: "Employment-only version focuses on job count. Can be extended to include wage effects and household income feedback loops if needed."

**Question 4: "What about productivity changes?"**
Answer: "This is a static model. For dynamic effects (productivity growth, induced investment), would need multi-period extension."

**Question 5: "How accurate are the multipliers?"**
Answer: "IO multipliers are well-established in economics. Uncertainty comes from: (1) base year data accuracy, (2) assumption that relationships are stable, (3) aggregation level. Typical validation: compare to other IO studies."

---

## 10. Next Steps in Analysis

### Phase 1: Descriptive Analysis
1. Run Test_AllProducts_1M_USA.xlsx
2. Rank sectors by employment multiplier
3. Identify highest job-creating sectors
4. Plot: Bar chart of top 20 sectors

### Phase 2: Sectoral Analysis
1. Group 120 products into broader categories
   - Agriculture (1-15)
   - Manufacturing (16-55)
   - Construction (56)
   - Services (57-120)
2. Compare average multipliers by category
3. Decompose: Direct vs. indirect effects

### Phase 3: Geographic Analysis
1. Run same scenario for multiple countries
2. Compare USA vs. China vs. Brazil
3. Analyze why multipliers differ
   - Labor intensity differences
   - Import dependencies
   - Wage levels

### Phase 4: Policy Analysis
1. Simulate realistic investment portfolios
2. Calculate weighted average multipliers
3. Compare alternative investment strategies
4. Sensitivity to investment composition

---

## 11. References and Further Reading

### MINDSET Model
- Original model developed by World Bank economists
- Based on GTAP (Global Trade Analysis Project) framework
- Extended with GLORIA MRIO database

### GLORIA Database
- Lenzen et al. (2013): "Building Eora: A Global Multi-Regional Input-Output Database at High Country and Sector Resolution"
- Updated annually by University of Sydney team
- Open access: gloria-mrio.com

### Input-Output Analysis
- Miller & Blair (2009): *Input-Output Analysis: Foundations and Extensions*
- Leontief (1986): *Input-Output Economics* (2nd edition)
- Ten Raa (2005): *The Economics of Input-Output Analysis*

### Employment Multipliers
- BLS Input-Output models (US Bureau of Labor Statistics)
- ILO employment impact assessment guides
- Infrastructure employment literature (World Bank, ILO)

---

## 12. Technical Support

### Script Locations
- Main script: `RunMINDSET_EmploymentOnly.py`
- Scenario creator: `ANNOTATED_CREATOR_WITH_EXPLANATIONS.py`
- Documentation: `Claude Code/temp/` folder

### Data Locations
- GLORIA database: `GLORIA_db/v57/2019/parsed_db_original/`
- Product/region lists: `GLORIA_template/Variables/`
- Scenario files: `GLORIA_template/Scenarios/`
- Results: `GLORIA_results/`

### Getting Help
- Full guides in: `Claude Code/temp/`
- R vs Python comparisons: `PATH_FIX_EXPLAINED.md`
- Beginner guide: `BEGINNER_GUIDE.md`
- Step-by-step: `POSITRON_STEP_BY_STEP.md`

---

## Appendix A: Equation Summary

### Core Model

```
1. Output determination:
   X = (I - A)^(-1) × Y
   X = L × Y

   Where:
   X = gross output vector (19,440 × 1)
   A = technical coefficients matrix (19,440 × 19,440)
   I = identity matrix
   L = Leontief inverse
   Y = final demand vector (19,440 × 1)

2. Employment determination:
   E = e × X

   Where:
   E = employment vector (19,440 × 1)
   e = employment coefficients (19,440 × 1)

3. Impact analysis:
   dX = L × dY
   dE = e × dX = e × L × dY

4. Multipliers:
   Output multiplier = Σ(dX) / Σ(dY)
   Employment multiplier = Σ(dE) / (Σ(dY) / 1,000,000)
```

### Matrix Dimensions

```
GLORIA v57 dimensions:
- Products (P): 120
- Regions (R): 162
- Sector-regions (N): P × R = 19,440

Matrix sizes:
- L: N × N = 19,440 × 19,440 ≈ 378M elements
- dY: N × 1 = 19,440 × 1
- dX: N × 1 = 19,440 × 1
- e: N × 1 = 19,440 × 1
- dE: N × 1 = 19,440 × 1
```

---

**End of Technical Documentation**

*This document provides the technical foundation for understanding and explaining the employment impact analysis methodology to research teams, dissertation committees, and policy stakeholders.*
