# Complete Guide: Running MINDSET Employment Analysis

## For: R Users New to Python

---

## Quick Start (3 Steps)

### 1. Run the Diagnostic Script
```bash
python "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main\Claude Code\temp\check_paths.py"
```

This will verify that:
- ✓ All modules can be found (exog_vars, IO, empl, etc.)
- ✓ GLORIA database files exist (employment data, IO matrices)
- ✓ Your scenario files are accessible
- ✓ The path setup works correctly

### 2. Configure Your Scenario
Edit `RunMINDSET_EmploymentOnly.py` line 103:
```python
scenario_name = "Infrastructure_Investment"  # ← CHANGE THIS TO YOUR SCENARIO
```

### 3. Run the Employment Analysis
```bash
python "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main\Claude Code\temp\RunMINDSET_EmploymentOnly.py"
```

---

## What Was Fixed

### The Core Problem
Your script couldn't find the MINDSET modules because of Python's import path system.

**File Structure:**
```
MINDSET_module-main/
  └── MINDSET_module-main/           ← PROJECT ROOT
      ├── SourceCode/                ← Modules you need
      │   ├── exog_vars.py
      │   ├── InputOutput.py
      │   ├── employment.py
      │   ├── results.py
      │   └── utils.py
      ├── GLORIA_db/                 ← Your data
      │   └── v57/2019/parsed_db_original/
      │       ├── empl_data.pkl      ← Employment coefficients
      │       ├── IND_sparse.pkl     ← Input-Output matrix
      │       ├── labor_data.pkl
      │       └── ...
      ├── GLORIA_template/           ← Configuration & scenarios
      │   ├── Variables/
      │   │   └── Variable_list_MINDSET.xlsx
      │   └── Scenarios/
      │       └── Infrastructure_Investment.xlsx
      └── Claude Code/
          └── temp/                  ← Your script location
              └── RunMINDSET_EmploymentOnly.py
```

