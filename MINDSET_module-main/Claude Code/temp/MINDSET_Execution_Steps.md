# MINDSET Model - Specific Execution Steps
## Script-by-Script Guide for Employment Impact Analysis

**Purpose:** Provide exact file paths and execution order for running MINDSET employment analysis
**User Level:** Beginner
**Data:** Synthetic (GLORIA not available)

---

## Quick Reference: Key Scripts in Execution Order

| Step | Script Path | Purpose | Inspect Before Running |
|------|-------------|---------|----------------------|
| 1 | `SourceCode/exog_vars.py` | Load all exogenous data | Data structure |
| 2 | `SourceCode/scenario.py` | Define shock scenario | Scenario parameters |
| 3 | `SourceCode/InputOutput.py` | Calculate IO multipliers | Leontief matrix |
| 4 | `SourceCode/employment.py` | Calculate employment impacts | Employment coefficients |
| 5 | `SourceCode/results.py` | Format and save results | Output structure |

**Main coordinator:** `RunMINDSET.py` (calls all modules in sequence)

---

## STEP 1: Understand Input Data Structure

### File to Inspect: `SourceCode/exog_vars.py`
**Location:** `.\SourceCode\exog_vars.py`
**Lines to read:** 1-150 (class definition and __init__ method)

**What this file does:**
- Loads all exogenous variables from GLORIA_db and GLORIA_template folders
- Creates data structures used throughout MINDSET
- Returns MRIO_BASE object containing all economic data

**Key data loaded:**
```python
# From exog_vars.py
self.IND_BASE  # Inter-industry flows
self.L_BASE    # Leontief inverse
self.Y_BASE    # Final demand
self.VA_BASE   # Value-added
self.HH_BASE   # Household consumption
self.FCF_BASE  # Investment
self.EMPL_COEF # Employment coefficients ← KEY FOR EMPLOYMENT ANALYSIS
self.COU_ID    # Country IDs
self.SEC_ID    # Sector IDs
```

**What YOU need to inspect:**
1. Open `SourceCode/exog_vars.py`
2. Find the `__init__` method (around line 20)
3. Look for where it loads `EMPL_COEF` (employment coefficients)
4. Note the expected file path: `GLORIA_template/Employment/Empl_coefficient.csv`

**Action:** Let's read this file together:

---

## STEP 2: Examine Employment Coefficient Structure

### File to Inspect: `GLORIA_template/Employment/Empl_coefficient.csv`
**Location:** `.\GLORIA_template\Employment\Empl_coefficient.csv`

**What YOU need to check:**
1. Open the CSV file in Excel or text editor
2. Identify column structure:
   - Country/Region identifiers
   - Sector identifiers
   - Employment coefficient values (jobs per $ of output)
3. Note dimensions: How many countries? How many sectors?
4. Check if values are realistic (typically 0.001 to 0.02 = 1-20 jobs per $1M output)

**This tells us:** The format we need for synthetic employment coefficients

---

## STEP 3: Examine Existing Scenario Structure

### File to Inspect: `GLORIA_template/Scenarios/*.xlsx`
**Location:** `.\GLORIA_template\Scenarios\`
**Example file:** Check any .xlsx file in this folder

**What YOU need to check:**
1. List all scenario files: `dir GLORIA_template\Scenarios\*.xlsx`
2. Open one scenario file (e.g., the one currently in RunMINDSET.py line 101)
3. Identify structure:
   - Sheet names
   - How final demand shocks are specified
   - How countries/sectors are identified
   - Tax rates (we'll set to zero)
   - Revenue recycling (we'll set to zero)

**This tells us:** The format we need for our synthetic infrastructure investment scenario

---

## STEP 4: Examine Main Execution Script

### File to Inspect: `RunMINDSET.py`
**Location:** `.\RunMINDSET.py`
**Lines to read:**
- Lines 1-125: Setup and argument parsing
- Lines 127-140: Load exogenous variables
- Lines 186-250: Energy elasticity module (we'll skip this)
- Lines 300-400: Input-Output calculations (KEY)
- Lines 450-500: Employment module (KEY)
- Lines 550-600: Results saving (KEY)

**Execution flow in RunMINDSET.py:**

```python
# Simplified flow (actual file is ~800 lines)

# 1. Load data
MRIO_BASE = exog_vars()  # Line ~129

