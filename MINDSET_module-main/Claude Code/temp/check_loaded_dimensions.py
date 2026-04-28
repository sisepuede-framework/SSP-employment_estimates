"""
Check what dimensions are actually loaded when MRIO_BASE loads L_BASE
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
print("CHECKING LOADED DIMENSIONS")
print("=" * 80)
print()

print("Step 1: Loading MRIO_BASE...")
MRIO_BASE = exog_vars()
print("OK")
print()

print("Step 2: Check if L_BASE was loaded...")
if hasattr(MRIO_BASE, 'L_BASE'):
    print(f"  L_BASE loaded: YES")
    print(f"  L_BASE type: {type(MRIO_BASE.L_BASE)}")
    if hasattr(MRIO_BASE.L_BASE, 'shape'):
        print(f"  L_BASE shape: {MRIO_BASE.L_BASE.shape}")
    else:
        print(f"  L_BASE has no shape attribute (might be dict)")
else:
    print(f"  L_BASE loaded: NO")
print()

print("Step 3: Initialize IO model...")
IO_model = IO(MRIO_BASE)
print("OK")
print()

print("Step 4: Check IO_model.L_BASE...")
if hasattr(IO_model, 'L_BASE'):
    print(f"  IO_model.L_BASE exists: YES")
    print(f"  IO_model.L_BASE type: {type(IO_model.L_BASE)}")
    if hasattr(IO_model.L_BASE, 'shape'):
        print(f"  IO_model.L_BASE shape: {IO_model.L_BASE.shape}")
    else:
        print(f"  IO_model.L_BASE is not a numpy array")
else:
    print(f"  IO_model.L_BASE exists: NO")
print()

print("Step 5: Check theoretical vs actual dimensions...")
print(f"  MRIO_BASE.mrio_id length: {len(MRIO_BASE.mrio_id)}")
print(f"  MRIO_BASE.A_id length: {len(MRIO_BASE.A_id)}")
print(f"  Theoretical (COU_ID × SEC_ID): {len(MRIO_BASE.COU_ID)} × {len(MRIO_BASE.SEC_ID)} = {len(MRIO_BASE.COU_ID) * len(MRIO_BASE.SEC_ID)}")
print()

print("=" * 80)
print("ANALYSIS")
print("=" * 80)

if hasattr(IO_model, 'L_BASE') and hasattr(IO_model.L_BASE, 'shape'):
    l_dim = IO_model.L_BASE.shape[0]
    mrio_dim = len(MRIO_BASE.mrio_id)

    print(f"L_BASE is {l_dim} × {l_dim}")
    print(f"mrio_id has {mrio_dim} entries")
    print()

    if l_dim == mrio_dim:
        print("✓ Dimensions MATCH - this is correct!")
    else:
        print(f"X Dimensions MISMATCH:")
        print(f"  L_BASE expects vectors of length {l_dim}")
        print(f"  But mrio_id (used by MRIO_df_to_vec) creates vectors of length {mrio_dim}")
        print()
        print("This explains the dimension error in the test!")
