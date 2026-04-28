# MINDSET Employment Analysis - Complete Workflow

## Purpose
Calculate Direct, Indirect, and Total employment impacts from investment scenarios using MINDSET's Input-Output model.

---

## Prerequisites

### 1. Software Requirements
- Python 3.13 (or compatible)
- Required packages: pandas, numpy, scipy, openpyxl, tqdm, alive-progress

### 2. Data Requirements
- GLORIA v57 parsed database (8 countries, 120 sectors)
  - Location: `GLORIA_db/v57/2019/parsed_db_original/`
  - Countries: BGR, BLZ, EGY, LBY, MAR, MEX, UGA, + 1 other
- Investment scenario files (469 total)
  - Location: `GLORIA_template/Scenarios/`
  - Format: `Strategy_[ID]_[COUNTRY].xlsx`
  - Structure: 67 strategies × 7 countries

### 3. File Structure
```
MINDSET_module-main/
├── SourceCode/                    # Core MINDSET modules
├── GLORIA_db/v57/2019/
│   └── parsed_db_original/        # Base GLORIA data
├── GLORIA_template/
│   ├── Scenarios/                 # Investment scenario files
│   └── Variables/                 # Configuration files
├── Claude Code/
│   └── temp/                      # Analysis scripts
└── Results/                       # Output directory (created automatically)
```

---

## ONE-TIME SETUP (First Time Only)

### Step 1: Calculate Leontief Inverse Matrix (L_BASE)

**What it does:**
- Calculates L = (I - A)^(-1) from GLORIA technical coefficients
- This captures direct + indirect economic linkages (supply chain multipliers)
- Required for estimating indirect employment effects

**When to run:**
- ✅ First time using MINDSET
- ✅ If you change GLORIA countries/year
- ❌ NOT needed for each scenario (reused for all 469 scenarios)

**How to run:**
```bash
cd "MINDSET_module-main\MINDSET_module-main"

# Close all other applications to maximize RAM
python "Claude Code/temp/CALCULATE_L_BASE_ONCE.py"
```

**Expected output:**
```
ONE-TIME CALCULATION: Leontief Inverse Matrix (L_BASE)
================================================================================

STEP 1: Loading GLORIA data...
OK - Loaded in 5.2 seconds

STEP 2: Initializing IO model...
OK

STEP 3: Building technical coefficient matrix (A)...
OK - Built A matrix: (960, 960)
  Time: 2.1 seconds

STEP 4: Calculating Leontief inverse: L = (I - A)^(-1)
  This is the memory-intensive step
  Progress will be shown below...

L_base inversion: 00:01 mins

================================================================================
✓ SUCCESS! L_BASE calculated and saved
================================================================================
Matrix size: (960, 960)
Total time: 45.3 seconds

File saved to:
  GLORIA_db\v57\2019\parsed_db_original\GLORIA_L_Base_2019.mat

This matrix will now be automatically loaded for all 469 scenario runs.
You will NOT need to run this script again.
```

**Expected file size:** ~7 MB (for 960×960 matrix with 8 countries)

**Troubleshooting:**
- If you get MemoryError: Close more applications, or restart computer
- If file is >100 MB: Wrong dimensions - check that Variable_list matches your 8-country data

---

## TESTING (Validate One Scenario)

### Step 2: Test Single Scenario

**Purpose:** Verify all steps work before running batch processing

**How to run:**
```bash
python "Claude Code/temp/TEST_ONE_SCENARIO.py"
```

**What it tests:**
- Scenario: Strategy_1004_MEX.xlsx
- STEP 1: Load MRIO data
- STEP 2: Load investment scenario ($1,000,000)
- STEP 3: Convert investment → product demand
- STEP 4: Calculate output changes (using L_BASE)
- STEP 5: Calculate employment impacts

**Expected output:**
```
================================================================================
TEST: SINGLE SCENARIO EMPLOYMENT ESTIMATION
================================================================================

Test scenario: Strategy_1004_MEX
Scenario file: [...]\Strategy_1004_MEX.xlsx
File exists: True

--------------------------------------------------------------------------------
STEP 1: Loading MRIO Data
--------------------------------------------------------------------------------
--- Collected exogenous variables: 5.1 s ---
OK - MRIO data loaded in 5.1 seconds
OK - Countries: 164, Sectors: 120

--------------------------------------------------------------------------------
STEP 2: Loading Investment Scenario
--------------------------------------------------------------------------------
OK - Investment loaded: $1,000,000
OK - Investment entries: 120

--------------------------------------------------------------------------------
STEP 3: Converting Investment to Product Demand
--------------------------------------------------------------------------------
OK - Investment converted to product demand
OK - Initial final demand (dy): $205,516
OK - Time: 2.3 seconds

--------------------------------------------------------------------------------
STEP 4: Calculating Output Changes (IO Model)
--------------------------------------------------------------------------------
OK - L_BASE loaded from file
OK - Output changes calculated
OK - Total output change (dq): $[VALUE]
OK - Time: 1.2 seconds

--------------------------------------------------------------------------------
STEP 5: Calculating Employment Changes
--------------------------------------------------------------------------------
OK - Employment coefficients loaded
OK - Direct jobs: [VALUE]
OK - Indirect jobs: [VALUE]
OK - Total jobs: [VALUE]
OK - Time: 0.8 seconds

================================================================================
✓ SUCCESS - All steps completed
================================================================================
Total processing time: 9.5 seconds
```

