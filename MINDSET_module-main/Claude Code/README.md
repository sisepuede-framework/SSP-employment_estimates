# MINDSET Economic Impact Model

## Project Goal
Estimate **economic and employment impacts** of water, energy, and climate‑related investments using the **MINDSET framework** and a **Multi‑Regional Input–Output (MRIO)** model.

---

## Methodological Overview
- **Model Type:** Multi‑Regional Input–Output (MRIO)
- **Base Data:** Regional make–use tables, labor coefficients, and industry linkages
- **Analysis Focus:** California regions and national comparison areas
- **Expected Outputs:**
  - Regional economic impact tables (direct, indirect, induced)
  - Employment multipliers by sector and region
  - Policy scenario evaluations (e.g., infrastructure investment, climate adaptation spending)

---

## Data Folder Structure

| Folder | Description |
|---------|-------------|
| `input_tables/` | MRIO tables, regional coefficients, and parameters |
| `sector_mappings/` | Crosswalks between SOC, NAICS, and MINDSET sectors |
| `scripts/` | Executable code for MINDSET runs (.R, .py, etc.) |
| `results/` | Model output tables, figures, and logs |
| `config/` | Configuration files for model parameters |
| `older_materials/` | Archived versions of input and script files |
| `WORK_LOG.md` | Detailed log of all operations and changes |

---

## ⚠️ CRITICAL: Original Files Modified

**IMPORTANT:** Claude has modified original SourceCode files directly. This violates best practices and should NOT have been done.

### Modified Original Files (DO NOT USE THESE AS REFERENCE):

1. **SourceCode/InputOutput.py** ⚠️ ORIGINAL FILE MODIFIED
   - Lines 202-234: Modified `build_A_base()` to filter IND_BASE to selected regions
   - Lines 240-242: Modified save path for L_BASE to include "parsed_db_original" folder
   - **Impact:** L_BASE calculation now filters to 8 selected regions instead of using full dataset

2. **SourceCode/scenario.py** ⚠️ ORIGINAL FILE MODIFIED
   - Lines 326, 336: Removed `skiprows=14` from Excel loading
   - **Impact:** Reads investment scenario files without skipping header rows

3. **SourceCode/utils.py** ⚠️ ORIGINAL FILE MODIFIED
   - Lines 119, 122, 124, 257-263: Fixed pandas 3.13 compatibility issues
   - **Impact:** Works with Python 3.13 / pandas 2.x

4. **SourceCode/investment.py** ⚠️ ORIGINAL FILE MODIFIED
   - Lines 59-61: Filter to valid regions before sorting
   - Line 223: Fix PROD_COMM type conversion (float→int→str)
   - **Impact:** Handles region filtering and type conversion correctly

### Correct Procedure Going Forward:

**NEVER modify original SourceCode files.** Instead:
1. Create copies with modified names (e.g., `InputOutput_employment_only.py`)
2. Update import statements to use modified versions
3. Document changes in `WORK_LOG.md`
4. Keep originals intact for reference

If you need to revert to original MINDSET behavior, you will need to restore these files from version control or the original MINDSET distribution.

---

## Claude Code Collaboration Ground Rules

### 1. Stay Inside the Working Directory
All activity must occur within the current MINDSET project folder.
No access to OneDrive master folders or external directories unless explicitly approved.

### 2. No Overwriting Without Permission - ESPECIALLY Original Source Code
When editing files:
- **NEVER modify original SourceCode/ files directly**
- Create new versions with modified names instead
- First copy the original to `older_materials/` with a timestamp
- Record this action in `WORK_LOG.md`
- Then create or modify the new version

### 3. Autonomous Allowed Actions
Claude may autonomously:
- Read, explore, and summarize input tables  
- Execute MRIO simulations and compute baseline results  
- Produce intermediate CSVs, charts, or markdown documentation  
- Run reproducibility or sensitivity checks

Claude must **ask permission before**:  
- Changing the model structure or formulas  
- Expanding geographic scope or variable set  
- Performing bulk file operations affecting many folders  
- Rewriting original data tables

### 4. Version Control Protocol
- All updates tracked via Git once synced to GitHub.  
- Use clear commit messages such as:  
  `_commit: calibrated regional employment multipliers for CA–NV–TX_`.  
- Commit only within this forked workspace.

