# File Inventory: MINDSET Employment Analysis
## Complete List of Files Created and Used

**Purpose:** Document all files involved in the employment estimation workflow, their purposes, creation methods, and relationships.

---

## Table of Contents

1. [File Overview](#file-overview)
2. [Manual Files (Pre-existing)](#manual-files-pre-existing)
3. [Generated Data Files](#generated-data-files)
4. [Scripts Created](#scripts-created)
5. [Output Files](#output-files)
6. [Documentation Files](#documentation-files)
7. [File Dependencies](#file-dependencies)

---

## File Overview

### File Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Manual Input Files | 4 | Pre-existing data and configurations |
| Generated Data Files | ~15 | Aggregated MRIO data |
| Scripts | 5 | Data processing and analysis |
| Output Files | 1 | Final consolidated results |
| Documentation | 4 | Methodology and guides |
| **Total** | **~29** | **Complete workflow** |

---

## Manual Files (Pre-existing)

### 1. GLORIA-Eora26 - Crosswalk.xlsx
**Location:** `C:\Users\festeves\...\Data\GLORIA-Eora26 - Crosswalk.xlsx`

**Purpose:** Maps 120 GLORIA products to 20 ISIC economic sectors

**Structure:**
- **Sheet used:** "GLORIA (v60) - ISIC concordance"
- **Dimensions:** 121 rows × 21 columns
- **Format:** Binary matrix (1 = product belongs to sector, 0 = does not)
- **Special case:** First row contains sector descriptions
- **Columns:** Product name + 20 ISIC sections (A-T)

**Created by:** External source (GLORIA/ISIC concordance table)

**Used by:**
- `BATCH_EMPLOYMENT_ALL_STRATEGIES.py`
- `TEST_FINAL_CLEAN.py`

**Why needed:** GLORIA's 120 products are too granular for policy analysis. ISIC's 20 sectors are the international standard for economic reporting.

---

### 2. ATTRIBUTE_STRATEGY.csv
**Location:** `C:\Users\festeves\...\Data\ATTRIBUTE_STRATEGY.csv`

**Purpose:** Provides human-readable names for strategy IDs

**Structure:**
```
strategy_id,strategy
0,Baseline NDP
1,Test AFOLU
2,Test Energy
1001,AFOLU Specific Strategies Start
...
```

**Dimensions:** 92 rows × 2 columns

**Created by:** Manual compilation (strategy metadata)

**Used by:**
- `BATCH_EMPLOYMENT_ALL_STRATEGIES.py`

**Why needed:** Converts "Strategy_1004_EGY" into interpretable descriptions like "Agricultural Infrastructure Investment - Egypt Baseline"

**Note:** Not all 469 strategies have entries (some will show NaN in strategy_name)

---

### 3. Strategy Investment Files (469 files)
**Location:** `MINDSET_module-main/GLORIA_template/Scenarios/`

**Naming pattern:** `Strategy_[ID]_[COUNTRY].xlsx`

**Examples:**
- `Strategy_1001_BGR.xlsx`
- `Strategy_1004_EGY.xlsx`
- `Strategy_1004_MEX.xlsx`
- ... (469 total)

**Purpose:** Specify investment amounts by product for each strategy

**Structure (Excel):**
- **Rows:** Product codes (1-120)
- **Columns:** Investment specifications
- **Key column:** "dk" (investment amount in thousands USD)

**Created by:** Manual scenario design (research team)

**Used by:**
- `scenario.py` (MINDSET module)
- `BATCH_EMPLOYMENT_ALL_STRATEGIES.py`

**Why needed:** These are the policy scenarios we're analyzing. Each file represents a different infrastructure investment strategy.

---

### 4. Variable_list_MINDSET_SSP.xlsx
**Location:** `MINDSET_module-main/GLORIA_template/Variable_list_MINDSET_SSP.xlsx`

**Purpose:** Tells MINDSET where to find data files

**Structure:**
- Lists all data files MINDSET should load
- Specifies paths (pointing to SSP subfolder for aggregated data)
- Indicates data types (DataFrame, sparse matrix, etc.)

**Created by:** Modified from original MINDSET template

**Used by:**
- `exog_vars_SSP.py` (reads this file to know what to load)

**Key modification:** Paths point to `GLORIA_db/v57/2019/SSP/` instead of root folder

**Why needed:** MINDSET is modular and data-driven. This file configures which data to load.

---

## Generated Data Files

### SSP Aggregated Data (Created Once)

**Location:** `MINDSET_module-main/GLORIA_db/v57/2019/SSP/`

**Created by:** `ParseCode/collapse_MRIO_SSP.py`

**Purpose:** Aggregate GLORIA's 164 countries to 8 SSP regions

---

#### 1. labor_data.pkl
**Format:** Pandas DataFrame (pickled)

**Dimensions:** 960 rows × 10 columns (8 countries × 120 products)

**Columns:**
- REG_imp: Region (e.g., EGY, MEX)
- PROD_COMM: Product code (1-120)
- vol_Fem_low: Female low-skill employment
- vol_Male_low: Male low-skill employment
- vol_Fem_high: Female high-skill employment
- vol_Male_high: Male high-skill employment
- ... (additional employment categories)

**Purpose:** Employment baseline data (how many people work in each sector-country)

**Used by:**
- `exog_vars_SSP.py` → loads as LABOR_BASE
- Employment calculations in `BATCH_EMPLOYMENT_ALL_STRATEGIES.py`

---

#### 2. IND_sparse.pkl
**Format:** Sparse matrix (pickled)

**Dimensions:** 960 × 960 (8 countries × 120 products)

**Purpose:** Industry-to-industry transaction matrix (who buys from whom)

**Used by:**
- `InputOutput_SSP.py` → builds Leontief inverse

---

#### 3. HH.pkl
**Format:** Pandas DataFrame (pickled)

**Purpose:** Household consumption by product-country

**Used by:**
- `InputOutput_SSP.py` → builds final demand vector (Y_BASE)

---

#### 4. GOV.pkl
**Format:** Pandas DataFrame (pickled)

**Purpose:** Government consumption by product-country

**Used by:**
- `InputOutput_SSP.py` → builds final demand vector (Y_BASE)

---

#### 5. FCF.pkl
**Format:** Pandas DataFrame (pickled)

**Purpose:** Fixed capital formation (investment) by product-country

**Used by:**
- `InputOutput_SSP.py` → builds final demand vector (Y_BASE)

---

#### 6. GFCF.pkl
**Format:** Pandas DataFrame (pickled)

**Purpose:** Gross fixed capital formation (detailed investment data)

**Used by:**
- `InputOutput_SSP.py` → builds final demand vector (Y_BASE)

---

#### 7. GLORIA_L_Base_2019.mat
**Format:** MATLAB .mat file

**Contents:** Leontief inverse matrix (L_BASE)

**Dimensions:** 960 × 960

**Purpose:** Contains all supply chain linkages. Core of Input-Output model.

**Formula:** L = (I - A)^(-1), where A is technical coefficients matrix

**Created by:** `InputOutput_SSP.py` (from IND_sparse and other matrices)

**Used by:**
- `InputOutput_SSP.py` → loads for output calculations

**Why .mat format:** MINDSET was originally MATLAB-based; uses scipy.io to read

---

#### 8. GLORIA_Y_Base_2019.mat
**Format:** MATLAB .mat file

**Contents:**
- y0: Total final demand baseline
- y_hh0: Household consumption component
- y_npish: Non-profit institutions component
- y_gov0: Government consumption component
- y_fcf0: Fixed capital formation component
- y_inv: Investment component

**Purpose:** Baseline final demand by product-country

**Created by:** `InputOutput_SSP.py` (from HH, GOV, FCF, etc.)

**Used by:**
- `InputOutput_SSP.py` → calculates baseline output (q_base = L × y0)

---

#### 9. GLORIA_G_Base_2019.mat
**Format:** MATLAB .mat file

**Contents:** G_BASE matrix (government spending matrix)

**Purpose:** Government consumption patterns

**Created by:** `InputOutput_SSP.py`

**Used by:**
- `InputOutput_SSP.py` → scenarios with government spending changes

---

### Additional SSP Files

**Similar structure for:**
- EXPORTS.pkl
- VA.pkl (value added)
- Q.pkl (production quantities)
- ... (various economic indicators)

All follow same pattern: 8 SSP regions × 120 products

---

## Scripts Created

### 1. collapse_MRIO_SSP.py
**Location:** `MINDSET_module-main/ParseCode/collapse_MRIO_SSP.py`

**Purpose:** One-time aggregation of GLORIA 164 countries → 8 SSP regions

**Status:** Already run (outputs exist in SSP folder)

**Input:** Original GLORIA data (164 countries)
**Output:** SSP aggregated data (8 regions)

**Method:** Aggregates by summing flows and employment across countries within regions

**Regions created:**
1. ROW (Rest of World - aggregates ~150 countries using China as representative)
2. BGR (Bulgaria)
3. BLZ (Belize)
4. EGY (Egypt)
5. LBY (Libya)
6. MAR (Morocco)
7. MEX (Mexico)
8. UGA (Uganda)

**Why needed:** Original GLORIA is too large and not aligned with study countries

**Re-run needed:** No (data already exists)

---

### 2. create_SSP_Y_BASE.py
**Location:** `MINDSET_module-main/Claude Code/temp/create_SSP_Y_BASE.py`

**Purpose:** Build .mat files (L_BASE, Y_BASE, G_BASE) for SSP data

**Status:** Already run (matrices exist in SSP folder)

**Input:** SSP .pkl files
**Output:** .mat files

**Method:**
1. Load SSP aggregated data
2. Calculate Leontief inverse
3. Build final demand vector
4. Save to MATLAB format

**Why needed:** MINDSET expects .mat files for I-O matrices

**Re-run needed:** No (matrices already exist)

---

### 3. InputOutput_SSP.py
**Location:** `MINDSET_module-main/SourceCode/InputOutput_SSP.py`

**Purpose:** Modified Input-Output module that loads from SSP subfolder

**Status:** Active (used by batch script)

**Based on:** Original `InputOutput.py`

**Key changes:**
- Line 197: G_BASE path → `SSP/GLORIA_G_Base_2019.mat`
- Line 232: L_BASE path → `SSP/GLORIA_L_Base_2019.mat`
- Line 259: Y_BASE path → `SSP/GLORIA_Y_Base_2019.mat`

**Why needed:** Ensures batch script loads SSP data, not original GLORIA data

**Used by:**
- `BATCH_EMPLOYMENT_ALL_STRATEGIES.py`
- `TEST_FINAL_CLEAN.py`

---

### 4. TEST_FINAL_CLEAN.py
**Location:** `MINDSET_module-main/Claude Code/temp/TEST_FINAL_CLEAN.py`

**Purpose:** Test script - processes one strategy to validate methodology

**Status:** Successfully tested

**Test case:** Strategy_1004_EGY

**Output:** Shows expected structure and validates:
- ✓ Employment calculation correct (20.93 jobs)
- ✓ ISIC aggregation working (20 sectors)
- ✓ Direct/indirect separation (74.6% / 25.4%)
- ✓ Share sum = 1.0
- ✓ Attribute merge working

**Why needed:** Validate methodology before running 469 strategies

**Re-run needed:** No (validation complete)

---

### 5. BATCH_EMPLOYMENT_ALL_STRATEGIES.py
**Location:** `MINDSET_module-main/Claude Code/temp/` → move to `Codes - SSP/`

**Purpose:** Production script - processes all 469 strategies

**Status:** Ready to run

**Runtime:** 30-60 minutes

**Input:**
- 469 strategy files
- ISIC crosswalk
- Strategy attributes
- SSP MRIO data

**Output:**
- `SSP - Results/employment_consolidated.csv`
- `SSP - Results/processing_errors.txt` (if errors occur)

**Features:**
- Progress tracking (prints every 10 strategies)
- Error logging (continues on failure)
- Validation checks (share sums, non-negative jobs)
- Summary statistics (by country, sector)

**Why needed:** Main production script for dissertation analysis

---

## Output Files

### 1. employment_consolidated.csv
**Location:** `MINDSET_module-main/SSP - Results/employment_consolidated.csv`

**Purpose:** Final dataset for dissertation analysis

**Dimensions:** ~9,380 rows × 10 columns

**Structure:**
```csv
country_name,country_ISO,strategy_id,strategy_name,sector_code,sector_name,direct_jobs,indirect_jobs,total_jobs,share_of_total_jobs
Egypt,EGY,Strategy_1004_EGY,Agricultural Infrastructure,A,Agriculture forestry and fishing,12.89,0.01,12.90,0.616
Egypt,EGY,Strategy_1004_EGY,Agricultural Infrastructure,B,Mining and quarrying,0.00,1.27,1.27,0.061
...
```

**Size:** ~2-3 MB

**Created by:** `BATCH_EMPLOYMENT_ALL_STRATEGIES.py`

**Status:** Ready for analysis (after running batch script)

**Quality checks:**
- All 469 strategies included
- All 20 ISIC sectors per strategy
- Shares sum to 1.0 per strategy
- No missing values in key columns

---

### 2. processing_errors.txt (if errors occur)
**Location:** `MINDSET_module-main/SSP - Results/processing_errors.txt`

**Purpose:** Log any strategies that failed processing

**Format:**
```
PROCESSING ERRORS
================================================================================

Strategy_XXXX_YYY: Error message here
Strategy_ZZZZ_AAA: Another error message
```

**Created by:** `BATCH_EMPLOYMENT_ALL_STRATEGIES.py`

**Status:** Only created if errors occur during processing

**Action if exists:** Review errors, investigate causes, potentially re-run failed strategies

---

## Documentation Files

### 1. WORKFLOW_DOCUMENTATION.md
**Location:** `MINDSET_module-main/Claude Code/temp/WORKFLOW_DOCUMENTATION.md`

**Purpose:** Complete methodology documentation

**Sections:**
- Research objective
- Methodology overview
- Workflow steps (detailed)
- Data sources
- Technical implementation
- Results and validation
- Output dataset

**Length:** ~600 lines

**Status:** Complete

---

### 2. FILE_INVENTORY.md (this file)
**Location:** `MINDSET_module-main/Claude Code/temp/FILE_INVENTORY.md`

**Purpose:** Catalog all files in the workflow

**Status:** Complete

---

### 3. SCRIPT_EXPLANATIONS.md
**Location:** `MINDSET_module-main/Claude Code/temp/SCRIPT_EXPLANATIONS.md`

**Purpose:** Explain each script's logic and purpose in plain language

**Status:** To be created next

---

### 4. README_BATCH_EMPLOYMENT.md
**Location:** `MINDSET_module-main/Claude Code/temp/README_BATCH_EMPLOYMENT.md`

**Purpose:** Quick start guide for running batch script

**Sections:**
- How to run
- Expected output
- Troubleshooting
- File requirements

**Status:** Complete

---

## File Dependencies

### Dependency Graph

```
Manual Files:
  ├─ Strategy Files (469) ─────┐
  ├─ GLORIA-Eora26 Crosswalk ──┼──┐
  ├─ ATTRIBUTE_STRATEGY.csv ───┼──┤
  └─ Variable_list_MINDSET ────┤  │
                                │  │
Generated Data (one-time):      │  │
  ├─ labor_data.pkl ────────────┤  │
  ├─ IND_sparse.pkl ────────────┤  │
  ├─ HH.pkl, GOV.pkl, etc. ─────┤  │
  ├─ L_BASE.mat ────────────────┤  │
  ├─ Y_BASE.mat ────────────────┤  │
  └─ G_BASE.mat ────────────────┤  │
                                │  │
Scripts:                        │  │
  ├─ InputOutput_SSP.py ────────┤  │
  ├─ exog_vars_SSP.py ──────────┤  │
  ├─ employment.py ─────────────┤  │
  ├─ scenario.py ───────────────┤  │
  ├─ investment.py ─────────────┤  │
  └─ BATCH_EMPLOYMENT... ───────┴──┤
                                   │
Output:                            │
  └─ employment_consolidated.csv ──┘
```

### Load Order

**1. Initialization:**
```
BATCH_EMPLOYMENT_ALL_STRATEGIES.py starts
  ↓
Loads GLORIA-Eora26 Crosswalk
  ↓
Loads ATTRIBUTE_STRATEGY.csv
  ↓
Loads MRIO data via exog_vars_SSP.py
  ├─ reads Variable_list_MINDSET_SSP.xlsx
  ├─ loads labor_data.pkl → LABOR_BASE
  └─ loads other SSP .pkl files
  ↓
Initializes InputOutput_SSP.py
  ├─ loads L_BASE.mat
  ├─ loads Y_BASE.mat
  ├─ loads G_BASE.mat
  └─ calculates q_base
  ↓
Initializes employment.py
  ├─ loads EMPL_COEF
  ├─ calculates empl_multipliers
  └─ ready for employment calculations
```

**2. For each strategy (469 iterations):**
```
Load Strategy_XXXX_YYY.xlsx via scenario.py
  ↓
Convert investment to demand via investment.py
  ↓
Calculate output changes via InputOutput_SSP.py
  ↓
Calculate employment via employment.py
  ↓
Aggregate to ISIC sectors (using crosswalk)
  ↓
Calculate shares
  ↓
Merge with ATTRIBUTE_STRATEGY.csv
  ↓
Store results
```

**3. Finalization:**
```
Consolidate all results
  ↓
Validate (share sums, non-negative, etc.)
  ↓
Export to employment_consolidated.csv
  ↓
Print summary statistics
```

---

## Storage Requirements

### Data Files
| Category | Size | Count | Total |
|----------|------|-------|-------|
| SSP .pkl files | ~5-20 MB each | ~15 | ~200 MB |
| SSP .mat files | ~10-30 MB each | 3 | ~60 MB |
| Strategy files | ~50 KB each | 469 | ~25 MB |
| Crosswalk | ~100 KB | 1 | 0.1 MB |
| Attributes | ~10 KB | 1 | 0.01 MB |
| **Subtotal** | | | **~285 MB** |

### Output Files
| File | Size |
|------|------|
| employment_consolidated.csv | ~2-3 MB |

### Scripts
| File | Size |
|------|------|
| Python scripts | ~1-2 KB each |
| **Total** | ~10 KB |

### Documentation
| File | Size |
|------|------|
| Markdown docs | ~50-100 KB each |
| **Total** | ~200 KB |

### Grand Total
**~290 MB** (data + output + scripts + documentation)

---

## File Locations Summary

### Absolute Paths (Data folder)
```
C:\Users\festeves\...\Data\
  ├─ GLORIA-Eora26 - Crosswalk.xlsx
  └─ ATTRIBUTE_STRATEGY.csv
```

### Relative to MINDSET_module-main
```
MINDSET_module-main/
├─ Codes - SSP/
│  └─ BATCH_EMPLOYMENT_ALL_STRATEGIES.py (production script)
│
├─ Claude Code/temp/
│  ├─ TEST_FINAL_CLEAN.py
│  ├─ README_BATCH_EMPLOYMENT.md
│  ├─ WORKFLOW_DOCUMENTATION.md
│  ├─ FILE_INVENTORY.md
│  └─ SCRIPT_EXPLANATIONS.md
│
├─ GLORIA_template/
│  ├─ Scenarios/
│  │  └─ Strategy_*.xlsx (469 files)
│  └─ Variable_list_MINDSET_SSP.xlsx
│
├─ GLORIA_db/v57/2019/SSP/
│  ├─ labor_data.pkl
│  ├─ IND_sparse.pkl
│  ├─ HH.pkl, GOV.pkl, FCF.pkl, etc.
│  ├─ GLORIA_L_Base_2019.mat
│  ├─ GLORIA_Y_Base_2019.mat
│  └─ GLORIA_G_Base_2019.mat
│
├─ SourceCode/
│  ├─ InputOutput_SSP.py (modified for SSP)
│  ├─ exog_vars_SSP.py
│  ├─ employment.py
│  ├─ scenario.py
│  ├─ investment.py
│  └─ utils.py
│
├─ ParseCode/
│  └─ collapse_MRIO_SSP.py (one-time use)
│
└─ SSP - Results/
   ├─ employment_consolidated.csv (final output)
   └─ processing_errors.txt (if errors)
```

---

## File Modification History

### Created During This Analysis
1. `InputOutput_SSP.py` - Modified version pointing to SSP folder
2. `TEST_FINAL_CLEAN.py` - Test script for validation
3. `BATCH_EMPLOYMENT_ALL_STRATEGIES.py` - Main production script
4. `WORKFLOW_DOCUMENTATION.md` - Methodology documentation
5. `FILE_INVENTORY.md` - This file
6. `README_BATCH_EMPLOYMENT.md` - Quick start guide

### Modified During This Analysis
1. `Variable_list_MINDSET_SSP.xlsx` - Updated paths to point to SSP subfolder

### Pre-existing (Unchanged)
1. All original MINDSET SourceCode files (except InputOutput_SSP.py)
2. All GLORIA data files
3. Strategy files (469)
4. Crosswalk file
5. Attributes file

---

## Backup Recommendations

### Critical Files to Backup
1. **SSP aggregated data** (~285 MB) - Time-consuming to regenerate
2. **Strategy files** (25 MB) - May be unique to research
3. **Output file** (3 MB) - Final results
4. **Scripts** (10 KB) - Replication code

### Can Be Regenerated
1. `.mat` files (if `.pkl` files exist)
2. Test outputs
3. Documentation (this file, etc.)

---

*Document Version: 1.0*
*Last Updated: March 22, 2026*
*Status: Complete*
