# Employment Data Fix - Summary

## Problem Diagnosed

Employment calculations were returning 0 jobs despite non-zero output changes for the 7 selected countries (BGR, BLZ, EGY, LBY, MAR, MEX, UGA). Investigation revealed:

1. **Root Cause 1**: `EMPL_COEF` file loaded by `Variable_list_MINDSET_SSP.xlsx` was **aggregated** (only ROW), not detailed country-level data
2. **Root Cause 2**: `HH_CONS_COU` mapping table mapped small/developing countries to "ROW" for employment, losing country-specific information
3. **Symptom**: After `build_empl_coef()` processing, only ROW (120 rows) remained in employment coefficients, not the 8 selected countries

## Solution Implemented

Modified **`SourceCode/exog_vars_SSP.py`** (confirmed by user as non-original file that can be edited) to:

### Fix 1: Load Detailed Employment Data

Added code (lines 186-231) that:
- **Detects** if loaded `EMPL_COEF` is aggregated (< 10 country columns)
- **Loads** detailed `empl_data.pkl` from GLORIA parsed database (all 164 countries)
- **Converts** from long format (REG_imp, PROD_COMM, Employment) to wide format (sectors × countries)
- **Creates** employment coefficients:
  - 1.0 for sectors/countries with employment data (proportional response)
  - 0.0 for sectors/countries without data
- **Filters** to only the 8 selected countries (avoids "'AUS' is not in list" error)
- **Formats** with `Unnamed: 0` and `Unnamed: 1` columns that `employment.py` expects

### Fix 2: Update Employment Mappings

Added code (lines 233-256) that:
- **Updates** `HH_CONS_COU` to map each selected country to **itself** for employment
  - BGR → BGR (not BGR → ROW)
  - MEX → MEX (not MEX → ROW)
  - etc.
- **Adds** mappings if they don't exist in HH_CONS_COU
- **Preserves** existing mappings for other purposes (household elasticities use different country groupings)

## Technical Details

### Employment Coefficient Interpretation

The employment multiplier formula in `employment.py` line 40:
```python
empl_multiplier = empl_coef * (empl_base / q_base)
```

Where:
- `empl_base / q_base` = baseline employment intensity (workers per $ of output)
- `empl_coef` = **elasticity** (how employment responds to output changes)
- `empl_coef = 1.0` means proportional response (1% output change → 1% employment change)

By using 1.0 as the coefficient, we assume employment changes proportionally with output at the baseline employment intensity.

### Data Source

- **Original**: `GLORIA_db/v57/2019/parsed_db_original/empl_data.pkl`
  - Created by `ParseCode/Parsing-Gloria-empl.py`
  - Extracts employment from GLORIA Satellite Accounts
  - Contains: REG_imp, PROD_COMM, Empl_Female, Empl_Male, Empl_low, Empl_mid, Empl_high
  - Covers: All 164 GLORIA countries × 120 sectors

## Files Modified

1. **`SourceCode/exog_vars_SSP.py`** (NOT an original MINDSET file - user confirmed OK to modify)
   - Added lines 186-231: Employment data fix
   - Added lines 233-256: HH_CONS_COU mapping fix

## Testing

### Quick Test

Run the employment fix test:
```bash
cd "C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main"
python "Claude Code/temp/TEST_EMPLOYMENT_FIX.py"
```

Expected output:
- ✓ EMPL_COEF has multiple countries (8), not just ROW
- ✓ HH_CONS_COU maps countries to themselves
- ✓ build_empl_coef() succeeds without errors
- ✓ Employment calculation returns non-zero jobs

### Full Scenario Test

Run the complete scenario test:
```bash
python "Claude Code/temp/TEST_ONE_SCENARIO.py"
```

Expected output:
- Step 1-4: ✓ (already working)
- Step 5: ✓ Employment = X jobs (non-zero)

## Next Steps

1. **Test the fix** using TEST_EMPLOYMENT_FIX.py
2. If successful, **test full scenario** using TEST_ONE_SCENARIO.py
3. Once single scenario works, **document workflow** for batch processing
4. **Run batch processing** of all 469 scenarios

## Potential Issues

### If employment is still zero:

Check if countries have employment data in empl_data.pkl:
```bash
python "Claude Code/temp/check_empl_data_pkl.py"
```

This will show:
- Which countries have employment data in empl_data.pkl
- Whether your 7 countries (BGR, BLZ, EGY, LBY, MAR, MEX, UGA) have data
- If not, you'll need to use ROW as a proxy or find alternative employment data

### If you get errors:

1. **FileNotFoundError for empl_data.pkl**: The file doesn't exist or path is wrong
2. **KeyError in employment.py**: HH_CONS_COU mapping may still have issues
3. **ValueError "'X' is not in list"**: EMPL_COEF has countries not in selected 8

## Assumptions

1. **Employment elasticity = 1.0**: Employment changes proportionally with output
   - More sophisticated: Could vary by sector (agriculture more elastic, etc.)
   - More sophisticated: Could use actual employment elasticities from literature

2. **Baseline employment intensity**: Derived from GLORIA Satellite Accounts
   - empl_base / q_base calculated in TEST_ONE_SCENARIO.py
   - Simplified: Uses q_base * 10 as placeholder

3. **Country aggregation**: Countries without specific employment data get coefficient = 0
   - Alternative: Could use regional averages or ROW as proxy
   - Alternative: Could use World Bank employment data to estimate

## Theory Reference

Leontief Input-Output Employment Model:
- ΔE = e * L * Δy
- Where:
  - ΔE = employment change (workers)
  - e = employment coefficient vector (workers/$)
  - L = Leontief inverse (I-A)^(-1)
  - Δy = final demand change ($)

MINDSET variation uses multiplier approach:
- ΔE = empl_multiplier * Δq
- Where:
  - empl_multiplier = empl_coef * (empl_base / q_base)
  - Δq = gross output change from IO model
