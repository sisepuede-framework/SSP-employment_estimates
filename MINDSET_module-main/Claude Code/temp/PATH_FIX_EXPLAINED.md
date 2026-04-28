# MINDSET Import Problem & Solution - Explained for R Users

## The Problem: Python Can't Find the Modules

### What Happened
Your script `RunMINDSET_EmploymentOnly.py` couldn't find the MINDSET modules (`exog_vars`, `IO`, `empl`, `results`, etc.) because it's looking in the wrong place.

### R vs Python Analogy

#### In R:
```r
# Your project structure:
# MINDSET_module-main/
# ├── SourceCode/
# │   ├── exog_vars.R
# │   ├── InputOutput.R
# │   └── employment.R
# └── Claude Code/
#     └── temp/
#         └── your_script.R

# If you're in Claude Code/temp/ and try:
source("SourceCode/exog_vars.R")
# ERROR! R looks for: Claude Code/temp/SourceCode/exog_vars.R (doesn't exist)

# You need to either:
# 1. Use setwd() to change to project root
setwd("../../")  # Go up two levels
source("SourceCode/exog_vars.R")  # Now it works!

# 2. Or use relative paths
source("../../SourceCode/exog_vars.R")
```

#### In Python (Same Problem):
```python
# Your script is in: MINDSET_module-main/Claude Code/temp/
# You try:
from SourceCode.exog_vars import exog_vars
# ERROR! Python looks in: Claude Code/temp/SourceCode/ (doesn't exist)

# You need to tell Python where the root directory is
```

---

## The Solution: What I Fixed

I added **path setup code** at the beginning of your script (lines 32-56). This code:

1. **Finds the script's location** (like `getwd()` in R)
2. **Navigates up to the project root** (like `setwd("../../")` in R)
3. **Adds the root to Python's search path** (like `.libPaths()` in R)
4. **Changes the working directory** (exactly like `setwd()` in R)

### The Fixed Code (Lines 32-56):

```python
#------------------------------------------------------------------------------
# PATH SETUP - Critical for finding MINDSET modules
#------------------------------------------------------------------------------
# In R, this is like: setwd("C:/path/to/project")
# In Python, we add the MINDSET root directory to sys.path so imports work

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up to MINDSET_module-main root (two levels up from Claude Code/temp)
# This is like using "../.." in R
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

# Add to Python's search path (like .libPaths() in R)
if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)

# Change working directory to MINDSET root (like setwd() in R)
os.chdir(mindset_root)

print(f"MINDSET root directory: {mindset_root}")
print(f"Current working directory: {os.getcwd()}\n")
```

### R Equivalent:
```r
# R equivalent of the above:
script_dir <- dirname(sys.frame(1)$ofile)  # Get script location
mindset_root <- file.path(script_dir, "..", "..")  # Go up 2 levels
mindset_root <- normalizePath(mindset_root)  # Make it absolute
setwd(mindset_root)  # Change working directory
print(paste("Working directory:", getwd()))
```

---

## Other Fixes

### 1. Scenario File Path (Line 115-118)
**Before:**
```python
cwd = os.getcwd() + "\\"
scenario_path = cwd + f"GLORIA_template\\Scenarios\\{scenario_name}.xlsx"
```

**After:**
```python
scenario_path = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios", f"{scenario_name}.xlsx")
print(f"Checking if scenario file exists: {os.path.exists(scenario_path)}\n")
```

**R Equivalent:**
```r
scenario_path <- file.path(getwd(), "GLORIA_template", "Scenarios",
                          paste0(scenario_name, ".xlsx"))
print(paste("File exists:", file.exists(scenario_path)))
```

### 2. Output File Path (Line 379-383)
**Before:**
```python
output_dir = "GLORIA_results"
output_file = f"{output_dir}\\Results_{scenario_name}_EmploymentOnly.xlsx"
```

**After:**
```python
output_dir = os.path.join(os.getcwd(), "GLORIA_results")
output_file = os.path.join(output_dir, f"Results_{scenario_name}_EmploymentOnly.xlsx")
```

