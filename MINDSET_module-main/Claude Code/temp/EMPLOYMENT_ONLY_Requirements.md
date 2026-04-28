# Employment Impact Estimation - Minimal Requirements

**Purpose:** Estimate employment impacts from exogenous final demand changes
**Scope:** Employment module ONLY - no energy, trade, household, or tax features

---

## CORE LOGIC: Employment Impact Calculation

```
Step 1: Define Exogenous Shock
   → $100M infrastructure investment

Step 2: Calculate Output Changes (Input-Output)
   → dX = L × dY
   → Where: L = Leontief inverse, dY = final demand change

Step 3: Calculate Employment Changes
   → dE = Employment_Coefficient × dX
   → Where: Employment_Coefficient = jobs per $ output

Step 4: Results
   → Employment impacts by sector and region
```

---

## REQUIRED DATA FILES

### 1. Inter-Industry Data (MRIO Tables)

**Location:** `GLORIA_db/parsed_db/` OR create synthetic

**Files needed:**
- `IND_sparse.pkl` - Inter-industry flows (Z matrix)
- `cid.pkl` - Country/region IDs
- `cou.pkl` - Country/region names
- `sid.pkl` - Sector IDs
- `sec.pkl` - Sector names

**Alternative:** Pre-calculated Leontief inverse
- `GLORIA_db/GLORIA_L_Base_2019.mat` - Leontief inverse (L matrix)
- `GLORIA_db/GLORIA_Y_Base_2019.mat` - Final demand (Y matrix)

**What these contain:**
```
IND_sparse.pkl: Inter-industry flows
   - Dimensions: (n_regions × n_sectors) × (n_regions × n_sectors)
   - Example: Flow from Region A, Manufacturing to Region B, Construction
   - Used to calculate technical coefficients (A) and Leontief inverse (L)

L_BASE: Leontief inverse = (I - A)^(-1)
   - Pre-calculated for speed
   - Used directly in: dX = L × dY

Y_BASE: Final demand by sector-region
   - Baseline final demand (household + government + investment + exports)
   - Used to calculate baseline output: X = L × Y
```

---

### 2. Employment Coefficients

**Location:** `GLORIA_template/Employment/Empl_coefficient.csv`

**Structure:**
```csv
SectorID, SectorName, Country1, Country2, Country3, ...
1, Growing wheat, 0.287, 0.591, 0.763, ...
2, Growing maize, 0.224, 0.624, 0.653, ...
3, Manufacturing, 0.050, 0.045, 0.080, ...
...
```

**What it contains:**
- Employment intensity by sector and region
- Units: Jobs per $1,000 (or per $1M) of output
- Dimensions: n_sectors × n_countries

---

### 3. Scenario Definition (Your Shock)

**Location:** `GLORIA_template/Scenarios/[YourScenario].xlsx` OR create new

**Minimum content needed:**
```
Sheet: "Final_Demand_Shock"
Columns: Region, Sector, Shock_Amount_USD

Example:
Region_A, Construction, 40000000    (40% of $100M)
Region_A, Manufacturing, 30000000   (30% of $100M)
Region_A, Services, 20000000        (20% of $100M)
Region_A, Utilities, 10000000       (10% of $100M)
```

**NOT needed for employment-only:**
- ❌ Carbon tax rates (skip)
- ❌ Revenue recycling (skip)
- ❌ Border tax adjustments (skip)
- ❌ Energy elasticities (skip)

---

## REQUIRED SCRIPTS

### 1. Data Loading: `SourceCode/exog_vars.py`

**What it does:**
- Loads all MRIO data from `GLORIA_db/`
- Loads employment coefficients from `GLORIA_template/Employment/`
- Creates MRIO_BASE object containing all data structures

**Key outputs:**
```python
MRIO_BASE.L_BASE          # Leontief inverse
MRIO_BASE.Y_BASE          # Final demand
MRIO_BASE.EMPL_COEF       # Employment coefficients
MRIO_BASE.COU_ID          # Country IDs
MRIO_BASE.SEC_ID          # Sector IDs
```

