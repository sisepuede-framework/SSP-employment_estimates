"""
Test the build_A_base with detailed output
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO

print("Step 1: Loading MRIO...")
MRIO_BASE = exog_vars()
print(f"  Regions: {MRIO_BASE.R['Region_acronyms'].tolist()}")
print(f"  Number of regions: {len(MRIO_BASE.R['Region_acronyms'].tolist())}")

print("\nStep 2: Initialize IO model...")
IO_model = IO(MRIO_BASE)
print(f"  IO_model.R_list: {IO_model.R_list}")
print(f"  IO_model.DIMS: {IO_model.DIMS}")

print("\nStep 3: Check IND_BASE before filtering...")
print(f"  IND_BASE shape: {IO_model.IND_BASE.shape}")
print(f"  IND_BASE index names: {IO_model.IND_BASE.index.names}")

# Check unique regions in IND_BASE
reg_exp_unique = IO_model.IND_BASE.index.get_level_values('REG_exp').unique()
reg_imp_unique = IO_model.IND_BASE.index.get_level_values('REG_imp').unique()
print(f"  Unique REG_exp in IND_BASE: {sorted(reg_exp_unique.tolist())}")
print(f"  Unique REG_imp in IND_BASE: {sorted(reg_imp_unique.tolist())}")

print("\nStep 4: Call build_A_base()...")
try:
    IO_model.build_A_base()
    print(f"  SUCCESS!")
    print(f"  A_BASE shape: {IO_model.A_BASE.shape}")
    print(f"  A_BASE type: {type(IO_model.A_BASE)}")

    # Check if matrix is singular
    import numpy as np
    I = np.identity(len(IO_model.A_BASE))
    I_minus_A = I - IO_model.A_BASE
    det = np.linalg.det(I_minus_A)
    print(f"  Determinant of (I - A): {det}")
    if abs(det) < 1e-10:
        print(f"  WARNING: Matrix is singular or near-singular!")
    else:
        print(f"  OK: Matrix is invertible")

except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
