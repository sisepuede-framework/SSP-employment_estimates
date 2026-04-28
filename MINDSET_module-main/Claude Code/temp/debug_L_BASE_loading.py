"""
Debug what L_BASE looks like after exog_vars loads it
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("DEBUG L_BASE LOADING")
print("="*80)
print()

from SourceCode.exog_vars_SSP import exog_vars

print("Step 1: Load MRIO_BASE")
print("-"*80)
MRIO_BASE = exog_vars()
print()

print("Step 2: Check if L_BASE was loaded")
print("-"*80)
if hasattr(MRIO_BASE, 'L_BASE'):
    print(f"✓ L_BASE exists")
    print(f"  Type: {type(MRIO_BASE.L_BASE)}")
    print(f"  Type name: {type(MRIO_BASE.L_BASE).__name__}")

    if isinstance(MRIO_BASE.L_BASE, dict):
        print(f"  Is dict: YES")
        print(f"  Keys: {list(MRIO_BASE.L_BASE.keys())}")
        if 'L_base' in MRIO_BASE.L_BASE:
            print(f"  'L_base' key exists: YES")
            print(f"  L_base data type: {type(MRIO_BASE.L_BASE['L_base'])}")
            print(f"  L_base shape: {MRIO_BASE.L_BASE['L_base'].shape}")
        else:
            print(f"  'L_base' key exists: NO")
    else:
        print(f"  Is dict: NO")
        if hasattr(MRIO_BASE.L_BASE, 'shape'):
            print(f"  Shape: {MRIO_BASE.L_BASE.shape}")
        if hasattr(MRIO_BASE.L_BASE, '__getitem__'):
            print(f"  Has __getitem__: YES (can be indexed)")
            try:
                test = MRIO_BASE.L_BASE["L_base"]
                print(f"  Can access ['L_base']: YES")
            except Exception as e:
                print(f"  Can access ['L_base']: NO - {type(e).__name__}: {e}")
else:
    print(f"✗ L_BASE does not exist")

print()

print("Step 3: Try to create IO model")
print("-"*80)
from SourceCode.InputOutput import IO

IO_model = IO(MRIO_BASE)

print(f"After IO.__init__:")
if hasattr(IO_model, 'L_BASE'):
    print(f"  IO_model.L_BASE type: {type(IO_model.L_BASE).__name__}")
    if isinstance(IO_model.L_BASE, dict):
        print(f"  Is dict: YES")
        print(f"  Keys: {list(IO_model.L_BASE.keys())}")
else:
    print(f"  IO_model.L_BASE does not exist")

print()
print("Step 4: Check what 'L_BASE' in dir(IO_model) returns")
print("-"*80)
print(f"  'L_BASE' in dir(IO_model): {'L_BASE' in dir(IO_model)}")

print()
print("Step 5: Try the problematic line manually")
print("-"*80)
try:
    if 'L_BASE' in dir(IO_model):
        print(f"  Condition is True, trying to access IO_model.L_BASE['L_base']...")
        test = IO_model.L_BASE["L_base"]
        print(f"  ✓ SUCCESS!")
        print(f"  Result type: {type(test).__name__}")
        print(f"  Result shape: {test.shape}")
    else:
        print(f"  Condition is False, would call invert_A_base() instead")
except Exception as e:
    print(f"  ✗ FAILED: {type(e).__name__}: {e}")
    print(f"  This is the error we're seeing!")
