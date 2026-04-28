# Beginner's Guide: Running Python Scripts in Positron

**For R users who are new to Python**

---

## The Basics: Python vs R

### Running Scripts

| R | Python |
|---|--------|
| `source("script.R")` | `python script.py` (in terminal) |
| Select code + Ctrl+Enter | Select code + Ctrl+Enter (same!) |
| Run whole script: Ctrl+Shift+Enter | Run whole script: Ctrl+Shift+Enter (same!) |

**Good news:** Positron works EXACTLY like RStudio for running code!

---

## Method 1: Run in Positron (EASIEST - Recommended!)

### Step 1: Open the Script
1. In Positron, click **File → Open File**
2. Navigate to: `Claude Code\temp\SIMPLE_SCENARIO_CREATOR.py`
3. The script opens in the editor (like opening .R file)

### Step 2: Run the Script
**Option A:** Press **Ctrl + Shift + Enter** (runs entire script)
**Option B:** Click the **Run** button (top-right of editor)

### Step 3: Check Output
- Look at the **Console** panel (bottom of Positron)
- You should see messages starting with "SIMPLE SCENARIO CREATOR"
- Look for ✓ marks (means success)
- Look for ✗ marks (means error - read the message)

### Step 4: Check Files Created
- Use **Files** panel in Positron (right side)
- Navigate to `Claude Code/temp/`
- You should see:
  - `GLORIA_Products_Reference.xlsx`
  - `GLORIA_Regions_Reference.xlsx`
  - `SCENARIO_TEMPLATE_SIMPLE.xlsx`

**That's it!** Much easier than terminal, right?

---

## Method 2: Run in Terminal (Alternative)

If Method 1 doesn't work, try this:

### Step 1: Open Terminal in Positron
- Click **Terminal** tab (bottom panel)
- Or: Menu → Terminal → New Terminal

### Step 2: Navigate to Directory
```bash
cd "Claude Code/temp"
```
(This is like `setwd()` in R)

### Step 3: Check You're in Right Place
```bash
pwd
```
Should show path ending in: `.../MINDSET_module-main/Claude Code/temp`

### Step 4: Run the Script
```bash
python SIMPLE_SCENARIO_CREATOR.py
```

---

## Common Errors & Solutions

### Error: "python: command not found"

**R equivalent:** Like getting "R not found" error

**Solution 1:** Try `python3` instead:
```bash
python3 SIMPLE_SCENARIO_CREATOR.py
```

**Solution 2:** Check Python is installed:
1. In Positron, look at bottom-right corner
2. Should say "Python 3.x"
3. If not, click it and select a Python interpreter

**Solution 3:** In Windows, try:
```bash
py SIMPLE_SCENARIO_CREATOR.py
```

### Error: "No module named 'pandas'" or "No module named 'openpyxl'"

**R equivalent:** Like "package 'dplyr' not found"

**Solution:** Install packages (like `install.packages()` in R)

In Positron terminal:
```bash
pip install pandas openpyxl numpy
```

Or if that doesn't work:
```bash
pip3 install pandas openpyxl numpy
```

Or:
```bash
python -m pip install pandas openpyxl numpy
```

### Error: "FileNotFoundError: GLORIA_template/Variables/..."

**R equivalent:** Like "cannot open file 'data.csv': No such file"

**Solution:** You're in wrong directory

In terminal:
```bash
# Check where you are
pwd

# Should show: .../MINDSET_module-main
# If not, navigate up:
cd ../..

# Then navigate to right place:
cd "Claude Code/temp"
```

**Or in Positron:** Just use Method 1 (run directly in editor) - it handles paths automatically!

### Error: Script runs but creates no files

**Solution:** Check the console output for error messages

Look for lines with ✗ marks - they tell you what went wrong

---

## Checking If It Worked

### What You Should See in Console:

```
============================================================
SIMPLE SCENARIO CREATOR
============================================================

1. Working directory: C:\Users\...\MINDSET_module-main

2. Loading GLORIA product list...
   ✓ Found 120 products

3. Loading GLORIA region list...
   ✓ Found 162 regions

4. Creating reference lists...
   ✓ Created: Claude Code/temp/GLORIA_Products_Reference.xlsx
   ✓ Created: Claude Code/temp/GLORIA_Regions_Reference.xlsx

5. Creating scenario template...
   ✓ Created: Claude Code/temp/SCENARIO_TEMPLATE_SIMPLE.xlsx

6. Creating test scenario (all 120 products)...
   ✓ Created: GLORIA_template/Scenarios/Test_AllProducts_1M_USA.xlsx
      This tests $1M in each of 120 products

7. Creating construction example...
   ✓ Created: GLORIA_template/Scenarios/Test_Construction_100M_USA.xlsx
      $100M construction investment

============================================================
SUCCESS! Files created:
============================================================
```

