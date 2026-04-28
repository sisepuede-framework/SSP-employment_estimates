# MINDSET Employment Estimation - Execution Guide

**Purpose:** Step-by-step guide to run employment impact estimation
**Script:** `RunMINDSET_EmploymentOnly.py`
**Location:** `Claude Code/temp/`
**Date:** 2026-03-09

---

## 📋 OVERVIEW

This guide shows you how to execute the employment-only MINDSET workflow using the modified script that **clearly marks what to run and what to skip**.

---

## 🎯 WHAT THE SCRIPT DOES

### ✅ Modules It RUNS (5 total):
1. **exog_vars.py** → Load MRIO data (Leontief inverse, employment coefficients)
2. **scenario.py** → Load investment scenario file
3. **InputOutput.py** → Calculate output changes (dX = L × dY)
4. **employment.py** → Calculate employment changes (dE = e × dX)
5. **utils.py** → Data conversion utilities

### ❌ Modules It SKIPS (11 total):
1. ener_elas.py (energy substitution)
2. ener_balance.py (carbon tax calculations)
3. tax_rev.py (tax revenue)
4. BTA.py (border tax adjustments)
5. prod_cost.py (production cost shocks)
6. price.py (price effects)
7. household.py (household responses)
8. government.py (government spending)
9. trade.py (trade substitution)
10. investment.py (induced investment)
11. income.py (income feedback loop)

---

## 📂 BEFORE YOU START: File Requirements

### ✅ Required Files:

1. **Leontief Inverse Matrix**
   - Location: `GLORIA_db/[version]/GLORIA_L_Base_2019.mat`
   - OR: `GLORIA_db/synthetic/GLORIA_L_Base_2019.mat` (if using synthetic)
   - Content: (I - A)^(-1) matrix

2. **Employment Coefficients**
   - Location: `GLORIA_template/Employment/Empl_coefficient.csv`
   - Content: Jobs per $1M output by sector-region

3. **Region/Sector IDs**
   - Location: `GLORIA_db/[version]/parsed_db/cid.pkl`, `sid.pkl`
   - OR: `GLORIA_db/synthetic/parsed_db/cid.pkl`, `sid.pkl`

4. **Scenario File**
   - Location: `GLORIA_template/Scenarios/Infrastructure_Investment.xlsx`
   - Content: Your $100M investment allocation
   - **YOU NEED TO CREATE THIS** (see Section IV below)

---

## 🚀 EXECUTION STEPS

### STEP 1: Copy the Modified Script

```bash
# Copy the employment-only script to main directory
cp "Claude Code/temp/RunMINDSET_EmploymentOnly.py" .
```

**OR** just run it from the temp directory:
```bash
cd "Claude Code/temp"
python RunMINDSET_EmploymentOnly.py
```

---

### STEP 2: Configure the Scenario

Open `RunMINDSET_EmploymentOnly.py` and find line ~55:

```python
if SPYDER:
    # CONFIGURE YOUR SCENARIO HERE:
    scenario_name = "Infrastructure_Investment"  # ← CHANGE THIS TO YOUR SCENARIO NAME
```

**Options:**
- Keep as `"Infrastructure_Investment"` (default)
- Change to your own scenario name (e.g., `"Synthetic_Infrastructure"`)

---

### STEP 3: Verify Data Files Exist

Before running, check that you have:

```bash
# Check Leontief inverse
ls GLORIA_db/synthetic/GLORIA_L_Base_2019.mat

# Check employment coefficients
ls GLORIA_template/Employment/Empl_coefficient.csv

# Check scenario file
ls GLORIA_template/Scenarios/Infrastructure_Investment.xlsx
```

If files are missing, you need to create synthetic data first (see Section V).

---

### STEP 4: Run the Script

**Option A: From IDE (Spyder, VS Code, etc.)**
```python
# Just run the script directly in your IDE
# Make sure SPYDER = True in the script
```

**Option B: From Command Line**
```bash
python RunMINDSET_EmploymentOnly.py
```

