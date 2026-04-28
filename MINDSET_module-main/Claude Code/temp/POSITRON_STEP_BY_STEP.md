# Positron Step-by-Step Guide (With Pictures in Words!)

**For beginners: Exactly what to click and where**

---

## Part 1: Create the Scenario Files (5 minutes)

### Step 1: Open the File

```
In Positron:
┌─────────────────────────────────────────┐
│ File  Edit  View  Terminal  Help        │  ← Menu bar at top
├─────────────────────────────────────────┤
│                                         │
```

1. Click **"File"** (top-left corner)
2. Click **"Open File..."**
3. Navigate to your folder:
   - Look for: `MINDSET_module-main`
   - Then: `Claude Code`
   - Then: `temp`
4. Click on: **`SIMPLE_SCENARIO_CREATOR.py`**
5. Click **"Open"**

**What you see:**
```
The file opens in the main editor panel (middle of screen)
You'll see Python code (don't worry about understanding it!)
```

### Step 2: Run the Script

Look at the top-right of the editor window. You'll see:

```
┌──────────────────────────────────┐
│ ▶ Run                     ↓      │  ← Buttons here
└──────────────────────────────────┘
```

**Option A (Easiest):**
- Click the **▶ Run** button

**Option B:**
- Press **Ctrl + Shift + Enter** on keyboard
  (Hold Ctrl, hold Shift, press Enter)

### Step 3: Watch the Console

The **Console panel** (bottom of screen) will show:

```
============================================================
SIMPLE SCENARIO CREATOR
============================================================

1. Working directory: C:\Users\festeves\...

2. Loading GLORIA product list...
   ✓ Found 120 products               ← Look for these checkmarks!

3. Loading GLORIA region list...
   ✓ Found 162 regions

4. Creating reference lists...
   ✓ Created: Claude Code/temp/GLORIA_Products_Reference.xlsx
   ✓ Created: Claude Code/temp/GLORIA_Regions_Reference.xlsx

[... more lines ...]

SUCCESS! Files created:
============================================================
```

**If you see ✓ marks and "SUCCESS!"** → Perfect! Continue to Part 2

**If you see ✗ or ERROR** → Read the error message and check BEGINNER_GUIDE.md

### Step 4: Verify Files Created

**In Positron's Files panel (usually right side):**

1. Navigate to `Claude Code` → `temp`
2. Look for new files:
   - `GLORIA_Products_Reference.xlsx` ✓
   - `GLORIA_Regions_Reference.xlsx` ✓
   - `SCENARIO_TEMPLATE_SIMPLE.xlsx` ✓

3. Navigate back to `MINDSET_module-main`
4. Then go to `GLORIA_template` → `Scenarios`
5. Look for:
   - `Test_AllProducts_1M_USA.xlsx` ✓
   - `Test_Construction_100M_USA.xlsx` ✓

**All there?** Great! Move to Part 2.

---

## Part 2: Run Your First Employment Analysis (10 minutes)

### Step 1: Open the Employment Script

```
In Positron:
File → Open File...
```

Navigate to: `Claude Code` → `temp` → **`RunMINDSET_EmploymentOnly.py`**

Click **Open**

### Step 2: Find Line 103

**Ways to find it:**

**Method A: Use "Go to Line"**
1. Press **Ctrl + G** on keyboard
2. Type: `103`
3. Press Enter
4. You jump to line 103!

**Method B: Scroll**
- Scroll down in the editor
- Look at line numbers on the left side
- Find line 103

**What you see at line 103:**
```python
    scenario_name = "Infrastructure_Investment"  # ← CHANGE THIS TO YOUR SCENARIO NAME
```

### Step 3: Edit Line 103

**Current:**
```python
scenario_name = "Infrastructure_Investment"
```

**Change to (for first test):**
```python
scenario_name = "Test_Construction_100M_USA"
```

**How to edit:**
1. Click on the line (line 103)
2. Delete the text inside the quotes: `"Infrastructure_Investment"`
3. Type: `Test_Construction_100M_USA`
4. Make sure quotes stay: `"Test_Construction_100M_USA"`

**Save the file:**
- Press **Ctrl + S**
- Or: File → Save

### Step 4: Run the Employment Script

Same as before:

**Option A:** Click **▶ Run** button (top-right)

**Option B:** Press **Ctrl + Shift + Enter**

### Step 5: Watch It Run (Be Patient!)

The console will show progress:

```
================================================================================
MINDSET EMPLOYMENT-ONLY ESTIMATION
================================================================================

MINDSET root directory: C:\Users\...\MINDSET_module-main
Current working directory: C:\Users\...\MINDSET_module-main

Running in IDE mode with scenario: Test_Construction_100M_USA
Scenario file: C:\...\GLORIA_template\Scenarios\Test_Construction_100M_USA.xlsx
Checking if scenario file exists: True

--------------------------------------------------------------------------------
STEP 1: Loading MRIO Data
--------------------------------------------------------------------------------
✓ Loaded Leontief inverse: (19440, 19440)
✓ Loaded employment coefficients
✓ Loaded 162 countries/regions
✓ Loaded 120 sectors
Time: 5.3 seconds

[... more steps ...]

SUMMARY:
  Total Investment: $100,000,000
  Total Jobs Created: 1,234
  Employment Multiplier: 12.34 jobs per $1M

✓ Results saved to: GLORIA_results\Results_Test_Construction_100M_USA_EmploymentOnly.xlsx

================================================================================
EMPLOYMENT ESTIMATION COMPLETE
================================================================================
```