**If test fails:**
- Check that L_BASE file exists and is correct size (~7 MB)
- Verify Strategy_1004_MEX.xlsx exists in Scenarios folder
- Check Claude Code/WORK_LOG.md for previous fixes applied

---

## BATCH PROCESSING (Run All 469 Scenarios)

### Step 3: Run All Scenarios

**What it does:**
- Loops through all 469 strategy-country combinations
- For each scenario:
  1. Load investment data
  2. Convert to product demand
  3. Calculate output changes (using L_BASE)
  4. Calculate Direct, Indirect, Total employment
  5. Save results to CSV

**How to run:**
```bash
python "Claude Code/temp/RunMINDSET_EmploymentOnly_BATCH_FINAL.py"
```

**Expected output:**
```
================================================================================
MINDSET EMPLOYMENT-ONLY BATCH PROCESSOR
================================================================================

Configuration:
  Strategies: 67
  Countries: 7
  Total scenarios: 469
  Scenarios folder: GLORIA_template\Scenarios

Loading MRIO data (one-time, used for all scenarios)...
--- Collected exogenous variables: 5.2 s ---
OK - MRIO loaded

================================================================================
PROCESSING SCENARIOS
================================================================================

[1/469] Strategy_1001_BGR
  ✓ Direct: 123 jobs | Indirect: 456 jobs | Total: 579 jobs
  Time: 2.1s

[2/469] Strategy_1001_BLZ
  ✓ Direct: 89 jobs | Indirect: 234 jobs | Total: 323 jobs
  Time: 1.9s

...

[469/469] Strategy_1067_UGA
  ✓ Direct: 156 jobs | Indirect: 567 jobs | Total: 723 jobs
  Time: 2.0s

================================================================================
BATCH PROCESSING COMPLETE
================================================================================

Total scenarios processed: 469
Successful: 469
Failed: 0
Total time: 15.3 minutes
Average time per scenario: 2.0 seconds

Results saved to:
  Results/Employment_Results_All_Scenarios.csv
  Results/Employment_Summary_Statistics.csv
```

**Estimated run time:**
- Per scenario: ~2 seconds
- Total for 469 scenarios: ~15-20 minutes

**Output files:**

1. **Employment_Results_All_Scenarios.csv**
   - Detailed results for all scenarios
   - Columns: Strategy_ID, Country, Sector, Direct_Jobs, Indirect_Jobs, Total_Jobs, Region, Sector_Name

2. **Employment_Summary_Statistics.csv**
   - Aggregated results by strategy and country
   - Columns: Strategy_ID, Country, Total_Direct_Jobs, Total_Indirect_Jobs, Total_Jobs, Multiplier

---

## UNDERSTANDING THE RESULTS

### Employment Impact Types

**1. Direct Employment**
- Formula: `e × dy`
- First-round effect from initial final demand
- Jobs created directly by the investment spending
- Example: Construction workers building the infrastructure

**2. Indirect Employment**
- Formula: `e × (L × dy - dy)`
- Supply chain multiplier effect
- Jobs created in upstream industries supplying inputs
- Example: Steel workers, cement producers, equipment manufacturers

**3. Total Employment**
- Formula: `Direct + Indirect = e × (L × dy)`
- Complete economic impact including supply chains
- This is the full job creation from the investment

**4. Employment Multiplier**
- Formula: `Total / Direct`
- Shows how many total jobs are created per direct job
- Typical range: 1.5 to 3.0
- Higher multiplier = stronger supply chain linkages

### Interpreting Results

**Key columns in output:**
- `Strategy_ID`: Investment strategy identifier (1001-1067)
- `Country`: 3-letter ISO code (BGR, BLZ, EGY, LBY, MAR, MEX, UGA)
- `Sector`: GLORIA sector code (1-120)
- `Direct_Jobs`: Jobs from initial spending
- `Indirect_Jobs`: Jobs from supply chain
- `Total_Jobs`: Sum of Direct + Indirect
- `Multiplier`: Total/Direct ratio

**Example interpretation:**
```
Strategy_1004, MEX, Total_Jobs: 1,234
  Direct: 456 jobs
  Indirect: 778 jobs
  Multiplier: 2.7
```
→ A $1M investment in Strategy 1004 in Mexico creates 1,234 total jobs, with a multiplier of 2.7 (each direct job creates 1.7 additional indirect jobs through supply chains)

---

## TROUBLESHOOTING

### Common Issues