# 2. Load scenario
Scenario = scenario(MRIO_BASE, scenario_path, Log)  # Line ~145

# 3. Energy module (SKIP FOR SIMPLE CASE)
# Ener_model = ener_elas(MRIO_BASE)

# 4. Input-Output calculations
IO_model = IO(MRIO_BASE)
IO_model.calculate_output_change(final_demand_shock)  # Calculates dq_total

# 5. Employment calculations
Empl_model = empl(MRIO_BASE)
Empl_model.calculate_employment(IO_model.dq_total)  # Calculates dempl_total

# 6. Save results
Results = results(MRIO_BASE, Scenario, IO_model, Empl_model)
Results.save()
```

**What YOU need to inspect:**
1. Open `RunMINDSET.py`
2. Find line ~97: `SPYDER = True` section
3. Look at line ~101: `scenario_name = "..."` ← This is what scenario file it loads
4. Scroll to find where `empl()` function is called
5. Note what inputs it receives

---

## STEP 5: Deep Dive into Employment Module

### File to Inspect: `SourceCode/employment.py`
**Location:** `.\SourceCode\employment.py`
**This is the CORE file for your analysis**

**What this file does:**
```python
# Simplified logic from employment.py

def calculate_employment(self, MRIO_BASE, output_changes):
    """
    Calculate employment changes from output changes

    Inputs:
        EMPL_COEF: Employment intensity (jobs per $ output)
        dq_total: Output changes by sector-region

    Output:
        dempl_total: Employment changes by sector-region
    """

    # Basic formula:
    dempl_total = EMPL_COEF * dq_total

    # Can also calculate by channel:
    dempl_direct = EMPL_COEF * dq_direct
    dempl_indirect = EMPL_COEF * dq_indirect
    dempl_induced = EMPL_COEF * dq_induced

    return dempl_total
```

**What YOU need to inspect:**
1. Open `SourceCode/employment.py`
2. Find the main calculation function (likely `calculate_employment` or similar)
3. Identify:
   - What input format does it expect? (pandas DataFrame? numpy array?)
   - What dimensions? (countries × sectors?)
   - How does it handle the multiplication?
4. Find where results are stored (e.g., `self.dempl_total`)

---

## STEP 6: Examine Input-Output Module

### File to Inspect: `SourceCode/InputOutput.py`
**Location:** `.\SourceCode\InputOutput.py`

**What this file does:**
```python
# Simplified logic from InputOutput.py

def calculate_output_change(self, L_BASE, Y_BASE, dY):
    """
    Calculate output changes from final demand changes

    Uses Leontief multiplier model:
    dX = L * dY

    where:
        dX = output change
        L = Leontief inverse = (I - A)^(-1)
        dY = final demand change (exogenous shock)
    """

    dq_total = L_BASE @ dY  # Matrix multiplication

    return dq_total
```

**What YOU need to inspect:**
1. Open `SourceCode/InputOutput.py`
2. Find where it uses `L_BASE` (Leontief inverse)
3. Find where it applies final demand shock `dY`
4. Identify the matrix multiplication operation
5. See where `dq_total` is calculated and stored

---

## STEP 7: Our Execution Plan with Synthetic Data

### Phase A: Create Synthetic Data (NEW SCRIPT)

**File to create:** `create_synthetic_GLORIA.py`
**Location:** `.\create_synthetic_GLORIA.py` (in root folder)

**What this script will do:**
1. Define dimensions (regions, sectors)
2. Create synthetic inter-industry matrix
3. Calculate Leontief inverse
4. Create employment coefficients
5. Save all in GLORIA format (.pkl files)

**Files it will create:**
- `GLORIA_db/synthetic/parsed_db/IND_sparse.pkl`
- `GLORIA_db/synthetic/parsed_db/VA.pkl`
- `GLORIA_db/synthetic/parsed_db/HH.pkl`
- `GLORIA_db/synthetic/parsed_db/FCF.pkl`
- `GLORIA_db/synthetic/parsed_db/cid.pkl` (country IDs)
- `GLORIA_db/synthetic/parsed_db/sid.pkl` (sector IDs)
- `GLORIA_db/synthetic/GLORIA_L_Base_2019.mat` (Leontief inverse)
- `GLORIA_db/synthetic/GLORIA_Y_Base_2019.mat` (final demand)
- `GLORIA_template/Employment/Synthetic_Empl_coefficient.csv`

---

### Phase B: Create Scenario File (NEW FILE)

**File to create:** `GLORIA_template/Scenarios/Synthetic_Infrastructure.xlsx`

**What this file will contain:**
- Sheet 1: "Scenario_Info"
  - Scenario name
  - Description: "$100M infrastructure investment in Region A"
- Sheet 2: "Final_Demand_Shock"
  - Region: A
  - Sector: Construction (40%), Manufacturing (30%), Services (30%)
  - Amount: $100M total
- Sheet 3: "Carbon_Tax" (all zeros - no tax)
- Sheet 4: "Revenue_Recycling" (all zeros - not applicable)

---

### Phase C: Modify exog_vars.py to Load Synthetic Data (MODIFICATION)

**File to modify:** `SourceCode/exog_vars.py`

**Changes needed:**
Add parameter to point to synthetic data folder:
```python
def __init__(self, synthetic=False):
    if synthetic:
        self.db_path = "GLORIA_db/synthetic/"
    else:
        self.db_path = "GLORIA_db/"
    # ... rest of loading code