**R Equivalent:**
```r
output_dir <- file.path(getwd(), "GLORIA_results")
output_file <- file.path(output_dir, paste0("Results_", scenario_name, "_EmploymentOnly.xlsx"))
```

---

## How to Run the Fixed Script

### Option 1: From Command Line (Recommended)
```bash
# Navigate to the script directory
cd "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main\Claude Code\temp"

# Run the script
python RunMINDSET_EmploymentOnly.py
```

### Option 2: From IDE (Spyder, VSCode, PyCharm)
1. Open the script in your IDE
2. Make sure `SPYDER = True` (line 99)
3. Set your scenario name (line 103)
4. Run the script (F5 in Spyder, Shift+Enter in VSCode)

### Option 3: From Any Directory
```bash
# You can run it from anywhere now:
python "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main\Claude Code\temp\RunMINDSET_EmploymentOnly.py"
```

---

## Testing the Fix

I created a test script: `test_imports.py`

Run it first to verify everything works:
```bash
cd "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main\Claude Code\temp"
python test_imports.py
```

You should see:
```
✓ Successfully imported: exog_vars
✓ Successfully imported: scenario
✓ Successfully imported: InputOutput (IO)
✓ Successfully imported: employment (empl)
✓ Successfully imported: results
✓ Successfully imported: utils
```

---

## Key Concepts: R vs Python

| Concept | R | Python |
|---------|---|--------|
| **Current directory** | `getwd()` | `os.getcwd()` |
| **Change directory** | `setwd(path)` | `os.chdir(path)` |
| **Check file exists** | `file.exists(path)` | `os.path.exists(path)` |
| **Join paths** | `file.path(a, b, c)` | `os.path.join(a, b, c)` |
| **Script location** | `dirname(sys.frame(1)$ofile)` | `os.path.dirname(__file__)` |
| **Relative paths** | `"../../folder"` | `os.path.join("..", "..", "folder")` |
| **Load external code** | `source("file.R")` | `from module import function` |
| **Library paths** | `.libPaths()` | `sys.path` |

### Important Differences:

1. **R's `source()`** vs **Python's `import`**:
   - R: Can source files from anywhere with relative/absolute paths
   - Python: Needs the directory in `sys.path` to import modules

2. **Path separators**:
   - R: Accepts both `/` and `\\`, usually use `/`
   - Python: Use `os.path.join()` for cross-platform compatibility

3. **Working directory**:
   - R: More flexible, can source from different directories
   - Python: Needs proper `sys.path` setup for imports to work

---

## Common Errors & Solutions

### Error: `ModuleNotFoundError: No module named 'SourceCode'`
**Cause:** Python can't find the SourceCode directory
**Solution:** Make sure the path setup code (lines 32-56) is at the top of your script

### Error: `FileNotFoundError: [Errno 2] No such file or directory: 'GLORIA_template\\Scenarios\\...'`
**Cause:** Working directory is wrong
**Solution:** The `os.chdir(mindset_root)` line (line 53) should fix this

### Error: `ImportError: cannot import name 'exog_vars' from 'SourceCode.exog_vars'`
**Cause:** The module file exists but has internal errors
**Solution:** Check the `SourceCode/exog_vars.py` file for syntax errors

---

## Summary

✅ **What was wrong:**
Your script was in a subdirectory (`Claude Code/temp/`) and couldn't find modules in the parent directory (`SourceCode/`)

✅ **What I fixed:**
Added path setup code to:
1. Find the MINDSET root directory (2 levels up)
2. Add it to Python's search path
3. Change the working directory
4. Use proper path joining functions

✅ **What you need to do:**
1. Run `test_imports.py` to verify the fix works
2. Run `RunMINDSET_EmploymentOnly.py` to do your employment analysis
3. Check the output in `MINDSET_module-main/GLORIA_results/`

---

## Need More Help?

If you still get errors, check:
1. Does `SourceCode/` directory exist in `MINDSET_module-main/`?
2. Does your scenario file exist in `GLORIA_template/Scenarios/`?
3. Do you have all required Python packages installed? (numpy, pandas, openpyxl)

Run `test_imports.py` and share the output if you need more help!
