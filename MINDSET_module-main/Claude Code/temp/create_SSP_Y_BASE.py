"""
CREATE SSP Y_BASE.mat FILE

This script uses MINDSET's built-in IO.initialize() method to create
the SSP\GLORIA_Y_Base_2019.mat file for 8 aggregated regions.

Prerequisites (manually completed):
1. Variable_list_MINDSET_SSP.xlsx has INV_BASE and NPISH_BASE entries
2. Y_BASE location updated to: GLORIA_db\v57\2019\SSP\GLORIA_Y_Base_2019.mat

What this script does:
- Loads SSP MRIO data (including INV_BASE and NPISH_BASE)
- Creates IO model
- Calls initialize() which:
  * Checks if Y_BASE.mat exists
  * Since it doesn't exist in SSP folder, builds it from scratch
  * Computes y_hh0, y_gov0, y_fcf0, y_npish, y_inv vectors
  * Saves as SSP\GLORIA_Y_Base_2019.mat

After this runs successfully:
- Y_BASE.mat will contain all final demand vectors for 8 regions
- INV_BASE and NPISH_BASE can be removed from Variable_list (optional)
"""

import sys
import os
import time

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("CREATE SSP Y_BASE.mat FILE")
print("="*80)
print()

#==============================================================================
# STEP 1: Load MRIO Data with SSP Variable List
#==============================================================================
print("STEP 1: Loading MRIO data from SSP folder...")
print("-"*80)

from SourceCode.exog_vars_SSP import exog_vars
start_time = time.time()
MRIO_BASE = exog_vars()

print(f"✓ MRIO data loaded in {round(time.time() - start_time, 1)} seconds")
print(f"  Countries: {len(MRIO_BASE.COU_ID)} ({', '.join(MRIO_BASE.COU_ID)})")
print(f"  Sectors: {len(MRIO_BASE.SEC_ID)}")
print()

# Verify INV_BASE and NPISH_BASE were loaded
if hasattr(MRIO_BASE, 'INV_BASE'):
    print(f"✓ INV_BASE loaded: {MRIO_BASE.INV_BASE.shape}")
else:
    print("✗ ERROR: INV_BASE not loaded!")
    print("  → Check Variable_list_MINDSET_SSP.xlsx has INV_BASE entry")
    sys.exit(1)

if hasattr(MRIO_BASE, 'NPISH_BASE'):
    print(f"✓ NPISH_BASE loaded: {MRIO_BASE.NPISH_BASE.shape}")
else:
    print("✗ ERROR: NPISH_BASE not loaded!")
    print("  → Check Variable_list_MINDSET_SSP.xlsx has NPISH_BASE entry")
    sys.exit(1)

print()

#==============================================================================
# STEP 2: Create IO Model and Initialize
#==============================================================================
print("STEP 2: Creating IO model and building Y_BASE...")
print("-"*80)

from SourceCode.InputOutput import IO

IO_model = IO(MRIO_BASE)

# Check if Y_BASE already exists
y_base_path = f"GLORIA_db\\v57\\2019\\SSP\\GLORIA_Y_Base_2019.mat"
if os.path.exists(y_base_path):
    print(f"⚠ WARNING: Y_BASE.mat already exists at {y_base_path}")
    response = input("Overwrite? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Aborted.")
        sys.exit(0)
    else:
        print("Proceeding with overwrite...")
        os.remove(y_base_path)
        print()

# Call initialize() - this will:
# 1. load_L_base() - build Leontief inverse
# 2. load_Y_base() - build final demand vectors from INV_BASE, NPISH_BASE, etc.
# 3. load_G_base() - build Ghosh inverse
# 4. calc_init_q() - calculate baseline output
start_time = time.time()
IO_model.initialize()
elapsed = time.time() - start_time

print()
print(f"✓ IO model initialized in {round(elapsed, 1)} seconds")
print()

#==============================================================================
# STEP 3: Verify Y_BASE.mat was created
#==============================================================================
print("STEP 3: Verifying Y_BASE.mat file...")
print("-"*80)

if os.path.exists(y_base_path):
    file_size = os.path.getsize(y_base_path) / 1024  # KB
    print(f"✓ Y_BASE.mat successfully created!")
    print(f"  Location: {y_base_path}")
    print(f"  Size: {file_size:.1f} KB")
    print()

    # Show what's in it
    print("Contents:")
    print(f"  y0 (total final demand): {IO_model.y0.shape}")
    print(f"  y_hh0 (household): {IO_model.y_hh0.shape}")
    print(f"  y_gov0 (government): {IO_model.y_gov0.shape}")
    print(f"  y_fcf0 (capital formation): {IO_model.y_fcf0.shape}")
    print(f"  y_npish (NPISH): {IO_model.y_npish.shape}")
    print(f"  y_inv (investment): {IO_model.y_inv.shape}")
    print()
    print(f"  Expected size: 960 elements (8 countries × 120 sectors)")
    print()
else:
    print(f"✗ ERROR: Y_BASE.mat was not created!")
    sys.exit(1)

#==============================================================================
# SUMMARY
#==============================================================================
print("="*80)
print("SUCCESS!")
print("="*80)
print()
print("SSP Y_BASE.mat has been created with 8 aggregated regions.")
print()
print("Next steps:")
print("  1. You can now remove INV_BASE and NPISH_BASE from Variable_list_MINDSET_SSP.xlsx")
print("     (optional - they won't be used anymore since Y_BASE.mat exists)")
print()
print("  2. Run your employment analysis - IO_model.initialize() will now load")
print("     Y_BASE.mat instead of rebuilding from components")
print()
print("="*80)
