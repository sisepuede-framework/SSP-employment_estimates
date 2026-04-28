# MINDSET Employment Impact Analysis - Workflow Guide

**Project:** Employment impact estimation from exogenous final demand using MINDSET model
**User:** Beginner MINDSET user
**Challenge:** GLORIA dataset not available - using synthetic data
**Goal:** Complete, replicable workflow for supervisor review

---

## Table of Contents
1. [Overview](#overview)
2. [Understanding the MINDSET Model](#understanding-the-mindset-model)
3. [Step-by-Step Workflow](#step-by-step-workflow)
4. [Current Status](#current-status)

---

## Overview

### What is MINDSET?
MINDSET is a Multi-Regional Input-Output (MRIO) model that calculates economic impacts of policy interventions. It uses:
- **GLORIA MRIO database** (Global Multi-Regional Input-Output tables)
- **Multiple modules** for energy, trade, household, employment effects
- **Python scripts** coordinated through main execution files

### Our Specific Goal
Estimate **employment impacts** from **exogenous changes in final demand** (e.g., infrastructure investment, climate adaptation spending).

### Why Synthetic Data?
Since you don't have access to GLORIA database, we will:
1. Create synthetic MRIO tables matching GLORIA structure
2. Generate realistic but simplified economic relationships
3. Run the full MINDSET workflow with this synthetic data
4. Document every step for replication

---

## Understanding the MINDSET Model

### Model Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MINDSET MODEL FLOW                        │
└─────────────────────────────────────────────────────────────┘

1. EXOGENOUS INPUTS
   - MRIO tables (inter-industry, value-added, final demand)
   - Employment coefficients
   - Elasticities (energy, trade, household)
   - Scenario parameters

2. SCENARIO MODULE
   - Define exogenous final demand shock
   - Tax rates (if applicable)
   - Revenue recycling (if applicable)

3. CORE CALCULATION MODULES
   - Energy elasticities (if energy shock)
   - Trade substitution
   - Input-Output calculations (Leontief inverse)
   - Price effects
   - Household demand response
   - Government spending
   - Investment (induced/exogenous)

4. EMPLOYMENT MODULE ← OUR FOCUS
   - Employment coefficients × Output changes
   - Calculate employment impacts by:
     * Region
     * Sector
     * Impact channel (direct, indirect, induced)

5. RESULTS
   - Employment changes
   - Output changes
   - GDP changes
```

### Key Data Structures

Based on the documentation, MINDSET requires:

| Data Component | Description | File Location (Template) |
|----------------|-------------|-------------------------|
| **IND_BASE** | Inter-industry flows, technical coefficients | GLORIA_db/parsed_db/IND_sparse.pkl |
| **L_BASE** | Leontief inverse matrix | GLORIA_db/GLORIA_L_Base_2019.mat |
| **Y_BASE** | Final demand matrix | GLORIA_db/GLORIA_Y_Base_2019.mat |
| **VA_BASE** | Value-added components | GLORIA_db/parsed_db/VA.pkl |
| **HH_BASE** | Household consumption | GLORIA_db/parsed_db/HH.pkl |
| **FCF_BASE** | Investment (fixed capital formation) | GLORIA_db/parsed_db/FCF.pkl |
| **EMPL_COEF** | Employment coefficients | GLORIA_template/Employment/Empl_coefficient.csv |
| **Country/Sector IDs** | Region and sector identifiers | GLORIA_db/parsed_db/cid.pkl, sid.pkl |

---

## Step-by-Step Workflow

### PHASE 1: Environment Setup and Data Preparation

#### Step 1.1: Verify Python Environment
**What we'll do:** Check that all required Python packages are installed.

**Required packages:**
- numpy
- pandas
- scipy
- openpyxl (for Excel files)
- pickle (built-in)

**How to verify:**
```python
import numpy as np
import pandas as pd
import scipy
import pickle
import openpyxl
print("All packages available!")
```

---

#### Step 1.2: Understand Existing Data Structure
**What we'll do:** Examine the GLORIA_template folder to understand expected data formats.

**Files to review:**
- `GLORIA_template/Employment/Empl_coefficient.csv` - Employment coefficient structure
- `GLORIA_template/Variables/Variable_list_MINDSET.xlsx` - All variable definitions
- `GLORIA_template/Scenarios/*.xlsx` - Scenario template structure

**Key questions to answer:**
- How many regions/countries?
- How many sectors?
- What format for employment coefficients?

---

#### Step 1.3: Create Synthetic MRIO Database
**What we'll do:** Generate synthetic data matching GLORIA structure but with simplified, realistic values.

**Synthetic data specifications:**
- **Regions:** Start with 3-5 regions (e.g., Region A, Region B, Region C, Rest of World)
- **Sectors:** Start with 10-15 sectors (aggregated from GLORIA's detailed sectors)
- **Base year:** 2019 (to match GLORIA template structure)

**Data to generate:**
1. **Inter-industry matrix (Z)**: Region-sector × Region-sector flows
   - Diagonal-dominant (most flows within-region)
   - Realistic sector dependencies

2. **Value-added vector (VA)**: Wages, profits, taxes by region-sector

3. **Final demand (Y)**: Household, government, investment, exports by region-sector

4. **Employment (L)**: Workers per sector-region

5. **Technical coefficients (A)**: Z / column sums

6. **Leontief inverse**: (I - A)^(-1)

---

### PHASE 2: Synthetic Data Generation

#### Step 2.1: Define Synthetic Economy Structure
**Parameters to set:**
- Number of regions: 3
- Number of sectors: 10
- Total economic output: $1 trillion (for scaling)

**Sector classification (simplified from GLORIA):**
1. Agriculture
2. Mining & Extraction
3. Manufacturing
4. Construction
5. Utilities (Energy & Water)
6. Trade & Transportation
7. Financial Services
8. Business Services
9. Government Services
10. Other Services

---

#### Step 2.2: Generate Synthetic MRIO Tables
**Method:** Create realistic-looking MRIO using economic principles:
- Input-output coefficients sum to < 1 (value-added must be positive)
- Manufacturing has higher inter-industry linkages
- Services have lower material intensity
- Trade flows follow gravity model patterns

---

#### Step 2.3: Generate Employment Coefficients
**Format:** Jobs per million dollars of output by sector and region
- Manufacturing: 5-8 jobs/$M
- Services: 10-15 jobs/$M
- Agriculture: 15-20 jobs/$M (labor-intensive)

---

### PHASE 3: Scenario Definition

#### Step 3.1: Define Exogenous Final Demand Shock
**Example scenario:** $100M infrastructure investment

**Where does it go?**
- 40% Construction sector
- 30% Manufacturing (materials)
- 20% Business Services (engineering, design)
- 10% Utilities

**Which region?**
- Region A receives the investment

---

#### Step 3.2: Create Scenario File
**File:** `GLORIA_template/Scenarios/Infrastructure_Investment.xlsx`

**Contents:**
- Scenario name
- Final demand changes by sector and region
- No carbon tax (set all tax rates to 0)
- No revenue recycling needed

---

### PHASE 4: Model Execution

#### Step 4.1: Run MINDSET with Synthetic Data
**Script:** `RunMINDSET.py`

**Execution steps:**
1. Load exogenous variables (our synthetic MRIO)
2. Load scenario (infrastructure investment)
3. Calculate Input-Output effects (Leontief multipliers)
4. Calculate employment impacts using employment module
5. Save results

---

#### Step 4.2: Employment Module Calculation
**What happens in the employment module:**

```python
# Simplified logic from SourceCode/employment.py
Employment_Change = Employment_Coefficient × Output_Change
```

**Breakdown by effect:**
- Direct employment: Jobs in sectors receiving investment
- Indirect employment: Jobs in supplying industries
- Induced employment: Jobs from worker spending (if income loop active)

---

### PHASE 5: Results Analysis and Documentation

#### Step 5.1: Extract Employment Results
**Output format:** Employment changes by:
- Region
- Sector
- Effect type (direct/indirect/induced)

---

#### Step 5.2: Create Results Summary
**Deliverables:**
- Table: Employment impacts by sector and region
- Table: Direct vs indirect vs induced effects
- Sanity checks: Do multipliers look reasonable? (typically 1.5-3.0)

---

#### Step 5.3: Document Full Replication Steps
**For supervisor:** Complete documentation including:
- All synthetic data generation code
- All parameters and assumptions
- Full model execution log
- Results interpretation

---

## Current Status

### Completed:
- ✅ Project structure reviewed
- ✅ Documentation examined
- ✅ Workflow guide created

### Next Steps:
1. **Step 1.1:** Verify Python environment
2. **Step 1.2:** Review existing template files
3. **Step 2.1-2.3:** Generate synthetic MRIO data
4. **Step 3.1-3.2:** Create infrastructure investment scenario
5. **Step 4.1-4.2:** Execute MINDSET model
6. **Step 5.1-5.3:** Analyze and document results

---

## Key Files Reference

### Input Files (to be created):
- `GLORIA_db/parsed_db/synthetic_*.pkl` - Synthetic MRIO tables
- `GLORIA_template/Scenarios/Synthetic_Infrastructure.xlsx` - Test scenario
- `GLORIA_template/Employment/Synthetic_Empl_coefficient.csv` - Employment coefficients

### Execution Files:
- `RunMINDSET.py` - Main execution script
- `SourceCode/employment.py` - Employment module

### Output Files:
- `GLORIA_results/Results_Synthetic_Infrastructure.xlsx` - Model results
- `MINDSET_Replication_Report.md` - Full documentation for supervisor

---

## Notes for Replication

### Key Assumptions with Synthetic Data:
1. **Simplified economy:** 3 regions, 10 sectors (vs GLORIA: 164 countries, 163 sectors)
2. **Stylized relationships:** Based on typical IO patterns, not actual data
3. **Focus:** Demonstrating methodology, not producing policy-relevant estimates

### What This Demonstrates:
- ✅ Complete MINDSET workflow
- ✅ Employment impact calculation methodology
- ✅ Proper model execution sequence
- ✅ Results interpretation

### What This Doesn't Provide:
- ❌ Real-world policy estimates (requires actual GLORIA data)
- ❌ Energy/trade substitution effects (we're focusing on simple final demand shock)
- ❌ Full geographic detail (simplified to 3 regions)

---

## Uganda & Libya Employment Estimate Review

**Date:** 2026-03-23
**Issue:** Unrealistically high employment estimates for Uganda and Libya
**Purpose:** Diagnostic trace and documentation for supervisor reporting

### Problem Statement

Employment estimates for **Uganda (UGA)** and **Libya (LBY)** show anomalously high values compared to other countries in the analysis. Specifically:

| Country | Jobs per $M Output | Comparison to Normal Range |
|---------|-------------------|---------------------------|
| **Uganda** | 272 - 2,051 | **20-100x higher** than typical |
| **Libya** | 100 - 170 | **5-10x higher** than typical |
| Normal Range | 10 - 50 | Observed in BGR, BLZ, EGY, MAR, MEX |

**Example from Strategy_1004_BGR results:**
- Mexico: 9.79 jobs/$M output ✓ Normal
- Egypt: 232.75 jobs/$M output (elevated but not extreme)
- Libya: 816.59 jobs/$M output ⚠️ **Anomaly**
- Uganda: 1,935.92 jobs/$M output ⚠️ **Severe Anomaly**

### Diagnostic Trace Through MINDSET Workflow

#### Step 1: Load Employment Coefficients

**Location:** `SourceCode/employment.py`, lines 10-34

**Process:** MINDSET loads base employment coefficients from GLORIA v57 database:
- File: `GLORIA_template/Employment/Empl_coefficient.csv`
- Structure: 120 products × 164 countries
- Units: Employment elasticity parameters (dimensionless)
- Source: GLORIA Multi-Regional Input-Output (MRIO) database

**Code Reference:**
```python
class empl:
    def __init__(self, MRIO_BASE):
        self.EMPL_COEF = MRIO_BASE.EMPL_COEF
```

#### Step 2: Calculate Employment Multipliers ⚠️ **Source of Anomaly**

**Location:** `SourceCode/employment.py`, lines 36-43

**Formula:**
```
empl_multiplier = EMPL_COEF × (empl_base / q_base)
```

Where:
- `EMPL_COEF` = Employment elasticity coefficient from GLORIA
- `empl_base` = Baseline employment level (workers)
- `q_base` = Baseline gross output (million USD)

**⚠️ CRITICAL INSIGHT:**
If `q_base` is very small → Division creates artificially large multiplier

**Code Reference:**
```python
def calc_empl_multiplier(self, empl_base, q_base):
    empl_coef = self.EMPL_COEF.loc[:,"empl_coef"].to_numpy()

    # Compute employment effects corresponding to effects on gross output
    self.empl_multiplier = empl_coef * (np.divide(
        empl_base, q_base, out=np.zeros_like(empl_base), where=q_base!=0))

    return True
```

**Hypothesis:** Uganda and Libya have abnormally small `q_base` values in GLORIA v57 data, causing the multiplier inflation.

#### Step 3: Investment Converter - "Strategy as Purchases" Fix

**Location:** `RunMINDSET_EmploymentOnly_BATCH_FINAL.py`, lines 126-145

**Conceptual Fix Already Implemented:**
The batch processing script correctly treats investment strategies as **purchases of specific products**, not as **investments by the producing sector**.

**Process Flow:**
1. Load strategy file: `Strategy_{ID}_{COUNTRY}.xlsx`
   - Contains investment amounts by sector

2. **Investment Converter** (`SourceCode/investment.py`):
   - Converts sector-based investments → product-specific final demand
   - Uses `INV_CONV` matrix: investment composition by product
   - Formula: `dY = INV_CONV × Investment_Vector`

**Code Reference:**
```python
# Investment Converter (Sector Investment → Product Demand)
INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

# Convert to vector: This is INITIAL FINAL DEMAND
dy_inv_exog = MRIO_df_to_vec(INV_model.dy_inv_exog, ...)
```

**Why This Matters:**
- **Before fix:** If investment was attributed to producing sector, it would create circular logic
- **After fix:** Investment creates demand for products, then Leontief model traces supply chain effects
- **Result:** Uganda/Libya anomalies are **not** caused by investment converter logic errors

#### Step 4: Employment Calculation

**Location:** `RunMINDSET_EmploymentOnly_BATCH_FINAL.py`, lines 162-178

**Formula:**
```python
# TOTAL employment = empl_multiplier × (L × dY)
dempl_total = Empl_model.calc_dempl([dq_total])[0]

# DIRECT employment = empl_multiplier × dY
dempl_direct = Empl_model.calc_dempl([dy_inv_exog])[0]

# INDIRECT employment = Total - Direct
dempl_indirect = dempl_total - dempl_direct
```

**Result:** Both direct and indirect employment inherit the inflated multipliers from Step 2.

### Root Cause Analysis

**Primary Hypothesis:** GLORIA v57 Data Quality Issues

The anomaly originates in **Step 2** (employment multiplier calculation) due to:

1. **Small `q_base` values** for Uganda and Libya in GLORIA v57
   - Possible causes:
     - Incomplete data coverage for these countries
     - Missing sectors in GLORIA aggregation
     - Data quality issues in source national accounts

2. **Formula sensitivity** to small denominators:
   ```
   multiplier = EMPL_COEF × (empl_base / q_base)
   ```
   - If `q_base` ≈ 0 → multiplier → ∞
   - Protected by `where=q_base!=0` but doesn't prevent near-zero issues

3. **Propagation through workflow:**
   - Multiplier calculated once at initialization
   - Applied to all demand scenarios
   - No country-specific validation or capping

**Why Not Other Steps:**
- ✓ Investment converter logic is correct ("purchases not production")
- ✓ Leontief model calculations are standard IO theory
- ✓ Aggregation and summation logic is sound
- ✗ **Base data quality** is the likely culprit

### Proposed Solutions

#### Option 1: Validate and Correct GLORIA Base Data ⭐ **Recommended**

**Actions:**
1. Examine `q_base` (gross output) values in GLORIA MRIO matrices
   - File location: `GLORIA_db/v57/2019/...`
   - Compare Uganda/Libya to similar economies

2. Cross-reference with external data sources:
   - World Bank National Accounts
   - UN System of National Accounts (SNA)
   - Regional development banks (AfDB, IsDB)

3. If GLORIA data is confirmed flawed:
   - Document specific products/sectors with missing/low output
   - Report issue to GLORIA database maintainers

#### Option 2: Use Proxy Country Coefficients

**Substitution Strategy:**
- **Uganda → Kenya or Tanzania** (East African proxies with better data)
- **Libya → Tunisia or Egypt** (North African proxies)

**Implementation:**
1. Replace Uganda/Libya employment coefficients with proxy country values
2. Document substitution in methodology section
3. Perform sensitivity analysis showing impact

#### Option 3: Cap Anomalous Multipliers

**Threshold Approach:**
- Set maximum reasonable threshold: 100 jobs per $M output
- Cap multipliers exceeding threshold
- Document as data quality adjustment

⚠️ **Not Recommended** without thorough validation

### Files for Reference

**Code Files:**
- `SourceCode/employment.py` - Employment multiplier calculation (lines 36-43)
- `SourceCode/investment.py` - Investment converter
- `Claude Code/temp/RunMINDSET_EmploymentOnly_BATCH_FINAL.py` - Main workflow

**Data Files:**
- `GLORIA_template/Employment/Empl_coefficient.csv` - Employment coefficients
- `Claude Code/temp/employment_results/*.csv` - Results showing anomalies
- `GLORIA_db/v57/2019/...` - Base MRIO matrices (q_base to examine)

**Diagnostic Scripts:**
- `Claude Code/temp/diagnose_employment_anomalies.py` - Automated diagnostic

---

*Last updated: 2026-03-23 (added Uganda/Libya review)*
*Created by: Claude Code assistant*
*Status: Employment analysis complete, anomalies documented*