**If you see this:** ✅ Success! Move to next step.

**If you see errors:** ❌ Read the error message and check solutions above.

---

## What Files Were Created?

### In `Claude Code/temp/` (Reference files)

1. **GLORIA_Products_Reference.xlsx**
   - All 120 GLORIA products
   - Like a lookup table in R
   - Open it to see product codes and names

2. **GLORIA_Regions_Reference.xlsx**
   - All 162 regions/countries
   - Country codes (USA, CHN, BRA, etc.)
   - Open it to see what codes to use

3. **SCENARIO_TEMPLATE_SIMPLE.xlsx**
   - Example template with 3 rows
   - Edit this to create your own scenarios
   - Like editing a data.frame in Excel

### In `GLORIA_template/Scenarios/` (Ready to run!)

4. **Test_AllProducts_1M_USA.xlsx**
   - Tests $1M investment in EACH of 120 products
   - Ready to run immediately!
   - Perfect for your dissertation

5. **Test_Construction_100M_USA.xlsx**
   - Simple test: $100M in construction
   - Run this first to test if everything works

---

## Next Steps

### Step 1: Verify Files Exist

**In Positron Files panel:**
1. Navigate to `Claude Code/temp/`
2. You should see 3 new Excel files
3. Navigate to `GLORIA_template/Scenarios/`
4. You should see 2 new Excel files

**Can't find them?**
- Try refreshing the Files panel
- Or check Windows File Explorer

### Step 2: Test Run with Construction Example

1. **Open:** `RunMINDSET_EmploymentOnly.py`
2. **Find line 103:**
   ```python
   scenario_name = "Infrastructure_Investment"
   ```
3. **Change to:**
   ```python
   scenario_name = "Test_Construction_100M_USA"
   ```
4. **Run:** Press Ctrl+Shift+Enter
5. **Wait:** Takes 5-10 minutes
6. **Check results:** `GLORIA_results/Results_Test_Construction_100M_USA_EmploymentOnly.xlsx`

### Step 3: Run Your Full Analysis

1. **Change line 103 to:**
   ```python
   scenario_name = "Test_AllProducts_1M_USA"
   ```
2. **Run:** Press Ctrl+Shift+Enter
3. **Wait:** Takes 5-10 minutes
4. **Check results:** `GLORIA_results/Results_Test_AllProducts_1M_USA_EmploymentOnly.xlsx`
5. **Open the Excel file** - Employment_by_Sector sheet has ALL 120 products!

---

## Tips for R Users

### Python Quirks to Know

1. **Indentation matters!**
   - R: `if (x > 0) { print("positive") }`
   - Python: Indentation defines code blocks
   ```python
   if x > 0:
       print("positive")  # Must be indented!
   ```

2. **Parentheses in print**
   - R: `print("hello")` or `print "hello"`
   - Python: `print("hello")` only (parentheses required)

3. **File paths**
   - R: Can use `\` or `/`
   - Python: Use `/` or `\\` (not single `\`)
   - Best: Let script handle paths (it does!)

4. **Packages/modules**
   - R: `library(dplyr)`
   - Python: `import pandas as pd`

5. **Assignment**
   - R: `x <- 5` or `x = 5`
   - Python: `x = 5` only (no `<-`)

### But in Positron...

**Good news:** You don't need to write Python code!
- Just run the scripts I created
- Edit Excel files (like editing data in R)
- Results come out as Excel files
- Analyze in R if you want!

---

## Still Having Issues?

### Try This Diagnostic

**In Positron terminal:**

```bash
# Check Python works
python --version

# Should show: Python 3.x.x
# If not, try: python3 --version

# Check pandas works
python -c "import pandas; print('Pandas works!')"

# Should show: Pandas works!
# If error, install: pip install pandas openpyxl

# Check current directory
pwd

# Should end with: .../MINDSET_module-main
```

### Ask for Help

If still stuck, tell me:
1. What command you ran
2. What error message you see (copy-paste the exact text)
3. What the console output shows

I'll help you fix it!

---

## Summary: The Easy Way

1. ✅ Open `SIMPLE_SCENARIO_CREATOR.py` in Positron
2. ✅ Press Ctrl+Shift+Enter
3. ✅ Check console for ✓ marks
4. ✅ Open `RunMINDSET_EmploymentOnly.py`
5. ✅ Change line 103 to: `scenario_name = "Test_Construction_100M_USA"`
6. ✅ Press Ctrl+Shift+Enter
7. ✅ Wait for results!

**No terminal needed! No complicated commands! Just like running R code in RStudio!** 🎉
