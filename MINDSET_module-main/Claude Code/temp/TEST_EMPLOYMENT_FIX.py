"""
TEST: Employment Fix for 7 Selected Countries

This script tests that the employment data fix in exog_vars_SSP.py works correctly.

WHAT WAS FIXED:
1. exog_vars_SSP.py now detects if EMPL_COEF is aggregated (ROW only)
2. If aggregated, loads detailed empl_data.pkl with all GLORIA countries
3. Converts to employment coefficients (1.0 where data exists, 0.0 otherwise)
4. Filters to only selected countries (BGR, BLZ, EGY, LBY, MAR, MEX, ROW, UGA)
5. Updates HH_CONS_COU to map countries to themselves for employment

EXPECTED RESULT:
- Employment calculations should return non-zero job estimates for countries with data
- No "'AUS' is not in list" errors
- EMPL_COEF should have 8 countries, not just ROW
"""

import sys
import os
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("EMPLOYMENT FIX TEST")
print("="*80)
print()

# Step 1: Load MRIO data (triggers the employment fix)
print("STEP 1: Loading MRIO data...")
from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()
print(f"✓ Loaded MRIO data")
print()

# Step 2: Check EMPL_COEF structure
print("STEP 2: Checking EMPL_COEF structure...")
print(f"  Shape: {MRIO_BASE.EMPL_COEF.shape}")
print(f"  Columns: {list(MRIO_BASE.EMPL_COEF.columns[:5])}... (first 5)")
num_country_cols = len(MRIO_BASE.EMPL_COEF.columns) - 2
print(f"  Number of country columns: {num_country_cols}")
print(f"  Expected: 8 (BGR, BLZ, EGY, LBY, MAR, MEX, ROW, UGA)")

if num_country_cols >= 7:
    print(f"  ✓ PASS: EMPL_COEF has multiple countries, not just ROW")
else:
    print(f"  ✗ FAIL: EMPL_COEF only has {num_country_cols} country column(s)")
print()

# Step 3: Check HH_CONS_COU mappings
print("STEP 3: Checking HH_CONS_COU employment mappings...")
for country in MRIO_BASE.COU_ID:
    matches = MRIO_BASE.HH_CONS_COU[MRIO_BASE.HH_CONS_COU['Country_Code'] == country]
    if len(matches) > 0:
        empl_country = matches['Employment_country'].iloc[0]
        if empl_country == country:
            print(f"  ✓ {country} → {empl_country}")
        else:
            print(f"  ✗ {country} → {empl_country} (should map to itself)")
    else:
        print(f"  ✗ {country} has NO mapping")
print()

# Step 4: Test build_empl_coef()
print("STEP 4: Testing build_empl_coef()...")
from SourceCode.employment import empl
try:
    Empl_model = empl(MRIO_BASE)
    Empl_model.build_empl_coef()

    print(f"  ✓ build_empl_coef() succeeded (no errors)")
    print(f"  EMPL_COEF after build: shape = {Empl_model.EMPL_COEF.shape}")
    print(f"  Unique regions: {sorted(Empl_model.EMPL_COEF['REG_imp'].unique())}")
    print(f"  Expected: {sorted(MRIO_BASE.COU_ID)}")

    # Check if we have more than just ROW
    unique_regions = Empl_model.EMPL_COEF['REG_imp'].unique()
    if len(unique_regions) > 1:
        print(f"  ✓ PASS: EMPL_COEF has {len(unique_regions)} regions (not just ROW)")
    else:
        print(f"  ⚠ WARNING: EMPL_COEF only has {unique_regions} after build")

    # Check for non-zero coefficients
    non_zero = (Empl_model.EMPL_COEF['empl_coef'] != 0).sum()
    print(f"  Non-zero coefficients: {non_zero} out of {len(Empl_model.EMPL_COEF)}")

except Exception as e:
    print(f"  ✗ FAIL: {type(e).__name__}: {str(e)}")
print()

# Step 5: Test with actual scenario
print("STEP 5: Testing with Strategy_1004_MEX scenario...")
try:
    # Load scenario
    from SourceCode.scenario import scenario

    # Try to load log module, use mock if not available
    try:
        from SourceCode.log import log
        Log = log()
    except (ModuleNotFoundError, ImportError):
        class MockLog:
            def log_to_csv(self, *args, **kwargs): pass
            def log(self, *args, **kwargs): pass
        Log = MockLog()
        print("  Note: Using mock logger (log module not found)")

    SCENARIO = scenario(MRIO_BASE, "GLORIA_template/Scenarios/MEX_newII/Strategy_1004_MEX.xlsx", Log)

    # Convert to demand
    dy_inv_exog = SCENARIO.convert_y_investment()
    print(f"  ✓ Loaded scenario: investment = ${dy_inv_exog.sum():,.0f}")

    # Calculate output
    from SourceCode.InputOutput import IO
    IO_model = IO(MRIO_BASE)
    dq_total = IO_model.calc_dq(dy_inv_exog)
    print(f"  ✓ Calculated output: Δq = ${dq_total.sum():,.0f}")

    # Calculate employment
    # Create simple base employment for testing (proportional to output)
    q_base = MRIO_BASE.output['output'].to_numpy()
    empl_base = q_base * 10  # Assume 10 workers per $M baseline

    Empl_model.calc_empl_multiplier(empl_base, q_base)
    dempl = Empl_model.calc_dempl(dq_total)

    total_jobs = dempl.sum()
    print(f"  Employment impact: {total_jobs:,.0f} jobs")

    if abs(total_jobs) > 0.1:
        print(f"  ✓ PASS: Employment calculation returns non-zero result!")
    else:
        print(f"  ✗ FAIL: Employment is still zero despite output changes")

    # Show breakdown by country
    print(f"\n  Jobs by country:")
    for i, country in enumerate(MRIO_BASE.COU_ID):
        start_idx = i * 120
        end_idx = start_idx + 120
        country_jobs = dempl[start_idx:end_idx].sum()
        if abs(country_jobs) > 0.01:
            print(f"    {country}: {country_jobs:,.0f} jobs")

except Exception as e:
    print(f"  ✗ FAIL: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print("TEST COMPLETE")
print("="*80)
