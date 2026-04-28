# Employment Impact Estimation - Visual Flow

## SIMPLIFIED FLOW: Employment Impacts Only

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUTS REQUIRED                           │
└─────────────────────────────────────────────────────────────┘

INPUT 1: Leontief Inverse Matrix (L)
┌────────────────────────────────────┐
│  From: GLORIA_L_Base_2019.mat      │
│  OR calculate from IND_sparse.pkl  │
│  Dimensions: (n×n)                 │
│  n = regions × sectors             │
└────────────────────────────────────┘

INPUT 2: Employment Coefficients
┌────────────────────────────────────┐
│  From: Empl_coefficient.csv        │
│  Format: sectors × regions         │
│  Values: jobs per $1M output       │
└────────────────────────────────────┘

INPUT 3: Exogenous Shock (Your Scenario)
┌────────────────────────────────────┐
│  $100M infrastructure investment   │
│  - 40% Construction                │
│  - 30% Manufacturing               │
│  - 20% Services                    │
│  - 10% Utilities                   │
│  Target: Region A                  │
└────────────────────────────────────┘

INPUT 4: Identifiers
┌────────────────────────────────────┐
│  Region IDs/Names (cid.pkl)        │
│  Sector IDs/Names (sid.pkl)        │
└────────────────────────────────────┘

                    ↓

┌─────────────────────────────────────────────────────────────┐
│                  CALCULATION STEPS                           │
└─────────────────────────────────────────────────────────────┘

STEP 1: Load Data
┌────────────────────────────────────┐
│  Script: exog_vars.py              │
│  Action: Load all inputs above     │
│  Output: MRIO_BASE object          │
└────────────────────────────────────┘
                    ↓
STEP 2: Define Scenario
┌────────────────────────────────────┐
│  Script: scenario.py               │
│  Action: Parse investment shock    │
│  Output: dY vector (n×1)           │
│          [$0, $0, $40M, $30M, ...] │
└────────────────────────────────────┘
                    ↓
STEP 3: Calculate Output Changes
┌────────────────────────────────────┐
│  Script: InputOutput.py            │
│  Calculation: dX = L × dY          │
│  Output: dX vector (n×1)           │
│          Output change by          │
│          sector-region             │
└────────────────────────────────────┘
                    ↓
STEP 4: Calculate Employment Changes
┌────────────────────────────────────┐
│  Script: employment.py             │
│  Calculation: dE = Coef × dX       │
│  Output: dE vector (n×1)           │
│          Jobs created by           │
│          sector-region             │
└────────────────────────────────────┘
                    ↓
STEP 5: Format & Save Results
┌────────────────────────────────────┐
│  Script: results.py                │
│  Action: Create Excel summary      │
│  Output: Results_[Scenario].xlsx   │
└────────────────────────────────────┘

                    ↓

┌─────────────────────────────────────────────────────────────┐
│                    OUTPUTS DELIVERED                         │
└─────────────────────────────────────────────────────────────┘

OUTPUT: Employment Impacts
┌────────────────────────────────────┐
│  TOTAL JOBS CREATED: X,XXX jobs   │
│                                    │
│  By Region:                        │
│    Region A: X,XXX jobs            │
│    Region B: XXX jobs              │
│    Rest of World: XXX jobs         │
│                                    │
│  By Sector:                        │
│    Construction: X,XXX jobs        │
│    Manufacturing: X,XXX jobs       │
│    Services: XXX jobs              │
│    ...                             │
│                                    │
│  Employment Multiplier:            │
│    X.XX jobs per $1M invested      │
└────────────────────────────────────┘
```

---

## MODULES SKIPPED (Not Needed for Employment-Only)

```
❌ SKIPPED: Energy Module
   - ener_elas.py
   - ener_balance.py
   Purpose: Energy substitution, carbon tax
   Not needed for simple final demand shock

❌ SKIPPED: Trade Module
   - trade.py
   Purpose: Trade substitution based on prices
   Not needed for employment estimation

❌ SKIPPED: Household Module
   - household.py
   Purpose: Household consumption response to prices/income
   Not needed without income feedback loop

❌ SKIPPED: Government Module
   - government.py
   Purpose: Government spending from tax revenue
   Not applicable without taxes

❌ SKIPPED: Investment Module
   - investment.py
   Purpose: Induced investment from output growth
   Can skip for simple analysis

❌ SKIPPED: Price Module
   - price.py
   Purpose: Price changes from cost shocks
   Not needed for quantity-only analysis

❌ SKIPPED: Tax/Revenue Modules
   - tax_rev.py
   - BTA.py
   Purpose: Carbon tax calculations
   Not applicable to infrastructure investment

❌ SKIPPED: Income/GDP Modules
   - income.py
   - GDP.py
   Purpose: Income feedback, GDP accounting
   Not needed for employment focus