**This takes 5-10 minutes. Don't worry if it seems slow!**

**What's happening:**
- Loading huge matrices (19,440 × 19,440 = 378 million cells!)
- Calculating employment for all 162 regions × 120 sectors
- Like running 19,440 regressions in R

### Step 6: Find Your Results

**In File Explorer (Windows):**

1. Navigate to your MINDSET folder
2. Look for folder: **`GLORIA_results`** (created automatically)
3. Inside, find: **`Results_Test_Construction_100M_USA_EmploymentOnly.xlsx`**
4. Double-click to open in Excel

**In Positron Files panel:**

1. Click refresh button (circular arrow)
2. Navigate to `GLORIA_results` folder
3. Right-click the Excel file
4. Click "Open with System Editor"

### Step 7: Explore the Results

**The Excel file has 5 sheets:**

**1. Summary Sheet**
```
┌──────────────────────────────────────┬────────────────┐
│ Metric                               │ Value          │
├──────────────────────────────────────┼────────────────┤
│ Total Investment (USD)               │ $100,000,000   │
│ Total Jobs Created                   │ 1,234          │
│ Employment Multiplier (jobs/$1M)     │ 12.34          │
│ Average Output Multiplier            │ 1.75x          │
└──────────────────────────────────────┴────────────────┘
```

**2. Employment_by_Region**
- Which countries got jobs
- Sorted by number of jobs

**3. Employment_by_Sector**
- Which industries got jobs
- Sorted by number of jobs

**4. Employment_Details**
- Full breakdown by region × sector
- 19,440 rows (every combination)

**5. Output_Details**
- Output changes
- For validation

---

## Part 3: Run the Full Analysis (All 120 Products!)

Now that you know it works, let's run the full analysis!

### Step 1: Change Scenario (Line 103 Again)

In `RunMINDSET_EmploymentOnly.py`:

**Change line 103 from:**
```python
scenario_name = "Test_Construction_100M_USA"
```

**To:**
```python
scenario_name = "Test_AllProducts_1M_USA"
```

**Save:** Ctrl + S

### Step 2: Run Again

- Click **▶ Run** or press **Ctrl + Shift + Enter**
- Wait 5-10 minutes
- Watch console for progress

### Step 3: Get Results

New file created:
- `GLORIA_results/Results_Test_AllProducts_1M_USA_EmploymentOnly.xlsx`

**Open it and look at "Employment_by_Sector" sheet!**

This has **ALL 120 products** with employment impacts!

```
Product_name               | Jobs_Created
────────────────────────────────────────
Construction               | 15.2
Manufacturing of machinery | 12.8
Transportation             | 11.5
Agriculture                | 9.3
... (all 120 products)
```

**Perfect for your dissertation!** 📊

---

## Troubleshooting: What If It Doesn't Work?

### Problem: "Python not found" when clicking Run

**Solution:**
1. Look at bottom-right corner of Positron
2. Should say: "Python 3.x"
3. If not:
   - Click on it
   - Select "Choose Python Interpreter"
   - Pick any Python 3.7+ option

### Problem: "No module named 'pandas'"

**Solution: Install packages**

1. Open **Terminal** in Positron (bottom panel)
2. Type and press Enter:
   ```bash
   pip install pandas numpy openpyxl
   ```
3. Wait for installation to complete
4. Try running script again

### Problem: Script runs but no files created

**Check console output:**
- Scroll up in console
- Look for ✗ marks or "Error" messages
- Read what it says

**Common issues:**
- "FileNotFoundError" → Wrong directory, check path
- "PermissionError" → Close Excel if file is open
- "No such file" → Make sure you're in MINDSET_module-main folder

### Problem: "Scenario file not found"

**Check:**
1. Did you run `SIMPLE_SCENARIO_CREATOR.py` first?
2. Check if file exists: `GLORIA_template/Scenarios/Test_Construction_100M_USA.xlsx`
3. Check spelling of scenario_name exactly matches filename

---

## Visual Checklist

```
□ Step 1: Open SIMPLE_SCENARIO_CREATOR.py
□ Step 2: Click Run button (or Ctrl+Shift+Enter)
□ Step 3: See "SUCCESS!" in console
□ Step 4: Check files exist in Claude Code/temp
□ Step 5: Open RunMINDSET_EmploymentOnly.py
□ Step 6: Change line 103 to: "Test_Construction_100M_USA"
□ Step 7: Save file (Ctrl+S)
□ Step 8: Click Run button
□ Step 9: Wait 5-10 minutes
□ Step 10: Check GLORIA_results folder for Excel file
□ Step 11: Open Excel file and explore!
```

---

## Quick Summary

### Creating Scenarios (One Time Setup)
```
Open: SIMPLE_SCENARIO_CREATOR.py
Press: Ctrl+Shift+Enter
Result: 5 files created
```

### Running Analysis (Each Time)
```
Open: RunMINDSET_EmploymentOnly.py
Edit: Line 103 (scenario name)
Press: Ctrl+Shift+Enter
Wait: 5-10 minutes
Check: GLORIA_results folder
```

---

## You're Ready!

**If you got this far:** ✅ You successfully ran Python in Positron!

**Next steps:**
1. Run the all-products scenario
2. Open the results Excel file
3. Analyze in R if you want (it's just an Excel file!)
4. Create your own scenarios using SCENARIO_TEMPLATE_SIMPLE.xlsx

**Remember:** You don't need to understand Python! Just:
- Click Run
- Edit line 103
- Get Excel results
- Analyze however you want!

🎉 **Good luck with your dissertation!** 🎉
