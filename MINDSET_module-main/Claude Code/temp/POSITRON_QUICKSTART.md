# Positron IDE Quick Start Guide

**For R users running MINDSET Python code in Positron**

---

## Why Positron is Great for R Users

Positron is made by the RStudio team specifically to feel familiar to R users. If you know RStudio, you already know Positron!

---

## Opening and Running the Script

### 1. Open Positron
- Launch Positron IDE

### 2. Open the Script
- **File → Open File...**
- Navigate to: `Claude Code\temp\RunMINDSET_EmploymentOnly.py`

### 3. Verify Python Environment
- Check bottom-right corner of Positron
- You should see: **"Python 3.x"** (any version 3.7+)
- If not, click to select your Python interpreter

### 4. Set Your Scenario
- Find line 103:
```python
scenario_name = "Infrastructure_Investment"  # ← CHANGE THIS
```
- Replace with your scenario name (must match a file in `GLORIA_template/Scenarios/`)

### 5. Run the Script

**Option A: Run Entire Script (Recommended for first time)**
- Press: **Ctrl + Shift + Enter** (Windows/Linux)
- Or: **Cmd + Shift + Enter** (Mac)
- Or: Click **"Run"** button in top-right

**Option B: Run Line by Line (Good for debugging)**
- Put cursor on a line
- Press: **Ctrl + Enter** (Windows/Linux)
- Or: **Cmd + Enter** (Mac)
- This is exactly like RStudio!

---

## Using Positron's Features (Just Like RStudio!)

### Variable Explorer (Like RStudio's Environment Tab)

After running the script, you'll see variables in the right panel:

| Variable | What It Is | Like in R |
|----------|-----------|-----------|
| `MRIO_BASE` | GLORIA database object | `MRIO_BASE` list object |
| `Scenario` | Your investment scenario | `Scenario` list |
| `dq_total` | Output changes (numpy array) | `dq_total` numeric vector |
| `dempl_total` | Employment changes (numpy array) | `dempl_total` numeric vector |
| `empl_change` | Results DataFrame | `empl_change` data.frame |

