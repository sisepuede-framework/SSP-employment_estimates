"""
Verify A matrix dimensions BEFORE calculating L_BASE
This ensures we're using the correct dimensions (960x960, not 19680x19680)
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO

print("=" * 80)
print("DIMENSION VERIFICATION")
print("=" * 80)
print()

print("Loading MRIO data...")
MRIO_BASE = exog_vars()
print("OK")
print()

print("Initializing IO model...")
IO_model = IO(MRIO_BASE)
print("OK")
print()

print("Building A matrix (technical coefficients)...")
IO_model.build_A_base()
print("OK")
print()

print("=" * 80)
print("DIMENSIONS CHECK")
print("=" * 80)
print()

print(f"A_BASE shape: {IO_model.A_BASE.shape}")
print()

# Expected dimensions
expected_size = 960  # Based on actual active country-sector pairs
theoretical_size = 19680  # 164 countries × 120 sectors

if IO_model.A_BASE.shape[0] == expected_size:
    print(f"✓ CORRECT! Matrix is {expected_size}x{expected_size}")
    print()
    print(f"This will create an L_BASE file of approximately:")
    matrix_elements = expected_size * expected_size
    bytes_needed = matrix_elements * 8  # float64
    mb_needed = bytes_needed / (1024 * 1024)
    print(f"  Size: ~{mb_needed:.1f} MB")
    print()
    print("You can safely run CALCULATE_L_BASE_ONCE.py now.")
    sys.exit(0)

elif IO_model.A_BASE.shape[0] == theoretical_size:
    print(f"X ERROR! Matrix is {theoretical_size}x{theoretical_size} (WRONG!)")
    print()
    print(f"This would create an L_BASE file of:")
    matrix_elements = theoretical_size * theoretical_size
    bytes_needed = matrix_elements * 8
    gb_needed = bytes_needed / (1024 * 1024 * 1024)
    print(f"  Size: ~{gb_needed:.1f} GB (TOO LARGE!)")
    print()
    print("DO NOT run CALCULATE_L_BASE_ONCE.py yet.")
    print("The dimension fix did not work correctly.")
    sys.exit(1)

else:
    print(f"? UNEXPECTED: Matrix is {IO_model.A_BASE.shape[0]}x{IO_model.A_BASE.shape[1]}")
    print()
    print(f"Expected either {expected_size} or {theoretical_size}")
    sys.exit(1)
