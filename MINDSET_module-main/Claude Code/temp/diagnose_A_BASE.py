"""
Diagnose what's happening in build_A_base
"""
import time
import sys
import os
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO

print("Loading GLORIA data...")
MRIO_BASE = exog_vars()
print("Initializing IO model...")
IO_model = IO(MRIO_BASE)

print()
print("=" * 80)
print("STEP 1: Check dimensions before build_A_base")
print("=" * 80)
print(f"R_list length: {len(IO_model.R_list)}")
print(f"P_list length: {len(IO_model.P_list)}")
print(f"Expected dimensions: {len(IO_model.R_list)} × {len(IO_model.P_list)} = {len(IO_model.R_list) * len(IO_model.P_list)}")
print(f"IO_model.DIMS: {IO_model.DIMS}")
print()

print("=" * 80)
print("STEP 2: Build A_BASE")
print("=" * 80)

try:
    # Get IND_BASE info
    print("IND_BASE info:")
    print(f"  Shape: {IO_model.IND_BASE.shape}")
    print(f"  Index names: {IO_model.IND_BASE.index.names}")
    print()

    # Extract a_bp and unstack
    A_BASE_df = IO_model.IND_BASE.loc[:, ["a_bp"]]
    print("After extracting a_bp:")
    print(f"  Shape: {A_BASE_df.shape}")
    print()

    A_BASE_df = A_BASE_df.unstack(level=["REG_imp","PROD_COMM"])
    print("After unstacking:")
    print(f"  Shape: {A_BASE_df.shape}")
    print(f"  Index length (rows): {len(A_BASE_df.index)}")
    print(f"  Columns length: {len(A_BASE_df.columns)}")
    print()

    A_BASE_df.columns = A_BASE_df.columns.droplevel(0)

    # Create actual pairs
    actual_regions = IO_model.R_list
    actual_sectors = IO_model.P_list
    actual_pairs = [(r, s) for r in actual_regions for s in actual_sectors]

    print("Actual pairs to use:")
    print(f"  Number of pairs: {len(actual_pairs)}")
    print(f"  First 5 pairs: {actual_pairs[:5]}")
    print()

    print("Attempting reindex...")
    A_BASE_reindexed = A_BASE_df.reindex(index=actual_pairs, columns=actual_pairs, fill_value=0)

    print("After reindex:")
    print(f"  Shape: {A_BASE_reindexed.shape}")
    print(f"  Dtype: {A_BASE_reindexed.dtypes.unique()}")
    print()

    print("Converting to numpy...")
    A_BASE = A_BASE_reindexed.to_numpy()

    print("Final A_BASE:")
    print(f"  Type: {type(A_BASE)}")
    print(f"  Shape: {A_BASE.shape}")
    print(f"  Dtype: {A_BASE.dtype}")
    print(f"  Contains NaN: {np.isnan(A_BASE).any()}")
    print(f"  Contains Inf: {np.isinf(A_BASE).any()}")
    print(f"  Min value: {A_BASE.min()}")
    print(f"  Max value: {A_BASE.max()}")
    print()

    print("=" * 80)
    print("SUCCESS - A_BASE built correctly")
    print("=" * 80)

except Exception as e:
    print()
    print("=" * 80)
    print("ERROR during build_A_base")
    print("=" * 80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    print()
    print("Full traceback:")
    traceback.print_exc()
