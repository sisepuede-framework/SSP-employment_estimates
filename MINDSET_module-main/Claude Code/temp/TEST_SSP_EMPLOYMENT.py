"""
TEST: SSP Employment with Aggregated Data

Tests if employment calculations work with:
- 8 aggregated regions in SSP\ folder (BGR, BLZ, EGY, LBY, MAR, MEX, ROW, UGA)
- ROW uses China elasticity proxy
- Aggregated employment data for ROW
"""

import sys
import os
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("TEST: SSP EMPLOYMENT WITH AGGREGATED DATA")
print("="*80)
print()

# STEP 1: Load aggregated MRIO data
print("STEP 1: Loading MRIO data from SSP folder...")
print("-"*80)
from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print(f"✓ Loaded MRIO data")
print(f"  Countries: {MRIO_BASE.COU_ID}")
print(f"  Number of countries: {len(MRIO_BASE.COU_ID)}")
print(f"  Expected: 8 (BGR, BLZ, EGY, LBY, MAR, MEX, ROW, UGA)")
print()

# STEP 2: Check EMPL_COEF structure
print("STEP 2: Checking EMPL_COEF (elasticity coefficients)...")
print("-"*80)
print(f"  Shape: {MRIO_BASE.EMPL_COEF.shape}")
print(f"  Columns (first 10): {list(MRIO_BASE.EMPL_COEF.columns[:10])}")
print(f"  Total country columns: {len(MRIO_BASE.EMPL_COEF.columns) - 2}")
print()

# STEP 3: Check HH_CONS_COU mappings
print("STEP 3: Checking HH_CONS_COU employment mappings...")
print("-"*80)
print(f"  Shape: {MRIO_BASE.HH_CONS_COU.shape}")
print(f"  Mappings:")
for _, row in MRIO_BASE.HH_CONS_COU.iterrows():
    country_code = row['Country_Code']
    empl_country = row['Employment_country']
    print(f"    {country_code} → {empl_country}")
print()

# STEP 4: Test build_empl_coef()
print("STEP 4: Testing build_empl_coef()...")
print("-"*80)
from SourceCode.employment import empl

try:
    Empl_model = empl(MRIO_BASE)
    Empl_model.build_empl_coef()

    print(f"✓ build_empl_coef() succeeded")
    print(f"  EMPL_COEF shape: {Empl_model.EMPL_COEF.shape}")
    print(f"  Expected: (960, 3) for 8 regions × 120 sectors")
    print(f"  Unique regions: {sorted(Empl_model.EMPL_COEF['REG_imp'].unique())}")
    print(f"  Non-zero coefficients: {(Empl_model.EMPL_COEF['empl_coef'] != 0).sum()}")

    if len(Empl_model.EMPL_COEF) == 960:
        print(f"\n✓ PASS: Got expected 960 rows (8 countries × 120 sectors)")
    else:
        print(f"\n✗ FAIL: Expected 960 rows, got {len(Empl_model.EMPL_COEF)}")

    # Check if ROW has coefficients
    row_coefs = Empl_model.EMPL_COEF[Empl_model.EMPL_COEF['REG_imp'] == 'ROW']
    if len(row_coefs) > 0:
        non_zero_row = (row_coefs['empl_coef'] != 0).sum()
        print(f"\n✓ ROW has {len(row_coefs)} rows with {non_zero_row} non-zero coefficients")
    else:
        print(f"\n✗ ROW has NO employment coefficients")

except Exception as e:
    print(f"✗ FAIL: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# STEP 5: Test with actual scenario (if available)
print("STEP 5: Testing with Strategy_1004_MEX scenario...")
print("-"*80)

scenario_file = "GLORIA_template/Scenarios/MEX_newII/Strategy_1004_MEX.xlsx"
if os.path.exists(scenario_file):
    try:
        from SourceCode.scenario import scenario

        # Mock log if not available
        try:
            from SourceCode.log import log
            Log = log()
        except:
            class MockLog:
                def log_to_csv(self, *args, **kwargs): pass
                def log(self, *args, **kwargs): pass
            Log = MockLog()

        SCENARIO = scenario(MRIO_BASE, scenario_file, Log)
        dy_inv_exog = SCENARIO.convert_y_investment()
        print(f"✓ Loaded scenario: ${dy_inv_exog.sum():,.0f} investment")

        # Calculate output changes
        from SourceCode.InputOutput import IO
        IO_model = IO(MRIO_BASE)
        dq_total = IO_model.calc_dq(dy_inv_exog)
        print(f"✓ Calculated output: Δq = ${dq_total.sum():,.0f}")

        # Calculate employment (simplified - just checking if it runs)
        # For proper calculation, would need empl_base from production cost module
        q_base = MRIO_BASE.output['output'].to_numpy()
        empl_base = q_base * 10  # Simplified assumption

        Empl_model.calc_empl_multiplier(empl_base, q_base)
        dempl = Empl_model.calc_dempl(dq_total)

        total_jobs = dempl.sum()
        print(f"✓ Employment impact: {total_jobs:,.0f} jobs")

        if abs(total_jobs) > 0.1:
            print(f"\n✓ PASS: Employment calculation returns non-zero result!")

            # Show breakdown by country
            print(f"\nJobs by country:")
            for i, country in enumerate(MRIO_BASE.COU_ID):
                start_idx = i * 120
                end_idx = start_idx + 120
                country_jobs = dempl[start_idx:end_idx].sum()
                if abs(country_jobs) > 0.01:
                    print(f"  {country}: {country_jobs:,.0f} jobs")
        else:
            print(f"\n✗ FAIL: Employment is still zero")

    except Exception as e:
        print(f"✗ FAIL: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print(f"⚠ Skipped: Scenario file not found")
    print(f"  Looking for: {scenario_file}")

print()
print("="*80)
print("TEST COMPLETE")
print("="*80)
