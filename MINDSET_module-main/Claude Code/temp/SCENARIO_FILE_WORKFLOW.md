# Scenario File Workflow - Complete Guide

## CRITICAL POINT

**The code does NOT automatically create or fill scenario files.**

**YOU must manually create the scenario file BEFORE running the analysis.**

---

## What Gets Filled Automatically vs. Manually

| Item | Automatic? | Where Configured |
|------|-----------|------------------|
| **Scenario file creation** | ❌ **MANUAL** | You create Excel file |
| **Investment amounts** | ❌ **MANUAL** | You fill in "Investment by" sheet |
| **Countries in scenario** | ❌ **MANUAL** | You specify in scenario file |
| **Sectors in scenario** | ❌ **MANUAL** | You specify in scenario file |
| **Countries in analysis** | ✅ Automatic | Variable_list_MINDSET_SSP.xlsx (R sheet) |
| **Reading scenario file** | ✅ Automatic | Code reads your file at line 118 |
| **Processing ranges** | ✅ Automatic | Code expands "1-10" or "ALL" |
| **Converting to demand** | ✅ Automatic | Investment module (lines 190-202) |

---

## Complete Workflow

### PHASE 1: One-Time Setup (Already Done)

✓ Variable_list_MINDSET_SSP.xlsx configured with your countries
✓ exog_vars_SSP.py created to load custom variable list
✓ RunMINDSET_EmploymentOnly.py configured

### PHASE 2: For Each Analysis (YOU MUST DO THIS)

#### Step 1: Create Scenario File

**Method A: Copy existing template (if available)**
```
1. Navigate to: GLORIA_template\Scenarios\
2. Look for: "New template.xlsx" or similar
3. Copy it
4. Rename to: Infrastructure_Investment.xlsx (or your chosen name)
```

**Method B: Use the creator script (if no template)**
```
1. Run: CREATE_SCENARIO_FILE.py (in Claude Code/temp/)
2. This creates: GLORIA_template\Scenarios\Infrastructure_Investment.xlsx
```

#### Step 2: Fill in Your Investment Data

**Open the Excel file and go to "Investment by" sheet:**

Row 16+ (after column headers at row 15):

| Country ISO* | Sector investing code* | Value* | Type* |
|--------------|------------------------|---------|-------|
| USA          | 56                     | 100000000 | abs-b |

**Where to find codes:**
- **Country codes:** See Variable_list_MINDSET_SSP.xlsx (R sheet) or GLORIA_Regions_Reference.xlsx
- **Sector codes:** See GLORIA_Products_Reference.xlsx
  - Product 56 = Construction
  - Product 1-120 = All sectors

**Examples:**

**Single sector:**
```
USA | 56 | 100000000 | abs-b
```

**Multiple sectors (manual entry):**
```
USA | 56 | 100000000 | abs-b
USA | 57 | 50000000  | abs-b
USA | 58 | 75000000  | abs-b
```

**Range shortcut (code expands automatically):**
```
USA | 1-10 | 10000000 | abs-b
```
Code expands this to 10 rows (sectors 1, 2, 3... 10), each getting $1M proportionally.

**All sectors (code expands automatically):**
```
USA | ALL | 120000000 | abs-b
```
Code expands to 120 rows, spreading $120M across all sectors proportionally.

**Multiple countries:**
```
USA | 56 | 100000000 | abs-b
CHN | 56 | 100000000 | abs-b
BRA | 56 | 100000000 | abs-b
```

#### Step 3: Save the File

Save as: `GLORIA_template\Scenarios\Infrastructure_Investment.xlsx`

#### Step 4: Update Script

In `RunMINDSET_EmploymentOnly.py` line 104:
```python
scenario_name = "Infrastructure_Investment"  # ← Must match your filename (without .xlsx)
```

#### Step 5: Run Analysis

In Positron:
- **Option A:** Run entire script: Ctrl+Shift+Enter
- **Option B:** Run line by line: Ctrl+Enter

