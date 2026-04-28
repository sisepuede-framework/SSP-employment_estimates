# START HERE: MINDSET Employment Analysis Guide

**For R Users Running Employment Estimates with MINDSET in Python**

---

## 🎯 What You Have Now

I've created a complete setup for you to run employment impact analysis using the MINDSET model. All files are in the `Claude Code/temp` directory.

### ✅ Fixed Issues:
1. **Path problems** - Script can now find all MINDSET modules
2. **Import errors** - SourceCode modules load correctly
3. **Data location** - GLORIA database is accessible
4. **Positron compatibility** - Works perfectly in Positron IDE

### 📁 Files Created:

#### Core Scripts
1. **`RunMINDSET_EmploymentOnly.py`** ⭐ MAIN SCRIPT
   - Your employment analysis script (FIXED with proper paths)
   - Calculates: dX = L × dY, then dE = e × dX
   - Outputs: Employment by region, by sector, multipliers

2. **`create_scenario_template.py`**
   - Generates scenario template Excel files
   - Creates product and region reference lists
   - Creates 3 example scenarios ready to use

3. **`generate_custom_scenario.py`**
   - Creates custom scenarios programmatically
   - No manual Excel editing needed!
   - Perfect for testing 120 products

4. **`check_paths.py`**
   - Diagnostic tool to verify everything works
   - Run this FIRST to check setup

#### Documentation
5. **`SCENARIO_FILE_GUIDE.md`** - Complete guide to scenario files
6. **`SCENARIO_QUICK_REFERENCE.md`** - Quick cheat sheet
7. **`SETUP_AND_RUN_GUIDE.md`** - Complete setup and usage
8. **`POSITRON_QUICKSTART.md`** - Positron IDE guide
9. **`PATH_FIX_EXPLAINED.md`** - R vs Python paths explained
10. **`README_START_HERE.md`** - This file!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Verify Setup (2 minutes)

In Positron terminal:
```bash
cd "Claude Code/temp"
python check_paths.py
```

**Expected output:** All ✓ marks

**If you see ✗ marks:** Check that file/directory exists

### Step 2: Generate Example Scenarios (2 minutes)

```bash
python create_scenario_template.py
```

**What this creates:**
- ✓ `Scenario_Template.xlsx` - Empty template for your own scenarios
- ✓ `GLORIA_Products_List.xlsx` - All 120 products reference
- ✓ `GLORIA_Regions_List.xlsx` - All 162 regions reference
- ✓ `Example_1M_Per_Product.xlsx` - $1M to each product (good for testing!)
- ✓ `Example_Construction_100M.xlsx` - $100M construction investment
- ✓ `Example_MultiCountry_Comparison.xlsx` - Compare 5 countries

### Step 3: Run Employment Analysis (5-10 minutes)

In Positron:

1. **Open `RunMINDSET_EmploymentOnly.py`**

2. **Set scenario (line 103):**
   ```python
   scenario_name = "Example_Construction_100M"  # Try this first!
   ```

3. **Run script:** Press `Ctrl+Shift+Enter`

4. **Check results:**
   - File: `GLORIA_results/Results_Example_Construction_100M_EmploymentOnly.xlsx`
   - Sheets: Summary, Employment_by_Region, Employment_by_Sector, Details

---

## 💡 Understanding the Scenario File

### What It Is (R Analogy)

**In R you might do:**
```r
# Your demand shock data
shock <- data.frame(
  country = c("USA", "USA", "CHN"),
  product = c(56, 1, 56),
  amount = c(100000000, 1000000, 100000000)
)

# Calculate impacts
output_change <- Leontief_matrix %*% shock$amount
employment_change <- employment_coef * output_change
```

**In MINDSET:**
- The Excel file IS your `shock` data.frame
- The script does the matrix math automatically
- You just specify: Which country, which product, how much $$$

### Excel Structure

Your scenario file has this structure:

```
Row 1-14:  Header/metadata (template boilerplate)
Row 15:    Column names (MUST be exact!)
Row 16+:   Your demand shocks (your data)
```

**Required columns (row 15):**
- `Producing country ISO*` - Country making the product
- `Consuming country ISO*` - Country buying it
- `Product code*` - Product 1-120
- `FD code*` - Final demand type (use FD_4)
- `Value*` - Dollar amount
- `Type*` - Value type (use abs-b)

**Example data (row 16):**
```
USA | USA | 56 | FD_4 | 100000000 | abs-b
```
= $100M to Construction (product 56) in USA

---

## 📊 Your Research Question

You want to test employment impacts across different products/sectors.

### Approach A: Test All 120 Products (Recommended!)

**Generate the scenario:**
```bash
python generate_custom_scenario.py --mode all_products --amount 1000000 --country USA
```

**This creates:**
- One Excel file
- 120 rows (one per product)
- $1M investment in each

**Run once, get:**
- Employment multiplier for all 120 products
- Compare which sectors create most jobs
- One comprehensive Excel output