```

---

## FILE STRUCTURE (Minimal)

```
MINDSET_module-main/
│
├── SourceCode/
│   ├── exog_vars.py          ✅ NEEDED (load data)
│   ├── scenario.py           ✅ NEEDED (load shock)
│   ├── InputOutput.py        ✅ NEEDED (calculate dX)
│   ├── employment.py         ✅ NEEDED (calculate dE)
│   ├── results.py            ✅ NEEDED (save results)
│   │
│   ├── ener_elas.py          ❌ SKIP
│   ├── ener_balance.py       ❌ SKIP
│   ├── trade.py              ❌ SKIP
│   ├── household.py          ❌ SKIP
│   ├── government.py         ❌ SKIP
│   ├── investment.py         ❌ SKIP
│   ├── price.py              ❌ SKIP
│   ├── tax_rev.py            ❌ SKIP
│   ├── BTA.py                ❌ SKIP
│   ├── income.py             ❌ SKIP
│   └── GDP.py                ❌ SKIP
│
├── GLORIA_db/
│   └── synthetic/                      (We'll create this)
│       ├── GLORIA_L_Base_2019.mat      ✅ NEEDED (Leontief)
│       └── parsed_db/
│           ├── cid.pkl                 ✅ NEEDED (region IDs)
│           ├── sid.pkl                 ✅ NEEDED (sector IDs)
│           └── IND_sparse.pkl          (Optional, if calculating L)
│
├── GLORIA_template/
│   ├── Employment/
│   │   └── Empl_coefficient.csv        ✅ NEEDED (employment coef)
│   │
│   └── Scenarios/
│       └── Infrastructure_Invest.xlsx  ✅ NEEDED (your shock)
│
├── GLORIA_results/
│   └── Results_Infrastructure.xlsx     ✅ OUTPUT (created by model)
│
└── RunMINDSET.py                       ✅ NEEDED (main script, modified)
```

---

## MINIMAL DATA DIMENSIONS

For demonstration/learning (vs full GLORIA):

```
┌─────────────────────────────────────────────────────────────┐
│              GLORIA (Full)      vs    Synthetic (Minimal)   │
├─────────────────────────────────────────────────────────────┤
│  Regions:    169                      3                     │
│  Sectors:    163                      10                    │
│  Matrix:     27,547 cells             30 cells              │
│  L matrix:   757M cells               900 cells             │
│  Runtime:    Hours                    Minutes               │
└─────────────────────────────────────────────────────────────┘

Regions (Synthetic):
  1. Region A (developed)
  2. Region B (emerging)
  3. Rest of World

Sectors (Synthetic):
  1. Agriculture
  2. Mining
  3. Manufacturing
  4. Construction         ← Primary target for infrastructure
  5. Utilities
  6. Trade & Transport
  7. Financial Services
  8. Business Services
  9. Government Services
  10. Other Services
```

---

## CALCULATION EXAMPLE (Simplified)

```python
# Given:
L = Leontief_inverse  # 30×30 matrix (10 sectors × 3 regions)
dY = [0, 0, 0, ..., 40M, 30M, 20M, 10M, ...]  # Shock vector (30×1)
     # Position 13: Region A, Construction = $40M
     # Position 14: Region A, Manufacturing = $30M
     # etc.

# Step 1: Calculate output changes
dX = L @ dY
# Result: Output increases in all sectors due to linkages
# Example output:
#   dX[13] = $50M  (Construction in Region A - direct + indirect)
#   dX[14] = $35M  (Manufacturing in Region A)
#   dX[23] = $5M   (Construction in Region B - spillover)
#   ...

# Step 2: Get employment coefficients
Emp_Coef = [15, 8, 6, 10, 4, ...]  # Jobs per $1M output
           # Position 13 (Region A, Construction) = 10 jobs/$M

# Step 3: Calculate employment changes
dE = Emp_Coef * dX
# Result:
#   dE[13] = 10 × $50M = 500 jobs (Construction, Region A)
#   dE[14] = 6 × $35M = 210 jobs (Manufacturing, Region A)
#   dE[23] = 10 × $5M = 50 jobs (Construction, Region B)
#   ...

# Step 4: Sum total
Total_Jobs = sum(dE) = 1,250 jobs

# Employment Multiplier:
Multiplier = 1,250 jobs / $100M = 12.5 jobs per $1M invested
```

---

## SUMMARY: 3 CORE EQUATIONS

```
┌─────────────────────────────────────────────────────────────┐
│  EQUATION 1: Leontief Model (Output Changes)                │
├─────────────────────────────────────────────────────────────┤
│  dX = L × dY                                                 │
│                                                              │
│  Where:                                                      │
│    dX = Output changes (what we want)                       │
│    L = (I - A)^(-1) = Leontief inverse                      │
│    dY = Final demand change (your $100M shock)              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  EQUATION 2: Employment Changes                             │
├─────────────────────────────────────────────────────────────┤
│  dE = e × dX                                                 │
│                                                              │
│  Where:                                                      │
│    dE = Employment changes (jobs created)                   │
│    e = Employment coefficient (jobs per $ output)           │
│    dX = Output changes (from Equation 1)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  EQUATION 3: Employment Multiplier                          │
├─────────────────────────────────────────────────────────────┤
│  m = Total Jobs Created / Investment Amount                 │
│                                                              │
│  Where:                                                      │
│    m = Employment multiplier (jobs per $1M)                 │
│    Typical range: 5-20 jobs per $1M                         │
└─────────────────────────────────────────────────────────────┘
```

**That's it!** Three equations, five data files, five scripts, one result.

---

**Next Step:** Create the minimal synthetic data generator that produces exactly these files.
