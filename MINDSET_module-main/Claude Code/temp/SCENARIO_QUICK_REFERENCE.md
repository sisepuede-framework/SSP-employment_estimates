# MINDSET Scenario Quick Reference

## For R Users: The Essentials

### Concept Map

| R | MINDSET |
|---|---------|
| Your shock data.frame | Excel "Final demand" sheet |
| `country` column | "Producing country ISO*" & "Consuming country ISO*" |
| `product` column | "Product code*" (1-120) |
| `shock_amount` column | "Value*" (in USD) |
| `read.csv("scenarios.csv")` | Excel file in `GLORIA_template/Scenarios/` |
| Loop through scenarios | Change `scenario_name` and re-run |

---

## Quick Start (3 Steps)

### 1. Generate Template & Examples
```bash
cd "Claude Code/temp"
python create_scenario_template.py
```

**What you get:**
- ✓ `Scenario_Template.xlsx` - Empty template
- ✓ `GLORIA_Products_List.xlsx` - 120 products reference
- ✓ `GLORIA_Regions_List.xlsx` - 162 regions reference
- ✓ 3 example scenarios ready to use

### 2. Create Your Scenario

**Option A: Use the script (Recommended!)**
```bash
# $1M to each of 120 products
python generate_custom_scenario.py --mode all_products --amount 1000000 --country USA

# $100M to construction sector only
python generate_custom_scenario.py --mode specific_products --products "56" --amount 100000000 --country USA

# Compare 5 countries
python generate_custom_scenario.py --mode multi_country --countries "USA,CHN,DEU,BRA,IND" --product 56 --amount 100000000
```

**Option B: Edit Excel manually**
- Open `Scenario_Template.xlsx`
- Delete rows 16-19 (examples)
- Add your data starting at row 16
- Save as: `GLORIA_template/Scenarios/YourScenarioName.xlsx`

### 3. Run Employment Analysis
```python
# In RunMINDSET_EmploymentOnly.py line 103:
scenario_name = "YourScenarioName"  # Without .xlsx extension

# Then run:
python RunMINDSET_EmploymentOnly.py
```

---

## Excel File Structure

### Required Columns (Row 15)

| Column | What to Put | Example |
|--------|-------------|---------|
| **Producing country ISO*** | Country making the product | USA, CHN, BRA, ALL |
| **Consuming country ISO*** | Country buying/using it | USA, CHN, BRA, ALL |
| **Product code*** | Product number 1-120 | 56, 1-10, 1,5,10, ALL |
| **FD code*** | Final demand type | FD_4 (investment) |
| **Value*** | Dollar amount | 100000000 |
| **Type*** | Value type | abs-b |

### Your Data (Row 16+)

```
Row 1-14:  Header info (don't change)
Row 15:    Column names (don't change)
Row 16:    Your first shock
Row 17:    Your second shock
...
Row N:     Your last shock
```

---

## Common Scenarios

### Scenario 1: Test All Products Individually

**Goal:** Employment multiplier for each of 120 products

**Method:**
```bash
python generate_custom_scenario.py --mode all_products --amount 1000000 --country USA
```

**Result:** One file, 120 rows, $1M each
- Run once
- Get 120 employment multipliers in one Excel output
- Compare across products

### Scenario 2: Focus on Specific Sectors

**Goal:** Compare construction vs manufacturing vs agriculture

**Method:**
```bash
# Construction (product 56)
python generate_custom_scenario.py --mode specific_products --products "56" --amount 100000000 --country USA --name "Construction_100M"

# Manufacturing (products 20-40)
python generate_custom_scenario.py --mode product_range --range "20-40" --amount 100000000 --country USA --name "Manufacturing_100M"

# Agriculture (products 1-15)
python generate_custom_scenario.py --mode product_range --range "1-15" --amount 100000000 --country USA --name "Agriculture_100M"
```

**Result:** 3 files
- Run 3 times (change scenario_name each time)
- Compare results across sectors

### Scenario 3: Country Comparison

**Goal:** How does $100M in USA vs China create jobs?

**Method:**
```bash
python generate_custom_scenario.py --mode multi_country --countries "USA,CHN,DEU,BRA,IND" --product 56 --amount 100000000
```

**Result:** One file, 5 rows
- Run once
- Compare employment across countries

---

## Special Codes Cheat Sheet

### Product Codes

| Code | Means |
|------|-------|
| `56` | Product 56 (Construction) |
| `1-10` | Products 1 through 10 |
| `1,5,10` | Products 1, 5, and 10 |
| `ALL` | All 120 products (proportional split) |

### Country Codes

| Code | Country |
|------|---------|
| `USA` | United States |
| `CHN` | China |
| `DEU` | Germany |
| `BRA` | Brazil |
| `IND` | India |
| `GBR` | United Kingdom |
| `JPN` | Japan |
| `ALL` | All countries (proportional split) |

**See:** `GLORIA_Regions_List.xlsx` for all 162 regions

### Final Demand Codes

| Code | Category | Use When |
|------|----------|----------|
| `FD_1` | Household consumption | Consumer demand shock |
| `FD_3` | Government spending | Public sector shock |
| `FD_4` | Investment | Infrastructure/capital (**Recommended**) |

### Type Codes

| Code | Meaning | Use When |
|------|---------|----------|
| `abs-b` | Absolute dollar amount | You know exact dollar value (**Recommended**) |
| `rel-b` | Relative % change | You want % increase (0.10 = 10%) |

---

## Command Line Cheat Sheet