**Option C: With Custom Scenario Name**
```bash
# Set SPYDER = False in script first
python RunMINDSET_EmploymentOnly.py "My_Custom_Scenario"
```

---

### STEP 5: Monitor the Output

You should see progress messages like:

```
================================================================================
MINDSET EMPLOYMENT-ONLY ESTIMATION
================================================================================

Scenario file: ...\GLORIA_template\Scenarios\Infrastructure_Investment.xlsx

--------------------------------------------------------------------------------
STEP 1: Loading MRIO Data
--------------------------------------------------------------------------------
✓ Loaded Leontief inverse: (30, 30)
✓ Loaded employment coefficients
✓ Loaded 3 countries/regions
✓ Loaded 10 sectors
Time: 2.3 seconds

--------------------------------------------------------------------------------
STEP 2: Loading Investment Scenario
--------------------------------------------------------------------------------
✓ Loaded exogenous final demand shock: $100,000,000
✓ Investment allocated across 4 sector-region pairs
Time: 0.5 seconds

--------------------------------------------------------------------------------
STEP 3: Calculating Output Changes
--------------------------------------------------------------------------------
✓ Initialized IO model
✓ Converted final demand shock to vector (size: 30)
✓ Total shock amount: $100,000,000
✓ Calculated output changes: dX = L × dY
✓ Total output change: $175,000,000
✓ Output multiplier: 1.75x
Time: 1.2 seconds

--------------------------------------------------------------------------------
STEP 4: Calculating Employment Changes
--------------------------------------------------------------------------------
✓ Loaded employment coefficients
✓ Calculated employment changes: dE = e × dX
✓ Total jobs created: 1,250
✓ Employment multiplier: 12.50 jobs per $1M
Time: 0.8 seconds

--------------------------------------------------------------------------------
STEP 5: Saving Results
--------------------------------------------------------------------------------
✓ Formatted output change results
✓ Formatted employment change results
✓ Created summary statistics

SUMMARY:
  Total Investment: $100,000,000
  Total Jobs Created: 1,250
  Employment Multiplier: 12.50 jobs per $1M

✓ Results saved to: GLORIA_results\Results_Infrastructure_Investment_EmploymentOnly.xlsx
Time: 1.5 seconds

================================================================================
EMPLOYMENT ESTIMATION COMPLETE
================================================================================

Total Runtime: 6.3 seconds

Results saved to:
  GLORIA_results\Results_Infrastructure_Investment_EmploymentOnly.xlsx

Sheets created:
  1. Summary - Key metrics and multipliers
  2. Employment_by_Region - Jobs created by region
  3. Employment_by_Sector - Jobs created by sector
  4. Employment_Details - Full sector-region breakdown
  5. Output_Details - Output changes for validation

Employment Impact:
  Investment: $100,000,000
  Jobs Created: 1,250
  Multiplier: 12.50 jobs/$1M
```

---

### STEP 6: Check the Results

Open the Excel file:
```
GLORIA_results/Results_Infrastructure_Investment_EmploymentOnly.xlsx
```

**5 Sheets Created:**

1. **Summary** - Key metrics
   - Total investment
   - Total jobs created
   - Employment multiplier
   - Output multiplier

2. **Employment_by_Region** - Jobs by region
   - Shows where jobs are created
   - Includes spillover effects

3. **Employment_by_Sector** - Jobs by sector
   - Shows which sectors benefit
   - Includes supply chain effects

4. **Employment_Details** - Full breakdown
   - 30 rows (or n × m for your data)
   - Each sector-region combination
   - dempl_total column shows jobs

5. **Output_Details** - Output changes
   - For validation purposes
   - dq_total column shows output change
   - q_base column shows baseline

---

## 📊 INTERPRETING THE RESULTS

### Expected Ranges (Validation):

**Employment Multiplier:**
- Typical range: 5-20 jobs per $1M
- Infrastructure: usually 8-15
- If outside range: check employment coefficients

**Output Multiplier:**
- Typical range: 1.5-3.0
- If below 1.5: check Leontief inverse
- If above 3.0: may indicate data issues