---

## What Happens When You Run the Script

### Line 118: Build File Path
```python
scenario_path = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios", f"{scenario_name}.xlsx")
```
**Result:** Looks for `GLORIA_template\Scenarios\Infrastructure_Investment.xlsx`

### Line 121: Check File Exists
```python
print(f"Checking if scenario file exists: {os.path.exists(scenario_path)}")
```
**If file doesn't exist:** Script will fail at line 326 when trying to read it

### Line 177 (via scenario.py line 326): Read Your Data
```python
inv_exog = pd.read_excel(self.scenario_file, sheet_name='Investment by', skiprows=14)
```
**Result:** Reads rows 16+ from your Excel file

### Lines 346-351: Process Ranges/ALL
```python
inv_exog = resolve_comma(inv_exog, "REG_imp")
inv_exog = resolve_all(inv_exog, "REG_imp", self.REGIONS['Region_acronyms'].to_list())
inv_exog = resolve_comma(inv_exog, "PROD_COMM")
inv_exog = resolve_hyphen(inv_exog, "PROD_COMM")
inv_exog = resolve_all(inv_exog, "PROD_COMM", [x for x in np.arange(1,121)])
```

**What this does:**
- `resolve_comma`: Expands "USA,CHN,BRA" into 3 separate rows
- `resolve_hyphen`: Expands "1-10" into sectors 1,2,3...10
- `resolve_all`: Expands "ALL" into all 120 sectors or all countries

**Example expansion:**

**Your input (1 row):**
```
USA | 1-10 | 10000000 | abs-b
```

**After processing (10 rows):**
```
USA | 1  | 1000000 | abs-b
USA | 2  | 1000000 | abs-b
USA | 3  | 1000000 | abs-b
...
USA | 10 | 1000000 | abs-b
```

---

## Common Scenarios to Create

### Scenario 1: Test Single Sector

**File:** `Test_Construction_USA.xlsx`

**Investment by sheet (row 16):**
```
Country ISO* | Sector investing code* | Value*    | Type*
USA          | 56                     | 100000000 | abs-b
```

**Purpose:** Test $100M in construction

---

### Scenario 2: Compare All Sectors

**File:** `All_Sectors_1M_USA.xlsx`

**Investment by sheet (row 16):**
```
Country ISO* | Sector investing code* | Value*    | Type*
USA          | 1-120                  | 120000000 | abs-b
```

OR manually list all 120:
```
USA | 1   | 1000000 | abs-b
USA | 2   | 1000000 | abs-b
...
USA | 120 | 1000000 | abs-b
```

**Purpose:** $1M in each sector, compare employment multipliers

---

### Scenario 3: Cross-Country Comparison

**File:** `Construction_MultiCountry.xlsx`

**Investment by sheet (row 16+):**
```
Country ISO* | Sector investing code* | Value*    | Type*
USA          | 56                     | 100000000 | abs-b
CHN          | 56                     | 100000000 | abs-b
BRA          | 56                     | 100000000 | abs-b
IND          | 56                     | 100000000 | abs-b
DEU          | 56                     | 100000000 | abs-b
```

**Purpose:** Compare construction employment multipliers across countries

---

### Scenario 4: Infrastructure Portfolio

**File:** `Infrastructure_Portfolio.xlsx`

**Investment by sheet (row 16+):**
```
Country ISO* | Sector investing code* | Value*     | Type*
USA          | 56                     | 500000000  | abs-b   (Construction)
USA          | 55                     | 200000000  | abs-b   (Utilities)
USA          | 59                     | 150000000  | abs-b   (Transportation)
USA          | 63                     | 150000000  | abs-b   (Communications)
```

**Purpose:** Realistic mixed infrastructure investment

---

## Types Explained

### Type: "abs-b" (Most Common)

**Meaning:** Absolute value, proportional to base

**Use when:** You specify exact dollar amounts

