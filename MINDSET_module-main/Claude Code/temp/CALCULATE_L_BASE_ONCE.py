"""
ONE-TIME CALCULATION: Leontief Inverse Matrix (L_BASE)

This script calculates the Leontief inverse matrix and saves it to disk.
Once calculated, it will be automatically loaded for all 469 scenario runs.

BEFORE RUNNING:
1. Close all unnecessary applications (browsers, Office, etc.)
2. Save all your work
3. This may take 1-5 minutes depending on your system

WHAT IT DOES:
- Loads GLORIA inter-industry data
- Builds technical coefficient matrix A (960x960)
- Inverts to get Leontief matrix: L = (I - A)^(-1)
- Saves to: GLORIA_db\v57\2019\GLORIA_L_Base_2019.mat

MEMORY ESTIMATE: ~1-2 GB RAM needed
"""

import time
import sys
import os

# Set working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("=" * 80)
print("ONE-TIME CALCULATION: Leontief Inverse Matrix (L_BASE)")
print("=" * 80)
print()

# Import after path is set
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO

print("STEP 1: Loading GLORIA data...")
start_time = time.time()
MRIO_BASE = exog_vars()
print(f"OK - Loaded in {time.time() - start_time:.1f} seconds")
print()

print("STEP 2: Initializing IO model...")
IO_model = IO(MRIO_BASE)
print("OK")
print()

# Check if L_BASE already exists
if hasattr(IO_model, 'L_BASE'):
    print("✓ L_BASE already loaded from file!")
    print("  No calculation needed - file exists.")
    print(f"  Matrix size: {IO_model.L_BASE.shape}")
    sys.exit(0)

print("STEP 3: Building technical coefficient matrix (A)...")
print("This creates the inter-industry linkages matrix")
step_start = time.time()
IO_model.build_A_base()
print(f"OK - Built A matrix: {IO_model.A_BASE.shape}")
print(f"  Time: {time.time() - step_start:.1f} seconds")
print()

print("STEP 4: Calculating Leontief inverse: L = (I - A)^(-1)")
print("  This is the memory-intensive step")
print("  Progress will be shown below...")
print()

try:
    step_start = time.time()
    IO_model.invert_A_base()

    print()
    print("=" * 80)
    print("✓ SUCCESS! L_BASE calculated and saved")
    print("=" * 80)
    print(f"Matrix size: {IO_model.L_BASE.shape}")
    print(f"Total time: {time.time() - start_time:.1f} seconds")
    print()
    print("File saved to:")
    print(f"  GLORIA_db\\v57\\2019\\parsed_db_original\\GLORIA_L_Base_2019.mat")
    print()
    print("This matrix will now be automatically loaded for all 469 scenario runs.")
    print("You will NOT need to run this script again.")
    print()

except MemoryError:
    print()
    print("=" * 80)
    print("✗ MEMORY ERROR")
    print("=" * 80)
    print()
    print("Not enough RAM to complete the calculation.")
    print()
    print("Options:")
    print("1. Close MORE applications and try again")
    print("2. Restart your computer to clear memory")
    print("3. Use a machine with more RAM (need ~16GB total)")
    print("4. Ask MINDSET/GLORIA provider for pre-calculated L_BASE file")
    print()
    sys.exit(1)

except Exception as e:
    print()
    print("=" * 80)
    print("✗ ERROR")
    print("=" * 80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print()
    sys.exit(1)
