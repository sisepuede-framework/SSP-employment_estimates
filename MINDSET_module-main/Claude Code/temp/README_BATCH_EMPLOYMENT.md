# Batch Employment Analysis Script

## Final Script Location

**Move this script to:**
```
MINDSET_module-main/SSP - Codes/BATCH_EMPLOYMENT_ALL_STRATEGIES.py
```

## How to Run

### From MINDSET_module-main root directory:

```bash
cd "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main"

python "SSP - Codes/BATCH_EMPLOYMENT_ALL_STRATEGIES.py"
```

**OR** (if running from SSP - Codes folder):

```bash
cd "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main\SSP - Codes"

python BATCH_EMPLOYMENT_ALL_STRATEGIES.py
```

**Note:** The script automatically detects which folder it's in and adjusts paths accordingly.

**Estimated runtime:** 30-60 minutes

## What It Does

Processes all 469 Strategy files and generates consolidated employment estimates using MINDSET methodology with ISIC sector classification.

## Output

Creates **one consolidated file** in:

```
MINDSET_module-main/SSP - Results/employment_consolidated.csv
```

## Output Structure

| Column | Description | Example |
|--------|-------------|---------|
| country_name | Full country name | Egypt |
| country_ISO | 3-letter ISO code | EGY |
| strategy_id | Full strategy identifier | Strategy_1004_EGY |
| strategy_name | Strategy description | (from ATTRIBUTE_STRATEGY.csv) |
| sector_code | ISIC section code | A, B, C, ... T |
| sector_name | ISIC sector description | Agriculture, forestry and fishing |
| direct_jobs | Direct employment | 12.89 |
| indirect_jobs | Supply chain employment | 0.01 |
| total_jobs | Total employment | 12.90 |
| share_of_total_jobs | Sector share (sums to 1.0) | 0.616 |

## Key Features

✅ **All 20 ISIC sectors** included per strategy (including zeros)
✅ **7 countries** included: BGR, BLZ, EGY, LBY, MAR, MEX, UGA
✅ **ROW excluded** per your request
✅ **Strategy attributes merged** from ATTRIBUTE_STRATEGY.csv
✅ **Direct/indirect jobs separated**
✅ **Shares sum to 1.0** per strategy-country
✅ **Path-independent** - works from root or SSP - Codes folder

## ISIC Sectors (20 total)

- **A**: Agriculture, forestry and fishing
- **B**: Mining and quarrying
- **C**: Manufacturing
- **D**: Electricity, gas, steam and air conditioning supply
- **E**: Water supply; sewerage, waste management
- **F**: Construction
- **G**: Wholesale and retail trade
- **H**: Transportation and storage
- **I**: Accommodation and food service activities
- **J**: Information and communication
- **K**: Financial and insurance activities
- **L**: Real estate activities
- **M**: Professional, scientific and technical activities
- **N**: Administrative and support services
- **O**: Public administration and defence
- **P**: Education
- **Q**: Human health and social work activities
- **R**: Arts, entertainment and recreation
- **S**: Other service activities
- **T**: Activities of households as employers

## Expected Dataset Size

- **Rows:** ~9,380 (469 strategies × 20 sectors, filtered to 7 countries)
- **Columns:** 10
- **File size:** ~2-3 MB

## Files Required

The script needs these files (uses absolute and relative paths):

### From Data folder (absolute path):
- `C:\Users\festeves\...\Data\GLORIA-Eora26 - Crosswalk.xlsx`
- `C:\Users\festeves\...\Data\ATTRIBUTE_STRATEGY.csv`

### From MINDSET_module-main (relative path):
- `GLORIA_template/Scenarios/Strategy_*.xlsx` (469 files)
- `GLORIA_db/v57/2019/SSP/...` (MRIO data)
- `SourceCode/*.py` (MINDSET modules)

## Path Handling

The script automatically handles paths whether run from:
- **Root:** `MINDSET_module-main/`
- **Codes folder:** `MINDSET_module-main/SSP - Codes/`
- **Temp folder:** `MINDSET_module-main/Claude Code/temp/`

It detects the folder and adjusts the path to MINDSET root accordingly.

## Methodology

Follows MINDSET's original employment calculation:
```
empl_multiplier = EMPL_COEF × (empl_base / q_base)
dempl = empl_multiplier × dq
```

Where:
- `empl_base`: Employment baseline from LABOR_BASE
- `q_base`: Baseline output from Leontief model
- `dq`: Output changes from investment
- `EMPL_COEF`: Country- and product-specific employment elasticities

Then aggregates 120 GLORIA products to 20 ISIC sectors using the crosswalk.

## Troubleshooting

### If script fails:

1. **Check working directory:**
   - Script should print: `Working directory: ...MINDSET_module-main`
   - If not, run from root directory

2. **Check files exist:**
   ```bash
   # From MINDSET_module-main directory
   ls "GLORIA_template/Scenarios/Strategy_*.xlsx" | wc -l
   # Should show 469
   ```

3. **Check data files:**
   - Data folder path is absolute - verify it exists
   - Check crosswalk and attributes files exist

4. **Check for errors:**
   - Look for "[ERROR]" messages in output
   - Check `SSP - Results/processing_errors.txt` if created

### Common issues:

- **"No Strategy files found!"** → Wrong working directory
- **"Crosswalk file not found"** → Check absolute path to Data folder
- **Memory error** → Close other programs (needs ~2-3 GB RAM)
- **Long runtime** → Normal! 469 files takes 30-60 minutes

## Progress Tracking

Script prints progress every 10 strategies:
```
Working directory: ...\MINDSET_module-main
[1/469] Strategy_1001_BGR (~45.2 min remaining)
[10/469] Strategy_1004_EGY (~35.3 min remaining)
[20/469] Strategy_1005_MEX (~33.1 min remaining)
...
[469/469] Strategy_9999_UGA (~0.0 min remaining)
```

## Validation

At the end, script validates:
- ✓ Share sums equal 1.0 per strategy (mean should be 1.000000)
- ✓ Total jobs calculated correctly
- ✓ Direct/indirect breakdown makes sense
- ✓ All 7 countries included (no ROW)
- ✓ Country-level summaries

## Output Example

```
[OK] SAVED: SSP - Results/employment_consolidated.csv
  Full path: C:\...\MINDSET_module-main\SSP - Results\employment_consolidated.csv
  Rows: 9,380
  Columns: 10

Dataset Overview:
  Total rows: 9,380
  Strategies: 469
  Countries: 7 (excl. ROW)
  ISIC sectors: 20

Total Jobs per Strategy:
  Mean:   35.2
  Median: 28.5
  Min:    1.2
  Max:    156.8

Direct vs Indirect Jobs (all strategies):
  Total Direct:   12,453 (65.3%)
  Total Indirect: 6,627 (34.7%)

By Country:
  BGR (Bulgaria):
    Mean jobs per strategy: 42.3
    Total jobs all strategies: 2,854
    Number of strategies: 67
  ...
```

## After Running

The output file will be at:
```
MINDSET_module-main\SSP - Results\employment_consolidated.csv
```

Ready to load into your dissertation analysis (R, Stata, Python, etc.)!

## Questions?

The script is self-contained and includes:
- ✓ Automatic path detection
- ✓ Progress indicators
- ✓ Error logging
- ✓ Validation checks
- ✓ Summary statistics
- ✓ Full path printing

Just move it to `SSP - Codes` folder and run!