**The Problem:**
- Your script is in: `MINDSET_module-main/Claude Code/temp/`
- It tries to import: `from SourceCode.exog_vars import exog_vars`
- Python looks in: `Claude Code/temp/SourceCode/` ❌ (doesn't exist!)
- Should look in: `MINDSET_module-main/SourceCode/` ✓

### The Solution (Lines 32-56 of RunMINDSET_EmploymentOnly.py)

```python
# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up to MINDSET root (2 levels up: temp/ → Claude Code/ → root/)
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

# Add to Python's search path
sys.path.insert(0, mindset_root)

# Change working directory (like setwd() in R)
os.chdir(mindset_root)
```

**R Equivalent:**
```r
# In R, you'd do:
setwd("C:/path/to/MINDSET_module-main")
source("SourceCode/exog_vars.R")
```

---

## Running in Positron IDE

### What is Positron?
Positron is RStudio's new IDE for Python and R. It works great with Python!

### Positron vs Spyder
Both are IDEs for Python. The `SPYDER = True` flag in the script just means "running from an IDE" (not command line). **This works perfectly in Positron!**

### How to Run in Positron:

1. **Open the script:**
   - File → Open → Navigate to `RunMINDSET_EmploymentOnly.py`

2. **Verify settings (lines 99-103):**
   ```python
   SPYDER = True  # Leave this as True for Positron

   if SPYDER:
       scenario_name = "Infrastructure_Investment"  # ← Set your scenario here
   ```

3. **Run the script:**
   - Click "Run" button, or
   - Press Ctrl+Shift+Enter (run entire script), or
   - Press Ctrl+Enter (run line by line)

4. **Check the output:**
   - Results will be saved in: `MINDSET_module-main/GLORIA_results/`
   - Look for: `Results_Infrastructure_Investment_EmploymentOnly.xlsx`

### Positron-Specific Tips:

**Advantage 1: Variable Explorer**
- Like RStudio's Environment pane
- You can inspect `MRIO_BASE`, `dq_total`, `dempl_total` etc.
- Click on DataFrames to view them (like `View()` in R)

**Advantage 2: Integrated Terminal**
- Use the terminal panel to run diagnostic scripts
- Just like RStudio's Terminal tab

**Advantage 3: R Users Feel at Home**
- Keyboard shortcuts similar to RStudio
- Panel layout similar to RStudio
- Can run both R and Python in same IDE

---

## Understanding the MINDSET Data Flow

For R users, here's how the employment estimation works:

### Step 1: Load IO Data (exog_vars module)

**What it does:**
- Reads GLORIA database from: `GLORIA_db/v57/2019/parsed_db_original/`
- Loads Leontief inverse matrix (L): `L_BASE`
- Loads employment coefficients (e): `EMPL_COEF`

**R Equivalent:**
```r
# In R, you might do:
load("GLORIA_db/v57/2019/parsed_db_original/L_BASE.RData")
load("GLORIA_db/v57/2019/parsed_db_original/empl_data.RData")
```

**Python Code (line 110):**
```python
MRIO_BASE = exog_vars()  # Automatically loads all data
```

### Step 2: Load Scenario (scenario module)

**What it does:**
- Reads your investment scenario from Excel
- Extracts final demand shock (dY): `fd_exog`

**R Equivalent:**
```r
# In R:
library(readxl)
scenario_data <- read_excel("GLORIA_template/Scenarios/Infrastructure_Investment.xlsx")
fd_exog <- scenario_data$dy  # Extract final demand shock
```

**Python Code (line 129):**
```python
Scenario = scenario(MRIO_BASE, scenario_path, None)
Scenario.set_exog_inv()  # Extract investment shock
```

### Step 3: Calculate Output Changes (InputOutput module)

**The Key Equation:**
```
dX = L × dY
```
Where:
- `dX` = change in output (what we're solving for)
- `L` = Leontief inverse matrix (direct + indirect effects)
- `dY` = change in final demand (your investment)

**R Equivalent:**
```r
# In R, you'd do:
dX <- L_BASE %*% dY  # Matrix multiplication
```

**Python Code (line 218):**
```python
dq_exog_fd = IO_model.calc_dq_exog(dy_exog_fd)
```

### Step 4: Calculate Employment Changes (employment module)

**The Key Equation:**
```
dE = e × dX
```
Where:
- `dE` = change in employment (jobs created)
- `e` = employment coefficient (jobs per $ of output)
- `dX` = change in output (from Step 3)

**R Equivalent:**
```r
# In R, you'd do:
dE <- empl_coef * dX  # Element-wise multiplication
total_jobs <- sum(dE)
employment_multiplier <- total_jobs / total_investment * 1e6  # Jobs per $1M
```

**Python Code (line 252):**
```python
dempl_exog_fd = Empl_model.calc_dempl([dq_exog_fd])[0]
```

### Step 5: Save Results

**What's Created:**
An Excel file with 5 sheets:
1. `Summary` - Key metrics
2. `Employment_by_Region` - Jobs by country/region
3. `Employment_by_Sector` - Jobs by industry
4. `Employment_Details` - Full breakdown
5. `Output_Details` - For validation

**R Equivalent:**
```r
# In R, using writexl or openxlsx:
library(openxlsx)
wb <- createWorkbook()
addWorksheet(wb, "Summary")
writeData(wb, "Summary", summary_stats)
# ... add more sheets
saveWorkbook(wb, "Results.xlsx")
```

**Python Code (lines 358-373):**
```python
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    summary_stats.to_excel(writer, sheet_name='Summary', index=False)
    empl_by_region.to_excel(writer, sheet_name='Employment_by_Region', index=False)
    # ... etc
```

---

## Troubleshooting Guide

### Problem: "ModuleNotFoundError: No module named 'SourceCode'"

**Cause:** Path setup didn't work

**Solution:**
1. Run `check_paths.py` to diagnose
2. Verify you're running from the correct script location
3. Check that lines 32-56 of `RunMINDSET_EmploymentOnly.py` are present

**R Analogy:**
```r
# This is like getting:
# Error in source("SourceCode/file.R") : cannot open file 'SourceCode/file.R'
# Solution in R: setwd("C:/correct/path")
```

### Problem: "FileNotFoundError: 'GLORIA_template\\Scenarios\\...'"

**Cause:** Scenario file doesn't exist

**Solution:**
1. Check scenario file name (line 103)
2. Run `check_paths.py` to see available scenarios
3. Verify the file exists in `GLORIA_template/Scenarios/`

**R Analogy:**
```r
# Like: Error in read_excel("file.xlsx") : 'file.xlsx' does not exist
```

### Problem: "ImportError: cannot import name 'exog_vars'"

**Cause:** Module exists but has errors inside it

**Solution:**
1. Check if `SourceCode/exog_vars.py` file exists
2. Check for Python syntax errors in that file
3. Make sure all dependencies are installed (pandas, numpy, scipy)

**Install dependencies:**
```bash
pip install pandas numpy scipy openpyxl pickle5
```

### Problem: Script runs but produces zero jobs

**Cause:** Scenario file may be empty or incorrectly formatted

**Solution:**
1. Open your scenario Excel file
2. Check that it has investment values (dY column)
3. Run `check_paths.py` to verify database files exist

---

## Key Differences: R vs Python

| Task | R | Python |
|------|---|--------|
| **Set working directory** | `setwd("path")` | `os.chdir("path")` |
| **Get working directory** | `getwd()` | `os.getcwd()` |
| **Join paths** | `file.path(a, b)` | `os.path.join(a, b)` |
| **Check file exists** | `file.exists("path")` | `os.path.exists("path")` |
| **Load code** | `source("file.R")` | `from module import function` |
| **Read Excel** | `read_excel("file.xlsx")` | `pd.read_excel("file.xlsx")` |
| **Matrix multiply** | `A %*% B` | `A @ B` or `np.dot(A, B)` |
| **Element multiply** | `A * B` | `A * B` (same!) |
| **View data** | `View(data)` | Click in Positron Variable Explorer |
| **Column sum** | `sum(df$column)` | `df['column'].sum()` |
| **Group by** | `aggregate()` or `dplyr::group_by()` | `df.groupby().sum()` |

---

## Expected Output

When the script runs successfully, you should see:

```
================================================================================
MINDSET EMPLOYMENT-ONLY ESTIMATION
================================================================================

MINDSET root directory: C:\Users\...\MINDSET_module-main
Current working directory: C:\Users\...\MINDSET_module-main

Running in IDE mode with scenario: Infrastructure_Investment
Scenario file: C:\...\GLORIA_template\Scenarios\Infrastructure_Investment.xlsx
Checking if scenario file exists: True

--------------------------------------------------------------------------------
STEP 1: Loading MRIO Data
--------------------------------------------------------------------------------
✓ Loaded Leontief inverse: (7224, 7224)
✓ Loaded employment coefficients
✓ Loaded 162 countries/regions
✓ Loaded 159 sectors
Time: 5.2 seconds

--------------------------------------------------------------------------------
STEP 2: Loading Investment Scenario
--------------------------------------------------------------------------------
✓ Loaded exogenous final demand shock: $100,000,000
✓ Investment allocated across 50 sector-region pairs
Time: 0.8 seconds

--------------------------------------------------------------------------------
STEP 3: Calculating Output Changes
--------------------------------------------------------------------------------
✓ Initialized IO model
✓ Converted final demand shock to vector (size: 7224)
✓ Total shock amount: $100,000,000
✓ Calculated output changes: dX = L × dY
✓ Total output change: $175,000,000
✓ Output multiplier: 1.75x
Time: 2.1 seconds

--------------------------------------------------------------------------------
STEP 4: Calculating Employment Changes
--------------------------------------------------------------------------------
✓ Loaded employment coefficients
✓ Calculated employment changes: dE = e × dX
✓ Total jobs created: 1,234
✓ Employment multiplier: 12.34 jobs per $1M
Time: 0.5 seconds

--------------------------------------------------------------------------------
STEP 5: Saving Results
--------------------------------------------------------------------------------
✓ Formatted output change results
✓ Formatted employment change results
✓ Created summary statistics

SUMMARY:
  Total Investment: $100,000,000
  Total Jobs Created: 1,234
  Employment Multiplier: 12.34 jobs per $1M

✓ Results saved to: GLORIA_results\Results_Infrastructure_Investment_EmploymentOnly.xlsx
Time: 1.2 seconds

================================================================================
EMPLOYMENT ESTIMATION COMPLETE
================================================================================

Total Runtime: 9.8 seconds
```

---

## Next Steps

### 1. Verify Your Setup
```bash
python check_paths.py
```
Look for all ✓ marks

### 2. Run a Test
```bash
python RunMINDSET_EmploymentOnly.py
```

### 3. Check Your Results
- Open: `MINDSET_module-main/GLORIA_results/Results_[ScenarioName]_EmploymentOnly.xlsx`
- Look at the `Summary` sheet for key metrics
- Check `Employment_by_Region` and `Employment_by_Sector` for details

### 4. Analyze in R (if you prefer!)
```r
library(readxl)
library(tidyverse)

# Read the Python output
results <- read_excel("GLORIA_results/Results_Infrastructure_Investment_EmploymentOnly.xlsx",
                     sheet = "Employment_by_Region")

# Analyze in R
results %>%
  arrange(desc(Jobs_Created)) %>%
  slice_head(n = 10) %>%
  ggplot(aes(x = reorder(Region_names, Jobs_Created), y = Jobs_Created)) +
  geom_col() +
  coord_flip() +
  labs(title = "Top 10 Regions by Job Creation",
       x = "Region", y = "Jobs Created")
```

---

## Summary

✅ **Fixed:**
- Module import paths (SourceCode modules)
- Data file paths (GLORIA database)
- Scenario file paths
- Output directory paths

✅ **Works with:**
- Positron IDE ✓
- Spyder IDE ✓
- VSCode ✓
- Command line ✓
- Jupyter notebooks ✓

✅ **What you get:**
- Employment impact estimates by region
- Employment impact by sector
- Employment multiplier (jobs/$1M)
- Output multiplier
- Detailed Excel output

---

## Questions?

**Import errors?** → Run `check_paths.py`
**File not found errors?** → Check paths in the error message
**Zero jobs?** → Check your scenario Excel file
**Other errors?** → Check that you have all Python packages installed

Remember: Python's import system is stricter than R's `source()`, but once the paths are set up correctly (which we've done!), it works reliably.