```bash
# Navigate to temp folder
cd "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main\Claude Code\temp"

# Generate templates and examples
python create_scenario_template.py

# Generate custom scenario - all products
python generate_custom_scenario.py --mode all_products --amount 1000000 --country USA

# Generate custom scenario - specific products
python generate_custom_scenario.py --mode specific_products --products "1,5,10,56" --amount 5000000 --country CHN

# Generate custom scenario - product range
python generate_custom_scenario.py --mode product_range --range "1-20" --amount 10000000 --country DEU

# Generate custom scenario - multi-country
python generate_custom_scenario.py --mode multi_country --countries "USA,CHN,DEU" --product 56 --amount 100000000

# Run employment analysis
python RunMINDSET_EmploymentOnly.py
```

---

## Workflow Summary

```
1. Create Scenario
   ├─→ Use generate_custom_scenario.py (easy)
   └─→ Or edit Scenario_Template.xlsx (manual)

2. Verify File
   └─→ Check it's in: GLORIA_template/Scenarios/

3. Update Script
   └─→ Line 103: scenario_name = "YourName"

4. Run Analysis
   └─→ python RunMINDSET_EmploymentOnly.py

5. Check Results
   └─→ GLORIA_results/Results_YourName_EmploymentOnly.xlsx
```

---

## Troubleshooting

### "No exogenous final demand found"
- ✓ Check file is in `GLORIA_template/Scenarios/`
- ✓ Check sheet named exactly "Final demand"
- ✓ Check data starts at row 16
- ✓ Check row 15 has exact column names (with *)

### "FileNotFoundError"
- ✓ Check scenario_name matches filename (without .xlsx)
- ✓ Run from correct directory
- ✓ Check path setup in script (lines 32-56)

### Zero jobs created
- ✓ Check Value* column has numbers (not text)
- ✓ Check Type* is "abs-b" (not blank)
- ✓ Check Product code* is valid (1-120)

---

## Examples Gallery

### Example 1: Single Product, Single Country
```
USA → USA → Product 56 → FD_4 → $100,000,000 → abs-b
```
**Result:** Employment from $100M construction investment in USA

### Example 2: Multiple Products, Single Country
```
USA → USA → 1 → FD_4 → $1,000,000 → abs-b
USA → USA → 2 → FD_4 → $1,000,000 → abs-b
...
USA → USA → 120 → FD_4 → $1,000,000 → abs-b
```
**Result:** Compare employment multipliers across all 120 products

### Example 3: Single Product, Multiple Countries
```
USA → USA → 56 → FD_4 → $100,000,000 → abs-b
CHN → CHN → 56 → FD_4 → $100,000,000 → abs-b
DEU → DEU → 56 → FD_4 → $100,000,000 → abs-b
```
**Result:** Compare employment across countries for same investment

### Example 4: Using "ALL"
```
USA → USA → ALL → FD_4 → $100,000,000 → abs-b
```
**Result:** $100M spread proportionally across all 120 products based on baseline

---

## Files Created by Scripts

### create_scenario_template.py
1. `Scenario_Template.xlsx` - Your starting point
2. `GLORIA_Products_List.xlsx` - Product reference (1-120)
3. `GLORIA_Regions_List.xlsx` - Country reference (162)
4. `Example_1M_Per_Product.xlsx` - Test all products
5. `Example_Construction_100M.xlsx` - Single sector
6. `Example_MultiCountry_Comparison.xlsx` - Cross-country

### generate_custom_scenario.py
- Creates custom scenario in `GLORIA_template/Scenarios/`
- Automatically names file based on your inputs
- Ready to use immediately!

---

## R Users: Translation Guide

### Creating Scenarios

**R approach:**
```r
scenarios <- list(
  construction = data.frame(country="USA", product=56, amount=1e8),
  agriculture = data.frame(country="USA", product=1:15, amount=1e7),
  multi_country = data.frame(country=c("USA","CHN"), product=56, amount=1e8)
)

for (s in names(scenarios)) {
  write.csv(scenarios[[s]], paste0("scenario_", s, ".csv"))
}
```

**MINDSET approach:**
```bash
python generate_custom_scenario.py --mode specific_products --products "56" --amount 100000000 --country USA --name "Construction"
python generate_custom_scenario.py --mode product_range --range "1-15" --amount 10000000 --country USA --name "Agriculture"
python generate_custom_scenario.py --mode multi_country --countries "USA,CHN" --product 56 --amount 100000000 --name "MultiCountry"
```

### Running Multiple Scenarios

**R approach:**
```r
results <- list()
for (scenario_name in names(scenarios)) {
  results[[scenario_name]] <- run_io_model(scenarios[[scenario_name]])
}
```

**MINDSET approach:**
```bash
# Edit line 103 each time:
scenario_name = "Construction"   # Run 1
scenario_name = "Agriculture"    # Run 2
scenario_name = "MultiCountry"   # Run 3

# Or create a loop script (advanced)
```

---

## Quick Links

📄 **Full Guide:** `SCENARIO_FILE_GUIDE.md`
📄 **Setup Guide:** `SETUP_AND_RUN_GUIDE.md`
📄 **Positron Guide:** `POSITRON_QUICKSTART.md`
📄 **Path Debugging:** `PATH_FIX_EXPLAINED.md`

---

## Summary

✅ **What you need to know:**
1. Scenarios = Excel files in `GLORIA_template/Scenarios/`
2. Use scripts to generate scenarios (easier than manual)
3. One scenario = one run of employment script
4. Results saved to `GLORIA_results/`

✅ **Most common command:**
```bash
python generate_custom_scenario.py --mode all_products --amount 1000000 --country USA
```

✅ **Then:**
```python
scenario_name = "AllProducts_1M_USA"  # In script line 103
python RunMINDSET_EmploymentOnly.py
```

**That's it!** 🎉
