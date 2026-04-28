"""
Examine the default INV_CONV matrix structure to understand
if sector→product conversion is mostly diagonal (identity-like)
"""
import sys
import os
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars

print("="*80)
print("EXAMINING INV_CONV MATRIX")
print("="*80)
print()

MRIO_BASE = exog_vars()

print("INV_CONV structure:")
print(f"  Type: {type(MRIO_BASE.INV_CONV)}")
print(f"  Shape: {MRIO_BASE.INV_CONV.shape if hasattr(MRIO_BASE.INV_CONV, 'shape') else 'N/A'}")
print()

if isinstance(MRIO_BASE.INV_CONV, pd.DataFrame):
    print("Columns:", list(MRIO_BASE.INV_CONV.columns))
    print()
    print("First 10 rows:")
    print(MRIO_BASE.INV_CONV.head(10))
    print()

    # Check if it's sparse (mostly zeros)
    if 'input_coeff' in MRIO_BASE.INV_CONV.columns:
        nonzero = (MRIO_BASE.INV_CONV['input_coeff'] > 0).sum()
        total = len(MRIO_BASE.INV_CONV)
        print(f"Sparsity: {nonzero}/{total} non-zero entries ({nonzero/total*100:.1f}%)")
        print()

        # Check if diagonal entries are 1.0
        diagonal_check = []
        for sector in range(1, 121):
            sector_data = MRIO_BASE.INV_CONV[
                (MRIO_BASE.INV_CONV['PROD_COMM'] == str(sector)) &
                (MRIO_BASE.INV_CONV['TRAD_COMM'] == str(sector))
            ]
            if len(sector_data) > 0:
                coeff = sector_data['input_coeff'].iloc[0]
                diagonal_check.append(coeff)

        diagonal_array = np.array(diagonal_check)
        print(f"Diagonal entries (sector investing in itself):")
        print(f"  Count: {len(diagonal_array)}")
        print(f"  Mean: {diagonal_array.mean():.4f}")
        print(f"  Std: {diagonal_array.std():.4f}")
        print(f"  Min: {diagonal_array.min():.4f}")
        print(f"  Max: {diagonal_array.max():.4f}")
        print()

        near_one = (np.abs(diagonal_array - 1.0) < 0.1).sum()
        print(f"  Entries near 1.0 (within 0.1): {near_one}/{len(diagonal_array)}")
        print()

print("="*80)
print("INTERPRETATION")
print("="*80)
print()
print("If diagonal entries are mostly 1.0:")
print("  → INV_CONV is mostly identity (sector N → product N)")
print("  → Putting product codes in 'Sector investing code*' would work")
print("  → Because 'Sector 55 invests' converts to 'Product 55'")
print()
print("If diagonal entries are NOT 1.0:")
print("  → INV_CONV redistributes significantly")
print("  → User's approach (product codes in sector field) is incorrect")