**How it works:**
- If you specify multiple sectors with same value, they each get that amount
- If you use ranges (1-10), the total is split proportionally based on base IO table

**Example:**
```
USA | 1-10 | 10000000 | abs-b
```
The $10M is split across sectors 1-10 proportional to their baseline final demand.

### Type: "abs" (Advanced)

**Meaning:** Absolute value, proportional to current state

**Use when:** Dynamic/multi-period models (not typical for employment-only)

### Type: "rel" (Advanced)

**Meaning:** Relative change (percentage)

**Example:**
```
USA | 56 | 0.10 | rel
```
Would mean: 10% increase in construction investment

**Note:** May require baseline investment data

---

## Troubleshooting

### Error: "Checking if scenario file exists: False"

**Problem:** File not found

**Solutions:**
1. Check filename matches (case-sensitive on some systems)
2. Check file is in correct directory: `GLORIA_template\Scenarios\`
3. Check file extension is `.xlsx`
4. Check `scenario_name` variable matches filename (without .xlsx)

### Error: "ValueError: Worksheet named 'Investment by' not found"

**Problem:** Sheet name is wrong

**Solutions:**
1. Open Excel file
2. Check sheet is named exactly: "Investment by" (with space)
3. Not: "Investment_by" or "Investment-by" or "Investment By"

### Error: "KeyError: 'Country ISO*'"

**Problem:** Column headers missing or wrong

**Solutions:**
1. Row 15 must have headers with asterisks:
   - Country ISO*
   - Sector investing code*
   - Value*
   - Type*
2. Headers must end with asterisk (*)
3. Must be at row 15 (code skips first 14 rows)

### Warning: "No exogenous investment found"

**Problem:** Sheet is empty or data not starting at row 16

**Solutions:**
1. Add data starting at row 16 (after headers at row 15)
2. Ensure cells are not empty
3. Ensure Value column has numbers, not text

---

## Summary: What YOU Must Do

| Step | Action | Tool |
|------|--------|------|
| 1. Create/copy scenario file | **MANUAL** | Excel or Python script |
| 2. Fill in countries | **MANUAL** | Excel |
| 3. Fill in sectors | **MANUAL** | Excel |
| 4. Fill in investment amounts | **MANUAL** | Excel |
| 5. Save file | **MANUAL** | Excel |
| 6. Set scenario_name in script | **MANUAL** | Python/Positron |
| 7. Run script | **MANUAL** | Positron (Ctrl+Shift+Enter) |

**Everything else (reading, processing, converting, calculating) is automatic.**

---

## R User Equivalent

In R, this would be like:

```r
# You create the scenario file
library(writexl)

# Create your investment scenario manually
investment <- data.frame(
  Country_ISO = c("USA", "CHN", "BRA"),
  Sector = c(56, 56, 56),
  Value = c(100000000, 100000000, 100000000),
  Type = c("abs-b", "abs-b", "abs-b")
)

# Save to Excel
write_xlsx(investment, "GLORIA_template/Scenarios/Infrastructure.xlsx")

# Then run the model (code reads your file)
source("RunMINDSET_EmploymentOnly.R")
```

**Key point:** YOU create the `investment` data frame. The code doesn't do it for you.

---

## Next Steps

1. **Create your first scenario file:**
   - Run `CREATE_SCENARIO_FILE.py` OR
   - Copy template if it exists

2. **Fill in simple test data:**
   - Country: USA
   - Sector: 56 (Construction)
   - Value: 100000000
   - Type: abs-b

3. **Run the analysis:**
   - Set `scenario_name = "Infrastructure_Investment"`
   - Press Ctrl+Shift+Enter

4. **Check results:**
   - Output in: `GLORIA_results/Infrastructure_Investment_[timestamp]/`
   - Look at Summary sheet first

5. **Create more scenarios for dissertation:**
   - All sectors comparison
   - Cross-country comparison
   - Infrastructure portfolio analysis

---

**Remember: The scenario file is YOUR input to the model. The code processes it, but doesn't create it.**