**What we can skip:**
- Energy elasticity loading (EN_OP_ELAS, EN_CP_ELAS_*)
- Trade elasticity loading (TRADE_ELAS)
- Household elasticity loading (HH_INC_ELAS, HH_OP_ELAS, HH_CP_ELAS_*)

---

### 2. Scenario Definition: `SourceCode/scenario.py`

**What it does:**
- Reads scenario file
- Extracts final demand shock (dY)
- Organizes shock by sector and region

**For employment-only, we need:**
```python
Scenario.exog_final_demand  # Your $100M investment shock
```

**What we can skip:**
- Tax rate extraction
- Revenue split calculations
- BTA (Border Tax Adjustment) setup
- Cost shock definitions

---

### 3. Input-Output Calculation: `SourceCode/InputOutput.py`

**What it does:**
- Takes final demand shock (dY)
- Calculates output changes: dX = L × dY
- Returns output changes by sector-region

**Key calculation:**
```python
def calculate_output_change(L_BASE, dY):
    """
    L_BASE: Leontief inverse (n×n matrix)
    dY: Final demand change (n×1 vector)

    Returns: dX (output change, n×1 vector)
    """
    dX = L_BASE @ dY  # Matrix multiplication
    return dX
```

**What we can skip:**
- Energy substitution effects (dL_ener)
- Trade substitution effects (A_trade)
- Iterative household income loops

---

### 4. Employment Calculation: `SourceCode/employment.py`

**What it does:**
- Takes output changes (dX)
- Takes employment coefficients
- Calculates employment changes: dE = coef × dX

**Key calculation:**
```python
def calculate_employment(EMPL_COEF, dX):
    """
    EMPL_COEF: Employment intensity (jobs per $ output)
    dX: Output changes by sector-region

    Returns: dE (employment change by sector-region)
    """
    dE = EMPL_COEF * dX  # Element-wise multiplication
    return dE
```

**Output:**
```python
dempl_total      # Total employment change by sector-region
dempl_direct     # Direct employment (in sectors receiving shock)
dempl_indirect   # Indirect employment (in supplying sectors)
```

---

### 5. Results Saving: `SourceCode/results.py`

**What it does:**
- Formats employment results
- Saves to Excel file

**Output file:**
```
GLORIA_results/Results_[ScenarioName].xlsx

Sheets:
  - Employment_Change: Employment impacts by sector and region
  - Summary: Total jobs created, by region, by sector
```

---

## EXECUTION FLOW (Simplified for Employment Only)

### Main Script: `RunMINDSET.py`

**Simplified flow:**
```python
# 1. Load data
MRIO_BASE = exog_vars()

# 2. Load scenario (your infrastructure investment)
Scenario = scenario(MRIO_BASE, scenario_file_path)
dY = Scenario.exog_final_demand  # Your shock vector

# 3. Calculate output changes
L = MRIO_BASE.L_BASE  # Leontief inverse
dX = L @ dY           # Output changes

# 4. Calculate employment changes
EMPL_COEF = MRIO_BASE.EMPL_COEF
dE = EMPL_COEF * dX   # Employment changes

# 5. Save results
results.save_employment(dE, scenario_name)
```

**Modules to SKIP:**
- ❌ `ener_elas.py` (energy elasticities)
- ❌ `ener_balance.py` (energy balance/carbon tax)
- ❌ `trade.py` (trade substitution)
- ❌ `household.py` (household demand response)
- ❌ `government.py` (government spending)
- ❌ `investment.py` (induced investment)
- ❌ `price.py` (price effects)
- ❌ `tax_rev.py` (tax revenue)
- ❌ `BTA.py` (border tax adjustments)

---

## SYNTHETIC DATA REQUIREMENTS (Minimal)

Since you don't have GLORIA, create synthetic versions:

