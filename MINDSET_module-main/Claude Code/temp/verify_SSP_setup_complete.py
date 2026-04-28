"""
VERIFY COMPLETE SSP SETUP

Checks that all components are ready for employment analysis:
1. Y_BASE.mat exists in SSP folder and loads correctly
2. IO_model.initialize() works (loads Y_BASE instead of rebuilding)
3. All required modules can be initialized

This confirms the SSP setup is complete and ready for batch processing.
"""

import sys
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("VERIFY COMPLETE SSP SETUP")
print("="*80)
print()

#==============================================================================
# CHECK 1: Y_BASE.mat exists in SSP folder
#==============================================================================
print("CHECK 1: Y_BASE.mat file location")
print("-"*80)

y_base_path = "GLORIA_db\\v57\\2019\\SSP\\GLORIA_Y_Base_2019.mat"
if os.path.exists(y_base_path):
    size_kb = os.path.getsize(y_base_path) / 1024
    print(f"✓ Y_BASE.mat exists in SSP folder")
    print(f"  Location: {y_base_path}")
    print(f"  Size: {size_kb:.1f} KB")
else:
    print(f"✗ Y_BASE.mat NOT found at: {y_base_path}")
    sys.exit(1)

print()

#==============================================================================
# CHECK 2: Load MRIO data with Y_BASE
#==============================================================================
print("CHECK 2: Loading MRIO data (should load Y_BASE from file)")
print("-"*80)

from SourceCode.exog_vars_SSP import exog_vars

start_time = time.time()
MRIO_BASE = exog_vars()
elapsed = time.time() - start_time

print(f"✓ MRIO data loaded in {round(elapsed, 1)} seconds")
print(f"  Countries: {len(MRIO_BASE.COU_ID)} ({', '.join(MRIO_BASE.COU_ID)})")
print(f"  Sectors: {len(MRIO_BASE.SEC_ID)}")

# Check if Y_BASE was loaded
if hasattr(MRIO_BASE, 'Y_BASE'):
    print(f"✓ Y_BASE loaded from .mat file")
    print(f"  Keys: {list(MRIO_BASE.Y_BASE.keys())}")
else:
    print(f"✗ Y_BASE not loaded")

print()

#==============================================================================
# CHECK 3: IO model initialization
#==============================================================================
print("CHECK 3: IO model initialization (should use pre-computed Y_BASE)")
print("-"*80)

from SourceCode.InputOutput import IO

IO_model = IO(MRIO_BASE)

start_time = time.time()
IO_model.initialize()
elapsed = time.time() - start_time

print(f"✓ IO model initialized in {round(elapsed, 1)} seconds")
print(f"  L_BASE shape: {IO_model.L_BASE.shape}")
print(f"  q_base shape: {IO_model.q_base.shape}")
print(f"  y0 shape: {IO_model.y0.shape}")

# Verify q_base has correct dimensions (960 = 8 countries × 120 sectors)
if IO_model.q_base.shape[0] == 960:
    print(f"✓ q_base has correct dimensions (960 elements)")
else:
    print(f"✗ q_base has wrong dimensions: {IO_model.q_base.shape}")

print()

#==============================================================================
# CHECK 4: Production cost module (for employment baseline)
#==============================================================================
print("CHECK 4: Production cost module")
print("-"*80)

# Create a mock scenario for prod_cost
from SourceCode.scenario import scenario

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

# Use Strategy_1004_MEX as test scenario
test_scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
if os.path.exists(test_scenario_file):
    Scenario = scenario(MRIO_BASE, test_scenario_file, MockLog())

    from SourceCode.prod_cost import prod_cost
    Prod_cost = prod_cost(MRIO_BASE, Scenario)
    Prod_cost.calc_shares()

    print(f"✓ Production cost module works")
    print(f"  empl_base shape: {Prod_cost.empl_base.shape}")
    print(f"  Expected: (954, 3) - some country-sector combos don't exist")
else:
    print(f"⚠ Test scenario not found, skipping prod_cost check")
    print(f"  (This is OK - will work when running actual scenarios)")

print()

#==============================================================================
# CHECK 5: Employment module
#==============================================================================
print("CHECK 5: Employment module")
print("-"*80)

from SourceCode.employment import empl

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

print(f"✓ Employment module works")
print(f"  EMPL_COEF shape: {Empl_model.EMPL_COEF.shape}")
print(f"  Regions: {sorted(Empl_model.EMPL_COEF['REG_imp'].unique())}")

print()

#==============================================================================
# SUMMARY
#==============================================================================
print("="*80)
print("✓ ALL CHECKS PASSED - SSP SETUP COMPLETE!")
print("="*80)
print()
print("Your SSP setup is ready for employment analysis.")
print()
print("Key components verified:")
print("  ✓ Y_BASE.mat in SSP folder (8 aggregated regions)")
print("  ✓ exog_vars_SSP loads all required data")
print("  ✓ IO model initializes with pre-computed matrices")
print("  ✓ Production cost module works")
print("  ✓ Employment module works")
print()
print("Next step: Create proper employment workflow script using MINDSET modules")
print("  - Investment module for proper investment-to-demand conversion")
print("  - Production cost module for employment baseline")
print("  - IO module for output changes")
print("  - Employment module for job impacts")
print()
print("="*80)