**Regional Distribution:**
- Target region: usually 70-90% of jobs
- Spillover regions: 10-30% of jobs
- Reflects inter-regional supply chains

**Sectoral Distribution:**
- Construction: typically largest (if infrastructure)
- Manufacturing: medium (materials)
- Services: medium to small (support)
- Should match investment allocation roughly

---

## ⚠️ COMMON ISSUES & SOLUTIONS

### Issue 1: "FileNotFoundError: GLORIA_L_Base_2019.mat"

**Problem:** Leontief inverse file not found
**Solution:** Create synthetic data first (see Section V)

### Issue 2: "No exogenous final demand found"

**Problem:** Scenario file missing or incorrect format
**Solution:** Check scenario Excel file has correct sheets and columns

### Issue 3: "Employment coefficients not loaded"

**Problem:** Empl_coefficient.csv missing or wrong format
**Solution:** Create synthetic employment coefficients (see Section V)

### Issue 4: "Negative employment changes"

**Problem:** Data or calculation error
**Solution:** Check employment coefficients are positive, verify output changes

### Issue 5: "Employment multiplier seems too high/low"

**Problem:** May indicate data issues
**Solution:**
- Check employment coefficient values (typical: 0.005-0.020)
- Verify Leontief inverse calculated correctly
- Compare to literature values

---

## 📝 WHAT THE SCRIPT EXPLICITLY MARKS

Throughout `RunMINDSET_EmploymentOnly.py`, you'll see clear annotations:

### ✓ Code That RUNS:
```python
# ✓ REQUIRED: Extract exogenous final demand shock
dy_exog_fd = MRIO_df_to_vec(...)

# ✓ REQUIRED: Calculate output changes using Leontief model
dq_exog_fd = IO_model.calc_dq_exog(dy_exog_fd)

# ✓ REQUIRED: Calculate employment changes
dempl_exog_fd = Empl_model.calc_dempl([dq_exog_fd])[0]
```

### ✗ Code That's SKIPPED:
```python
# ✗ SKIP: Energy elasticity calculations
# Ener_model = ener_elas(MRIO_BASE)
# tech_coef_ener = Ener_model.calc_tech_coef_ener()
# dL_ener = IO_model.build_dL_ener(...)

# ✗ SKIP: Household demand response
# HH_model = hh(MRIO_BASE)
# HH_price_eff, HH_inc_eff = HH_model.calc_hh_demand_change(...)

# ✗ SKIP: Trade substitution
# Trade_model = trade(MRIO_BASE)
# ind_trade = Trade_model.calc_IO_coef(ind_ener_glo, dp_pre_trade)
```

This makes it crystal clear what's running and what's not!

---

## 🔧 SECTION IV: Creating the Scenario File

If you don't have `Infrastructure_Investment.xlsx`, create it:

### Minimum Required Format:

**File:** `GLORIA_template/Scenarios/Infrastructure_Investment.xlsx`

**Sheet 1: "Scenario_Info"**
| Parameter | Value |
|-----------|-------|
| Scenario_Name | Infrastructure Investment |
| Total_Amount | 100000000 |
| Description | $100M infrastructure investment in Region A |

**Sheet 2: "Final_Demand_Shock"** (most important!)
| REG_exp | TRAD_COMM | PROD_COMM | dy |
|---------|-----------|-----------|------------|
| RegionA | 4 | FD_4 | 40000000 |
| RegionA | 3 | FD_4 | 30000000 |
| RegionA | 8 | FD_4 | 20000000 |
| RegionA | 5 | FD_4 | 10000000 |

**Where:**
- `REG_exp` = target region (must match cid.pkl)
- `TRAD_COMM` = sector ID (4=Construction, 3=Manufacturing, etc.)
- `PROD_COMM` = final demand category ("FD_4" = investment)
- `dy` = dollar amount of shock

**Other sheets (can be blank for employment-only):**
- Carbon_Tax (skip - set all to zero or leave blank)
- Revenue_Recycling (skip - leave blank)
- BTA (skip - leave blank)

---

## 🔧 SECTION V: Creating Synthetic Data (If Needed)