### Required Synthetic Files:

**1. Inter-industry matrix**
```
File: GLORIA_db/synthetic/parsed_db/IND_sparse.pkl
Dimensions: (n_regions × n_sectors) × (n_regions × n_sectors)
Content: Dollar flows between sector-region pairs
```

**2. Leontief inverse**
```
File: GLORIA_db/synthetic/GLORIA_L_Base_2019.mat
Dimensions: (n_regions × n_sectors) × (n_regions × n_sectors)
Content: (I - A)^(-1) where A = technical coefficients
```

**3. Employment coefficients**
```
File: GLORIA_template/Employment/Synthetic_Empl_coefficient.csv
Dimensions: n_sectors × n_regions
Content: Jobs per $1M output by sector-region
```

**4. Identifiers**
```
Files:
  - GLORIA_db/synthetic/parsed_db/cid.pkl (region IDs)
  - GLORIA_db/synthetic/parsed_db/sid.pkl (sector IDs)
```

**5. Scenario file**
```
File: GLORIA_template/Scenarios/Infrastructure_Investment.xlsx
Content: Final demand shock by sector-region
```

---

## WHAT YOU DON'T NEED

For **employment-only** estimation:

### Data You Can Skip:
- ❌ Energy balance data
- ❌ Carbon emission factors
- ❌ Energy elasticities (own-price, cross-price)
- ❌ Trade elasticities
- ❌ Household elasticities (income, own-price, cross-price)
- ❌ Investment conversion matrices
- ❌ Supply constraints/criticality data
- ❌ Tax rate parameters

### Scripts You Can Skip:
- ❌ `ener_elas.py`
- ❌ `ener_balance.py`
- ❌ `trade.py`
- ❌ `household.py`
- ❌ `government.py`
- ❌ `investment.py`
- ❌ `price.py`
- ❌ `tax_rev.py`
- ❌ `BTA.py`
- ❌ `prod_cost.py`
- ❌ `income.py`
- ❌ `GDP.py`

---

## SUMMARY: MINIMAL FILE CHECKLIST

### ✅ Required Data Files:
- [ ] Inter-industry matrix (IND_sparse.pkl) OR Leontief inverse (GLORIA_L_Base_2019.mat)
- [ ] Final demand baseline (Y_BASE - can be simple, just for scaling)
- [ ] Employment coefficients (Empl_coefficient.csv)
- [ ] Country/region IDs (cid.pkl, cou.pkl)
- [ ] Sector IDs (sid.pkl, sec.pkl)
- [ ] Scenario file (your infrastructure investment shock)

### ✅ Required Scripts:
- [ ] `SourceCode/exog_vars.py` (load data)
- [ ] `SourceCode/scenario.py` (load shock)
- [ ] `SourceCode/InputOutput.py` (calculate dX = L × dY)
- [ ] `SourceCode/employment.py` (calculate dE = coef × dX)
- [ ] `SourceCode/results.py` (save results)
- [ ] `RunMINDSET.py` (main coordinator - needs modification to skip other modules)

### ✅ Your Input:
- [ ] Define exogenous shock: $100M infrastructure investment
- [ ] Allocate across sectors: e.g., 40% Construction, 30% Manufacturing, etc.
- [ ] Choose target region: e.g., Region A

### 📊 Output:
- [ ] Employment changes by sector and region (jobs created)
- [ ] Total jobs created
- [ ] Employment multiplier (jobs per $M invested)

---

## NEXT STEP: CREATE MINIMAL SYNTHETIC DATA

We need to create a script that generates ONLY these essential files:

```
create_synthetic_employment_data.py
   ↓
Generates:
   1. Leontief inverse (L matrix)
   2. Employment coefficients
   3. Country/sector IDs
   4. Infrastructure investment scenario
```

This will be much simpler than creating the full GLORIA database!

---

**Ready to proceed?** We'll create the minimal synthetic data generator next.