**R equivalent:**
```r
products <- 1:120
results <- data.frame()
for (p in products) {
  shock <- create_shock(product=p, amount=1e6, country="USA")
  result <- run_io_model(shock)
  results <- rbind(results, result)
}
```

### Approach B: Focus on Specific Sectors

**Construction:**
```bash
python generate_custom_scenario.py --mode specific_products --products "56" --amount 100000000 --country USA --name "Construction_100M"
```

**Manufacturing (products 20-40):**
```bash
python generate_custom_scenario.py --mode product_range --range "20-40" --amount 100000000 --country USA --name "Manufacturing_100M"
```

**Agriculture (products 1-15):**
```bash
python generate_custom_scenario.py --mode product_range --range "1-15" --amount 100000000 --country USA --name "Agriculture_100M"
```

**Then run script 3 times** (change scenario_name each time)

### Approach C: Country Comparisons

**Generate:**
```bash
python generate_custom_scenario.py --mode multi_country --countries "USA,CHN,DEU,BRA,IND" --product 56 --amount 100000000
```

**Run once, compare** employment creation across countries

---

## 📖 Key Concepts for R Users

### Input-Output Model Basics

**The Core Equations:**
```
1. Output changes:      dX = L × dY
   where L = Leontief inverse, dY = final demand shock

2. Employment changes:  dE = e × dX
   where e = employment coefficient, dX = output change

3. Employment multiplier = Total jobs / Investment ($M)
```

**R equivalent:**
```r
# Leontief inverse
L <- solve(I - A)  # where A is technical coefficients

# Output change
dX <- L %*% dY

# Employment change
dE <- empl_coef * dX

# Multiplier
multiplier <- sum(dE) / (sum(dY) / 1e6)  # Jobs per $1M
```

### GLORIA Database

- **120 products** (agriculture, manufacturing, services, construction, etc.)
- **162 regions** (countries + ROW)
- **Dimensions:** 120 × 162 = 19,440 sector-regions
- **Year:** 2019 (most recent parsed data)

### Final Demand Categories

| Code | Category | Use When |
|------|----------|----------|
| FD_1 | Household consumption | Consumer demand |
| FD_3 | Government spending | Public sector |
| **FD_4** | **Investment** | **Infrastructure (Recommended)** |

---

## 🔧 Common Commands

### Diagnostics
```bash
cd "Claude Code/temp"
python check_paths.py  # Verify setup
```

### Generate Scenarios
```bash
# All products
python generate_custom_scenario.py --mode all_products --amount 1000000 --country USA

# Specific products
python generate_custom_scenario.py --mode specific_products --products "1,5,10,56" --amount 5000000 --country USA

# Product range
python generate_custom_scenario.py --mode product_range --range "1-20" --amount 10000000 --country USA

# Multiple countries
python generate_custom_scenario.py --mode multi_country --countries "USA,CHN,DEU" --product 56 --amount 100000000
```

### Run Analysis
```python
# In Positron:
# 1. Open RunMINDSET_EmploymentOnly.py
# 2. Edit line 103: scenario_name = "YourScenarioName"
# 3. Press Ctrl+Shift+Enter
```

---

## 📋 Typical Workflow

```
Day 1: Setup & Test
├─ 1. Run check_paths.py (verify setup)
├─ 2. Run create_scenario_template.py (get examples)
├─ 3. Test with Example_Construction_100M
└─ 4. Examine output Excel file

Day 2: Generate Your Scenarios
├─ 1. Decide: test all products? specific sectors? countries?
├─ 2. Use generate_custom_scenario.py
└─ 3. Verify files in GLORIA_template/Scenarios/

Day 3+: Run Analysis
├─ 1. For each scenario:
│     ├─ Update scenario_name (line 103)
│     ├─ Run script
│     └─ Save results
└─ 2. Combine results in R for analysis/visualization
```

---

## 📊 Output Structure

The script creates one Excel file per scenario with 5 sheets:

### 1. Summary
- Total investment
- Total jobs created
- Employment multiplier (jobs/$1M)
- Output multiplier

### 2. Employment_by_Region
- Jobs created per country/region
- Sorted by impact

### 3. Employment_by_Sector
- Jobs created per product/industry
- Sorted by impact

### 4. Employment_Details
- Full sector-region breakdown
- All 19,440 rows (162 regions × 120 products)

### 5. Output_Details
- Output changes for validation
- Check if results are reasonable

---

## 🔍 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'SourceCode'"
**Solution:** Path setup issue
```bash
python check_paths.py  # Should show the problem
```
The script should automatically fix paths (lines 32-56)

### Problem: "FileNotFoundError: GLORIA_template\\Scenarios\\..."
**Solution:** Scenario file not found
- Check file is in `GLORIA_template/Scenarios/`
- Check `scenario_name` matches filename (without .xlsx)
- Check you ran `create_scenario_template.py` first

### Problem: "No exogenous final demand found"
**Solution:** Excel file format issue
- Check sheet named exactly "Final demand"
- Check columns named exactly (with *)
- Check data starts at row 16
- Use `Scenario_Template.xlsx` as starting point