If you don't have GLORIA data, you need synthetic versions.

**We'll create this in the next step**, but here's what's needed:

### Files to Generate:

1. **Leontief Inverse (L matrix)**
   ```
   GLORIA_db/synthetic/GLORIA_L_Base_2019.mat
   Dimensions: 30×30 (for 3 regions × 10 sectors)
   ```

2. **Employment Coefficients**
   ```
   GLORIA_template/Employment/Empl_coefficient_synthetic.csv
   Dimensions: 10 sectors × 3 regions
   Values: 0.005-0.020 (jobs per $1M output)
   ```

3. **Region/Sector IDs**
   ```
   GLORIA_db/synthetic/parsed_db/cid.pkl
   GLORIA_db/synthetic/parsed_db/sid.pkl
   ```

**Next:** I'll create a `create_synthetic_data.py` script to generate all these files.

---

## 📊 COMPARING TO ORIGINAL RunMINDSET.py

### Original Script (~800 lines):
- Runs all 16 modules
- Includes energy, trade, household, tax modules
- Has iterative income-employment loop
- Takes hours with full GLORIA data
- Complex with many moving parts

### Employment-Only Script (~450 lines):
- Runs only 5 modules
- Skips 11 unnecessary modules
- No iterations (single pass)
- Takes minutes with synthetic data
- Focused and straightforward

### Line-by-Line Comparison:

| Section | Original | Employment-Only | Notes |
|---------|----------|-----------------|-------|
| Imports | Lines 28-58 | Lines 23-45 | 11 fewer imports |
| Energy Module | Lines 154-223 | ✗ SKIPPED | Commented out |
| Tax Revenue | Lines 229-260 | ✗ SKIPPED | Commented out |
| Prod Cost | Lines 266-281 | ✗ SKIPPED | Commented out |
| IO Calculation | Lines 294-330 | ✓ SIMPLIFIED | Key calculation kept |
| Price Module | Lines 313-328 | ✗ SKIPPED | Not needed |
| Household | Lines 342-356 | ✗ SKIPPED | Not needed |
| Government | Lines 365-381 | ✗ SKIPPED | Not needed |
| Trade | Lines 384-392 | ✗ SKIPPED | Not needed |
| Investment | Lines 456-494 | ✗ SKIPPED | Not needed |
| Employment | Lines 498-520 | ✓ KEPT | Core calculation |
| Income Loop | Lines 537-689 | ✗ SKIPPED | No iterations |
| GDP | Lines 692-705 | ✗ SKIPPED | Not needed |
| Results | Lines 707-789 | ✓ SIMPLIFIED | Key results kept |

**Result:** ~50% of code removed, workflow clarified!

---

## ✅ CHECKLIST FOR EXECUTION

Before running:
- [ ] `RunMINDSET_EmploymentOnly.py` copied or accessible
- [ ] Scenario name configured (line ~55)
- [ ] MRIO data files exist (Leontief, employment coefs)
- [ ] Scenario Excel file created
- [ ] Python environment has numpy, pandas, openpyxl

During run:
- [ ] Monitor console output for errors
- [ ] Check each step completes successfully
- [ ] Note the employment multiplier value

After run:
- [ ] Open results Excel file
- [ ] Verify Summary sheet has reasonable values
- [ ] Check Employment_by_Region makes sense
- [ ] Check Employment_by_Sector matches investment
- [ ] Validate multiplier against literature (5-20 jobs/$1M)

---

## 📚 NEXT STEPS

1. **Create synthetic data** (if needed)
   - Run `create_synthetic_data.py` (we'll create this next)

2. **Run employment estimation**
   - Execute `RunMINDSET_EmploymentOnly.py`

3. **Analyze results**
   - Open Excel file
   - Calculate summaries
   - Compare to literature

4. **Document for supervisor**
   - Use presentation we created
   - Show results
   - Explain methodology

---

**Questions?** All supporting documentation is in `Claude Code/temp/`

**Ready to execute?** Just run: `python RunMINDSET_EmploymentOnly.py`