### 5. Data Protection
- Sensitive MRIO or proprietary data remain stored locally; Claude works only on safe copies.  
- Shared OneDrive materials should remain read‑only when linked to Claude.  
- Backups and version history should be enabled in OneDrive or Git.

### 6. Documentation Discipline
- Every model run, file update, or parameter adjustment logged in `WORK_LOG.md`.  
- Major methodological or analytical decisions added to the **Project Decisions** section below.


---

## Project Decisions
*(Add entries with date and description whenever key choices are made.)*

- **2026‑02‑15:** Template adapted from RAND Condo Production Study for MINDSET MRIO modeling with enhanced security workflow.

---

## Current Status

**Employment Impact Analysis: Ready for Production**

- ✅ Batch processing script completed and validated
- ✅ 469 scenarios ready (67 strategies × 7 countries)
- ✅ Direct, Indirect, and Total employment separation implemented
- ✅ Output structure: Employment by Region + Employment by Sector
- ✅ Grounded in original MINDSET methodology

**Next Steps:**
1. Run full batch processing (2-4 hours)
2. Analyze results in R
3. Validate employment multipliers
4. Generate visualizations for dissertation

---

## Documentation for Research Team

### 📘 Detailed Technical Documentation

For comprehensive understanding of MINDSET methodology and scripts:

**👉 [README_DETAILED.md](./README_DETAILED.md)** - Complete technical guide including:
- Step-by-step investment-to-employment flow with diagrams
- Detailed script documentation
- Mathematical formulas and calculations
- Data structure specifications
- Example analyses in R
- Troubleshooting guide

### 📄 Additional Documentation

- **[MINDSET_INVESTMENT_FLOW_DOCUMENTATION.md](./temp/MINDSET_INVESTMENT_FLOW_DOCUMENTATION.md)** - Technical reference based on original MINDSET source code
- **[SCENARIO_QUICK_REFERENCE.md](./temp/SCENARIO_QUICK_REFERENCE.md)** - Quick reference for scenario files
- **[README_START_HERE.md](./temp/README_START_HERE.md)** - Getting started guide

---

## Quick Start

### Running Employment Analysis

**For full batch processing (all 469 scenarios):**

```bash
cd "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main/Claude Code/temp"

python RunMINDSET_EmploymentOnly_BATCH_FINAL.py
```

**Expected runtime:** 2-4 hours

**Output files:**
- `GLORIA_results/ALL_RESULTS_Employment_by_Region.csv` (~76,000 rows)
- `GLORIA_results/ALL_RESULTS_Employment_by_Sector.csv` (~56,000 rows)
- `GLORIA_results/BATCH_SUMMARY.csv` (469 rows)

**For testing a single scenario:**

```python
# Edit line 104 in RunMINDSET_EmploymentOnly.py:
scenario_name = "Strategy_1004_MEX"

# Run:
python RunMINDSET_EmploymentOnly.py
```

---

## Key Concepts

### Investment-to-Employment Chain

```
Investment Scenario
    ↓
Investment Converter (sector → products)
    ↓
Leontief IO Model (direct + supply chain)
    ↓
Employment Calculation (jobs = coeff × output)
    ↓
Results: Direct, Indirect, Total Employment
```

### Direct vs Indirect Employment

- **Direct Employment:** Jobs producing the initially demanded goods (first-round effect)
- **Indirect Employment:** Jobs in supply chain sectors (Leontief multiplier effect)
- **Total Employment:** Direct + Indirect

**Example:** Construction invests $10M
- Creates demand for cement, steel, machinery
- Those sectors need inputs (limestone, iron ore, energy)
- Direct jobs: 120 (producing investment goods)
- Indirect jobs: 80 (producing supply chain inputs)
- Total: 200 jobs (multiplier: 20 jobs/$1M)

---

## Best Practices Summary
- Keep all Claude operations limited to this forked workspace  
- Always preserve originals before any modification  
- Maintain clear documentation for every modeling step  
- Review results and methodological decisions before merging outputs into production  
- Use version control for each meaningful update

---

## Project Decisions (Recent)

- **2026-03-20:** Completed employment impact batch processing system
  - Implemented Direct vs Indirect employment separation based on standard IO theory
  - Created comprehensive technical documentation for research team
  - Validated against original MINDSET source code
  - Ready for production runs (469 scenarios)

---

*Last updated: 2026-03-20*