```

---

### Phase D: Run Modified MINDSET (MODIFICATION)

**File to modify:** `RunMINDSET.py`

**Changes at line ~97:**
```python
if SPYDER:
    scenario_name = "Synthetic_Infrastructure"  # Our new scenario
    synthetic_data = True  # NEW FLAG
```

**Change at line ~129:**
```python
MRIO_BASE = exog_vars(synthetic=synthetic_data)  # Pass flag
```

---

### Phase E: Execute and Capture Results (EXECUTION)

**Command line:**
```bash
cd "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main"
python RunMINDSET.py
```

**Expected output:**
- Console messages showing progress through modules
- Results file: `GLORIA_results/Results_Synthetic_Infrastructure.xlsx`

---

### Phase F: Analyze Results (NEW SCRIPT)

**File to create:** `analyze_employment_results.py`

**What this script will do:**
1. Load results from Excel file
2. Extract employment impacts
3. Calculate:
   - Total jobs created
   - Jobs by sector
   - Jobs by region
   - Employment multiplier (jobs created / jobs directly invested)
4. Create summary tables and charts

---

## NEXT IMMEDIATE STEPS

### Step 1: Inspect Existing Files (DO NOW)
Let me help you inspect these files in order:

1. **Employment coefficient file**
   ```
   Read: GLORIA_template/Employment/Empl_coefficient.csv
   Questions: What are dimensions? What is format?
   ```

2. **Example scenario file**
   ```
   Read: GLORIA_template/Scenarios/[pick any .xlsx]
   Questions: What sheets? What format?
   ```

3. **Employment module**
   ```
   Read: SourceCode/employment.py
   Questions: What is the main function? What are inputs/outputs?
   ```

### Step 2: Create Synthetic Data Generator (NEXT)
After we understand the structure, we'll create `create_synthetic_GLORIA.py`

### Step 3: Create Scenario (AFTER SYNTHETIC DATA)
We'll create the infrastructure investment scenario file

### Step 4: Run Model (AFTER SCENARIO READY)
Execute RunMINDSET.py with our synthetic data

### Step 5: Analyze Results (FINAL)
Extract and interpret employment impacts

---

## SUMMARY: Files You Need to Inspect (In Order)

| Order | File Path | What to Look For |
|-------|-----------|------------------|
| 1 | `GLORIA_template/Employment/Empl_coefficient.csv` | Structure, dimensions, example values |
| 2 | `GLORIA_template/Scenarios/*.xlsx` (any one) | Sheet structure, how shocks are specified |
| 3 | `SourceCode/exog_vars.py` (lines 1-150) | What data structures are created |
| 4 | `SourceCode/employment.py` (entire file) | Main calculation logic |
| 5 | `SourceCode/InputOutput.py` (lines 1-200) | How output changes are calculated |
| 6 | `RunMINDSET.py` (lines 1-150, 400-500) | Overall execution flow |

---

**Ready to proceed?** Let's start with Step 1: inspecting these files together!

---

*Created: 2026-03-07*
*Purpose: Provide specific file paths and execution order for MINDSET beginner*
*Next: Inspect files together step-by-step*
