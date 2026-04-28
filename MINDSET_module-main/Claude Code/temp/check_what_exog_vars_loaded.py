"""
Check what exog_vars_SSP actually loaded for INV_BASE and NPISH_BASE
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("Check what exog_vars_SSP loaded")
print("="*80)
print()

from SourceCode.exog_vars_SSP import exog_vars

print("Loading MRIO_BASE...")
MRIO_BASE = exog_vars()
print()

print("-"*80)
print("INV_BASE:")
print("-"*80)
if hasattr(MRIO_BASE, 'INV_BASE'):
    print(f"✓ INV_BASE exists")
    print(f"  Type: {type(MRIO_BASE.INV_BASE)}")
    print(f"  Shape: {MRIO_BASE.INV_BASE.shape}")
    print(f"  Columns: {list(MRIO_BASE.INV_BASE.columns)}")
    if hasattr(MRIO_BASE.INV_BASE, 'index'):
        print(f"  Index names: {MRIO_BASE.INV_BASE.index.names}")
    print(f"\nFirst 3 rows:")
    print(MRIO_BASE.INV_BASE.head(3))
else:
    print("✗ INV_BASE does NOT exist")

print()
print("-"*80)
print("NPISH_BASE:")
print("-"*80)
if hasattr(MRIO_BASE, 'NPISH_BASE'):
    print(f"✓ NPISH_BASE exists")
    print(f"  Type: {type(MRIO_BASE.NPISH_BASE)}")
    print(f"  Shape: {MRIO_BASE.NPISH_BASE.shape}")
    print(f"  Columns: {list(MRIO_BASE.NPISH_BASE.columns)}")
    if hasattr(MRIO_BASE.NPISH_BASE, 'index'):
        print(f"  Index names: {MRIO_BASE.NPISH_BASE.index.names}")
    print(f"\nFirst 3 rows:")
    print(MRIO_BASE.NPISH_BASE.head(3))
else:
    print("✗ NPISH_BASE does NOT exist")

print()
print("-"*80)
print("Test groupby on loaded INV_BASE:")
print("-"*80)
if hasattr(MRIO_BASE, 'INV_BASE'):
    try:
        result = MRIO_BASE.INV_BASE.groupby(['REG_exp','TRAD_COMM']).agg({'INV':'sum'}).reset_index()
        print(f"✓ SUCCESS! Result shape: {result.shape}")
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        print(f"\nThis means INV_BASE has wrong structure!")
        print(f"Expected column 'INV' but columns are: {list(MRIO_BASE.INV_BASE.columns)}")