**1. "AttributeError: 'IO' object has no attribute 'L_BASE'"**
- **Cause:** L_BASE file not found or not loading correctly
- **Fix:** Run CALCULATE_L_BASE_ONCE.py to create the file
- **Verify:** Check file exists at `GLORIA_db\v57\2019\parsed_db_original\GLORIA_L_Base_2019.mat`

**2. "ValueError: shapes (960,) and (19680,19680) not aligned"**
- **Cause:** Dimension mismatch between dy vector and L_BASE matrix
- **Fix:** Delete old L_BASE file and recalculate with correct dimensions
- **Note:** L_BASE should be 960×960 for 8-country data, NOT 19680×19680

**3. "KeyError: 'L_base' not in index"**
- **Cause:** L_BASE loaded as dictionary, not extracted as array
- **Fix:** Already fixed in exog_vars_SSP.py lines 60-66
- **Check:** Ensure you're using the updated code

**4. "ModuleNotFoundError: No module named 'SourceCode.log'"**
- **Cause:** Missing log module (not needed for employment-only analysis)
- **Fix:** Already handled with MockLog class in scripts
- **Note:** This is expected and harmless

**5. Investment total doesn't match expected value**
- **Cause:** Missing sector codes in scenario file
- **Fix:** Open Excel file, find empty "Sector investing code*" cells, fill them in
- **Verify:** Check that sum of "Value*" column matches expected total

---

## TECHNICAL NOTES

### Data Dimensions
- **Countries:** 8 active (from parsed GLORIA data)
- **Sectors:** 120 (GLORIA v57 classification)
- **Total dimensions:** 960 (8 × 120)
- **L_BASE matrix:** 960 × 960 = ~7 MB
- **dy vector:** 960 × 1 (most elements are zero)
- **dq vector:** 960 × 1 (output changes)

### Key Formulas
```
Technical coefficients:  A = inputs/output
Leontief inverse:       L = (I - A)^(-1)
Output change:          dq = L × dy
Employment change:      dE = e × dq
```

Where:
- `A` = technical coefficient matrix (how much input needed per unit output)
- `I` = identity matrix
- `L` = Leontief inverse (direct + indirect effects multiplier)
- `dy` = final demand shock (from investment)
- `dq` = total output change (direct + indirect)
- `e` = employment coefficients (jobs per unit output)
- `dE` = employment change (jobs created)

### ⚠️ CRITICAL WARNING: Original Files Were Modified

**This violates best practices. Original SourceCode files should NEVER be modified directly.**

The following original MINDSET source files were modified:

1. **SourceCode/InputOutput.py** (lines 202-234, 240-242)
   - Modified `build_A_base()` to filter IND_BASE to selected 8 regions
   - Modified L_BASE save path to include "parsed_db_original" folder
   - **This fundamentally changes how MINDSET builds the Leontief matrix**

2. **SourceCode/exog_vars_SSP.py** (lines 60-66, 77-82, 117-125)
   - Added logic to extract L_base array from .mat dict
   - Added NPISH_BASE default
   - Added INV_BASE default

3. **SourceCode/scenario.py** (lines 326, 336)
   - Removed skiprows=14 from Excel loading

4. **SourceCode/utils.py** (lines 119, 122, 124, 257-263)
   - Fixed pandas 3.13 compatibility (4 fixes)

5. **SourceCode/investment.py** (lines 59-61, 223)
   - Filter to valid regions before sorting
   - Fix PROD_COMM type conversion

**To revert to original MINDSET:** You will need to restore these files from the original MINDSET distribution or version control.

**Correct procedure:** Create modified copies (e.g., `InputOutput_modified.py`) and update imports, never alter originals.

---

## SUMMARY CHECKLIST

### First-Time Setup (Do Once)
- [ ] Install Python 3.13 and required packages
- [ ] Verify GLORIA data in parsed_db_original/ (8 countries)
- [ ] Verify 469 scenario files in Scenarios/
- [ ] Run CALCULATE_L_BASE_ONCE.py (creates ~7 MB file)
- [ ] Verify L_BASE file created successfully

### Before Each Analysis (Testing)
- [ ] Run TEST_ONE_SCENARIO.py
- [ ] Verify all 5 steps complete successfully
- [ ] Check employment results look reasonable

### Production Run
- [ ] Run RunMINDSET_EmploymentOnly_BATCH_FINAL.py
- [ ] Wait 15-20 minutes for 469 scenarios
- [ ] Check Results/ folder for output CSVs
- [ ] Verify all scenarios processed successfully

### Using Results
- [ ] Open Employment_Results_All_Scenarios.csv
- [ ] Filter/pivot by Strategy_ID and Country as needed
- [ ] Calculate multipliers: Total_Jobs / Direct_Jobs
- [ ] Aggregate by sector, region, or strategy as needed

---

## SUPPORT

For issues or questions:
1. Check Claude Code/WORK_LOG.md for session notes and fixes
2. Review this WORKFLOW document for common issues
3. Check test output files in Claude Code/temp/ for diagnostics
4. Verify file locations and dimensions match this guide

Last updated: 2026-03-21
MINDSET Version: GLORIA v57, Python 3.13