### Problem: Zero jobs created
**Solution:** Data format issue
- Check `Value*` column has numbers (not text/formulas)
- Check `Type*` is "abs-b"
- Check `Product code*` is valid (1-120)

---

## 📚 Documentation Files

### For Quick Reference
- **`SCENARIO_QUICK_REFERENCE.md`** ⭐ Cheat sheet
  - Commands, examples, quick tips

### For Learning
- **`SCENARIO_FILE_GUIDE.md`** - Deep dive on scenario files
- **`SETUP_AND_RUN_GUIDE.md`** - Complete setup guide
- **`POSITRON_QUICKSTART.md`** - Positron IDE tips
- **`PATH_FIX_EXPLAINED.md`** - Understanding path issues

### Open in Positron
- Click file in Files panel
- Or use terminal: `code SCENARIO_QUICK_REFERENCE.md`

---

## 🎓 For Your Dissertation

### Suggested Analysis Path

1. **Descriptive Analysis**
   - Run: all 120 products with $1M each
   - Calculate: employment multiplier for each product
   - Plot: ranking of products by jobs/$1M
   - Identify: which sectors create most jobs

2. **Sectoral Analysis**
   - Group: products into sectors (agriculture, manufacturing, services, etc.)
   - Compare: employment multipliers across sectors
   - Analyze: direct vs indirect employment

3. **Geographic Analysis**
   - Test: same investment across different countries
   - Compare: USA vs China vs Brazil vs others
   - Analyze: why multipliers differ

4. **Policy Analysis**
   - Test: different investment amounts
   - Analyze: linearity assumptions
   - Compare: infrastructure vs other investments

### Combining Results in R

After running multiple scenarios, combine in R:

```r
library(tidyverse)
library(readxl)

# Read all results
files <- list.files("GLORIA_results", pattern="Results_.*_EmploymentOnly.xlsx", full.names=TRUE)

results <- map_df(files, ~{
  read_excel(.x, sheet="Summary") %>%
    mutate(scenario = str_extract(.x, "Results_(.*)_EmploymentOnly", group=1))
})

# Analyze
results %>%
  arrange(desc(`Employment Multiplier`)) %>%
  ggplot(aes(x=reorder(scenario, `Employment Multiplier`),
             y=`Employment Multiplier`)) +
  geom_col() +
  coord_flip()
```

---

## ✅ Checklist: Ready to Start?

Before running your first analysis:

- [ ] Ran `check_paths.py` → all ✓ marks
- [ ] Ran `create_scenario_template.py` → files created
- [ ] Have `GLORIA_Products_List.xlsx` for reference
- [ ] Have `GLORIA_Regions_List.xlsx` for reference
- [ ] Opened `RunMINDSET_EmploymentOnly.py` in Positron
- [ ] Understand scenario file structure (row 15 = headers, row 16+ = data)
- [ ] Know how to generate scenarios (`generate_custom_scenario.py`)

If all checked ✅ → **You're ready!**

---

## 🎯 Start NOW: Recommended First Steps

### 1. Verify Everything Works (5 min)
```bash
cd "Claude Code/temp"
python check_paths.py
```
Look for all ✓ marks

### 2. Generate Examples (2 min)
```bash
python create_scenario_template.py
```
Creates reference lists and example scenarios

### 3. Test Run (10 min)
```python
# In Positron, open RunMINDSET_EmploymentOnly.py
# Line 103: scenario_name = "Example_Construction_100M"
# Press Ctrl+Shift+Enter
# Wait for completion
# Check: GLORIA_results/Results_Example_Construction_100M_EmploymentOnly.xlsx
```

### 4. Generate Your First Real Scenario (5 min)
```bash
python generate_custom_scenario.py --mode all_products --amount 1000000 --country USA
```

### 5. Run Your Analysis (10 min)
```python
# Line 103: scenario_name = "AllProducts_1M_USA"
# Run script
# Analyze results!
```

**Total time: ~30 minutes from zero to results! 🎉**

---

## 💬 Questions?

### Quick answers:
- **"Which file do I run?"** → `RunMINDSET_EmploymentOnly.py`
- **"How do I create scenarios?"** → Use `generate_custom_scenario.py` or edit `Scenario_Template.xlsx`
- **"What's the 120 products?"** → Check `GLORIA_Products_List.xlsx`
- **"It's not working!"** → Run `check_paths.py` first

### More help:
- Read: `SCENARIO_QUICK_REFERENCE.md` (cheat sheet)
- Read: `SETUP_AND_RUN_GUIDE.md` (complete guide)
- Check: `PATH_FIX_EXPLAINED.md` (if errors about paths)

---

## 🎊 You're All Set!

You now have:
- ✅ Fixed employment analysis script
- ✅ Scenario generation tools
- ✅ Example scenarios ready to test
- ✅ Complete documentation
- ✅ Product and region reference lists
- ✅ Positron IDE compatibility

**Next: Run `check_paths.py` to verify, then start your analysis!**

Good luck with your dissertation! 🚀📊🎓