**To view a DataFrame:**
- Click on `empl_change` in Variable Explorer
- A viewer tab opens (just like RStudio's `View()`)
- You can sort, filter, and explore the data

### Console (Like RStudio's Console Tab)

The bottom panel shows:
- Script output (all the ✓ marks and progress)
- Any errors or warnings
- You can type Python commands here (like R console)

**Example interactive commands after running:**
```python
# Check total jobs created
dempl_total.sum()

# Check by region
empl_change.groupby('Reg_ID')['dempl_total'].sum()

# View top 10 sectors
empl_change.groupby('Sec_ID')['dempl_total'].sum().nlargest(10)
```

### Files Panel (Like RStudio's Files Tab)

- Navigate to `GLORIA_results/`
- Double-click the Excel file to open it
- Or right-click → "Open with System Editor"

### Terminal (Like RStudio's Terminal Tab)

Use the terminal to run diagnostic scripts:
```bash
python check_paths.py
```

---

## Keyboard Shortcuts (Same as RStudio!)

| Action | Shortcut | R Equivalent |
|--------|----------|--------------|
| Run current line | Ctrl+Enter | Same! |
| Run entire script | Ctrl+Shift+Enter | Same! |
| Comment/uncomment | Ctrl+Shift+C | Same! |
| Indent | Tab | Same! |
| Un-indent | Shift+Tab | Same! |
| Find | Ctrl+F | Same! |
| Find & Replace | Ctrl+H | Same! |
| Go to line | Ctrl+G | Same! |
| Save | Ctrl+S | Same! |

---

## Debugging in Positron (Like RStudio)

### View Variable Contents

**In R:**
```r
View(my_data)
str(my_data)
head(my_data)
```

**In Positron Python:**
- **View:** Click variable in Explorer
- **Structure:** Hover over variable name
- **Head:** Type in console:
```python
empl_change.head()
empl_change.info()
empl_change.describe()
```

### Check for Errors

**In R:**
```r
traceback()  # After an error
```

**In Positron Python:**
- Error traceback automatically appears in console
- Shows line number and error type
- Click on filename:line to jump to that line

---

## Running the Diagnostic Script

### Method 1: From Terminal Panel
1. Click Terminal tab (bottom of Positron)
2. Type:
```bash
cd "Claude Code/temp"
python check_paths.py
```

### Method 2: Open and Run
1. Open `check_paths.py` in Positron
2. Press Ctrl+Shift+Enter

You should see all ✓ marks!

---

## Common Workflow

### 1. First Time Setup
```bash
# In Terminal
python check_paths.py  # Verify everything works
```

### 2. Set Your Scenario
Edit line 103 of `RunMINDSET_EmploymentOnly.py`:
```python
scenario_name = "Your_Scenario_Name"
```

### 3. Run the Analysis
- Open `RunMINDSET_EmploymentOnly.py`
- Press Ctrl+Shift+Enter
- Watch the progress in Console
- Check Variable Explorer for results

### 4. View Results in Excel
- Files panel → `GLORIA_results/`
- Double-click `Results_Your_Scenario_Name_EmploymentOnly.xlsx`

### 5. Further Analysis in R (Optional!)
Positron can run both Python and R. To analyze in R:

1. **File → New File → R Script**
2. Load the Python results:
```r
library(readxl)
library(tidyverse)

results <- read_excel("../../GLORIA_results/Results_Infrastructure_Investment_EmploymentOnly.xlsx",
                      sheet = "Employment_by_Region")

# Now use your favorite R tools
results %>%
  arrange(desc(Jobs_Created)) %>%
  slice_head(n = 10)
```

---

## Panel Layout (Just Like RStudio!)

```
┌──────────────────────┬──────────────────────┐
│                      │                      │
│   Script Editor      │  Variable Explorer   │
│                      │  (Environment)       │
│   (Your code here)   │  - MRIO_BASE         │
│                      │  - Scenario          │
│                      │  - empl_change       │
│                      │  - etc.              │
├──────────────────────┴──────────────────────┤
│                                              │
│   Console / Terminal / Output                │
│                                              │
│   >>> dempl_total.sum()                      │
│   1234.56                                    │
│                                              │
└──────────────────────────────────────────────┘
```

Same layout as RStudio! 🎉

---

## Switching Between Python and R

Positron's killer feature: **Native support for both Python and R**

### Current Script (Python)
```python
# RunMINDSET_EmploymentOnly.py
import pandas as pd
results = pd.read_excel("results.xlsx")
```

### Follow-up Analysis (R)
```r
# analysis.R
library(tidyverse)
results <- read_excel("results.xlsx")
results %>% ggplot(...)
```

**Both work perfectly in Positron!**

---

## Troubleshooting in Positron

### Issue: "Python interpreter not found"

**Solution:**
1. Click Python version in bottom-right
2. Select "Choose Python Interpreter"
3. Pick any Python 3.7+

### Issue: "Module not found"

**Solution:**
1. Open Terminal in Positron
2. Install packages:
```bash
pip install pandas numpy scipy openpyxl
```

### Issue: "Script runs but no output"

**Solution:**
- Check Console tab (bottom panel)
- Errors appear there
- Look for red error messages

### Issue: Can't find output file

**Solution:**
- Use Files panel (like RStudio)
- Navigate to: `../../GLORIA_results/`
- Or use full path in File Explorer

---

## Pro Tips for R Users

### 1. Use Variable Explorer
- Click on DataFrames to view them (like `View()` in R)
- No need to write `print()` statements

### 2. Interactive Console
- After script runs, try commands in console
- Just like R console

### 3. Code Completion
- Start typing and press Tab
- Just like RStudio!

### 4. Help/Documentation
- Hover over function name
- Or type in console: `help(function_name)`

### 5. Multiple Scripts
- Open multiple tabs
- Can run Python and R side by side

---

## Summary: Positron vs RStudio

| Feature | RStudio (R) | Positron (Python) |
|---------|-------------|-------------------|
| Run line | Ctrl+Enter | Ctrl+Enter ✓ |
| Run script | Ctrl+Shift+Enter | Ctrl+Shift+Enter ✓ |
| View data | `View(df)` | Click in Explorer ✓ |
| Environment | Environment tab | Variables tab ✓ |
| Console | R console | Python console ✓ |
| Terminal | Terminal tab | Terminal tab ✓ |
| Files | Files tab | Files tab ✓ |
| Layout | 4 panels | 4 panels ✓ |

**Everything is the same!** 🎉

---

## Ready to Run?

### Quick Checklist:
- [ ] Positron is open
- [ ] `RunMINDSET_EmploymentOnly.py` is open in editor
- [ ] Line 103 has your scenario name
- [ ] `SPYDER = True` on line 99 (leave as is)
- [ ] Press Ctrl+Shift+Enter
- [ ] Watch progress in Console
- [ ] Check results in `GLORIA_results/` folder

**You're all set!** The script will run just like R code in RStudio. 🚀

---

## Need Help?

1. Run `check_paths.py` first
2. Check Console for error messages
3. All ✓ marks means it worked!
4. Open the Excel file to see results

Enjoy using Positron - it's RStudio for Python! 🎊
