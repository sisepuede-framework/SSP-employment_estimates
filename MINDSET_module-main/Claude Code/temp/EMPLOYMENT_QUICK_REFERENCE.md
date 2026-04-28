# Employment Impact Estimation - Quick Reference

**Last Updated:** 2026-03-09
**Purpose:** One-page reference for employment-only MINDSET analysis

---

## 📊 WHAT YOU NEED (Checklist)

### ✅ 5 Data Files Required:

1. **Leontief Inverse**
   - File: `GLORIA_db/synthetic/GLORIA_L_Base_2019.mat`
   - Dimensions: (30×30) for 3 regions × 10 sectors
   - Content: (I - A)^(-1) matrix

2. **Employment Coefficients**
   - File: `GLORIA_template/Employment/Empl_coefficient.csv`
   - Dimensions: 10 sectors × 3 regions
   - Content: Jobs per $1M output

3. **Region Identifiers**
   - File: `GLORIA_db/synthetic/parsed_db/cid.pkl`
   - Content: ['RegionA', 'RegionB', 'ROW']

4. **Sector Identifiers**
   - File: `GLORIA_db/synthetic/parsed_db/sid.pkl`
   - Content: List of 10 sector names

5. **Investment Scenario**
   - File: `GLORIA_template/Scenarios/Infrastructure_Investment.xlsx`
   - Content: $100M allocation by sector

---

### ✅ 5 Scripts Required:

1. `SourceCode/exog_vars.py` → Load data
2. `SourceCode/scenario.py` → Parse shock
3. `SourceCode/InputOutput.py` → Calculate dX = L × dY
4. `SourceCode/employment.py` → Calculate dE = Coef × dX
5. `SourceCode/results.py` → Save outputs

**Main coordinator:** `RunMINDSET.py` (modified to skip other modules)

---

### ❌ 11 Modules to SKIP:

- ener_elas.py, ener_balance.py (energy)
- trade.py (trade substitution)
- household.py (household response)
- government.py (government spending)
- investment.py (induced investment)
- price.py (price effects)
- tax_rev.py, BTA.py (taxes)
- income.py, GDP.py (income/GDP)

---

## 🔢 THE 3 CORE EQUATIONS

```
1. OUTPUT CHANGES:      dX = L × dY
   Where: L = Leontief inverse, dY = $100M shock

2. EMPLOYMENT CHANGES:  dE = e × dX
   Where: e = employment coefficient, dX = output changes

3. MULTIPLIER:          m = Σ(dE) / $100M
   Where: m = jobs per $1M invested
```

---

## 📏 DIMENSIONS (Synthetic Data)

```
Regions:   3  (RegionA, RegionB, RestOfWorld)
Sectors:   10 (Agriculture, Mining, Manufacturing, Construction,
               Utilities, Trade, Financial, Business, Government, Other)

Vector Length:        n = 30 (3 regions × 10 sectors)
Leontief Matrix:      L = 30×30 = 900 cells
Employment Coef:      e = 30×1 = 30 values
Final Demand Shock:   dY = 30×1 = 30 values
Output Change:        dX = 30×1 = 30 values
Employment Change:    dE = 30×1 = 30 values
```

---

## 💼 YOUR SCENARIO

**Infrastructure Investment:** $100M in RegionA

**Allocation:**
- 40% → Construction ($40M)
- 30% → Manufacturing ($30M)
- 20% → Business Services ($20M)
- 10% → Utilities ($10M)

**Expected Result:**
- Total jobs created: ~1,000-1,500 jobs
- Employment multiplier: 10-15 jobs per $1M
- By sector: Construction (500+), Manufacturing (200+), Others (300+)

---

## 🗂️ FILE STRUCTURE

```
MINDSET_module-main/
│
├── SourceCode/
│   ├── exog_vars.py          ✅
│   ├── scenario.py           ✅
│   ├── InputOutput.py        ✅
│   ├── employment.py         ✅
│   ├── results.py            ✅
│   └── [11 other modules]    ❌ SKIP
│
├── GLORIA_db/synthetic/
│   ├── GLORIA_L_Base_2019.mat         ✅
│   └── parsed_db/
│       ├── cid.pkl                    ✅
│       └── sid.pkl                    ✅
│
├── GLORIA_template/
│   ├── Employment/
│   │   └── Empl_coefficient.csv      ✅
│   └── Scenarios/
│       └── Infrastructure_Invest.xlsx ✅
│
├── GLORIA_results/
│   └── Results_Infrastructure.xlsx    📊 OUTPUT
│
├── RunMINDSET.py                      ✅ (modified)
│
└── create_synthetic_data.py           🔧 TO CREATE
```

---

## 🚀 EXECUTION STEPS

```bash
# Step 1: Create synthetic data
python create_synthetic_data.py

# Step 2: Run MINDSET (employment-only)
python RunMINDSET.py

# Step 3: Check results
# Open: GLORIA_results/Results_Infrastructure_Investment.xlsx
```

---

## 📊 EXPECTED OUTPUT

**Excel File:** `GLORIA_results/Results_Infrastructure_Investment.xlsx`

**Contents:**
- Sheet 1: Employment_Changes
  - Rows: 30 (each sector-region combination)
  - Columns: Sector, Region, Jobs_Created

- Sheet 2: Summary
  - Total jobs created
  - Jobs by region
  - Jobs by sector
  - Employment multiplier (jobs/$M)

**Sample Output:**
```
Total Jobs Created: 1,250

By Region:
  RegionA:      1,000 jobs (80%)
  RegionB:        150 jobs (12%)
  RestOfWorld:    100 jobs (8%)

By Sector:
  Construction:   500 jobs (40%)
  Manufacturing:  250 jobs (20%)
  Services:       300 jobs (24%)
  Other:          200 jobs (16%)

Employment Multiplier: 12.5 jobs per $1M invested
```

---

## 🎯 NEXT ACTIONS

1. **Review Requirements:**
   - Read: `EMPLOYMENT_ONLY_Requirements.md` (detailed)
   - Read: `EMPLOYMENT_ONLY_Visual_Flow.md` (diagrams)

2. **Create Synthetic Data:**
   - Generate: `create_synthetic_data.py` script
   - Run it to create 5 required data files

3. **Modify Main Script:**
   - Edit: `RunMINDSET.py`
   - Skip 11 unnecessary modules
   - Run employment-only workflow

4. **Execute & Analyze:**
   - Run model
   - Extract employment impacts
   - Calculate multipliers
   - Document for supervisor

---

## 💡 KEY INSIGHTS

1. **Employment estimation is simple:** Just 3 equations, 5 data files, 5 scripts

2. **Synthetic data is tiny:** 30 employment coefficients, 900-cell Leontief matrix

3. **Most MINDSET features not needed:** 11 of 16 modules can be skipped

4. **Fast execution:** Minutes, not hours (900× smaller than full GLORIA)

5. **Same methodology:** Matches full MINDSET, just simplified data

---

## 📚 DOCUMENTATION FILES

All in: `Claude Code/temp/`

- `EMPLOYMENT_QUICK_REFERENCE.md` ← You are here
- `EMPLOYMENT_ONLY_Requirements.md` ← Detailed requirements
- `EMPLOYMENT_ONLY_Visual_Flow.md` ← Visual diagrams
- `START_HERE.md` ← General orientation
- `MINDSET_Workflow_Guide.md` ← Full workflow context
- `MINDSET_Execution_Steps.md` ← Step-by-step guide

---

**Ready to create synthetic data?** Let me know and I'll generate the `create_synthetic_data.py` script!
