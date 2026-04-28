"""
Check what regions are actually in the data
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO

print("Loading MRIO...")
MRIO_BASE = exog_vars()

print()
print("=" * 80)
print("REGIONS IN PARSED GLORIA DATA")
print("=" * 80)
print(f"R_list (from parsed data): {MRIO_BASE.R['Region_acronyms'].tolist()}")
print(f"Total regions: {len(MRIO_BASE.R['Region_acronyms'].tolist())}")
print()

print("=" * 80)
print("IND_BASE INDEX LEVELS")
print("=" * 80)
print(f"IND_BASE shape: {MRIO_BASE.IND_BASE.shape}")
print(f"IND_BASE index names: {MRIO_BASE.IND_BASE.index.names}")
print()

# Check unique values in each index level
print("Unique values in IND_BASE index levels:")
print(f"  REG_exp: {sorted(MRIO_BASE.IND_BASE.index.get_level_values('REG_exp').unique().tolist())}")
print(f"  REG_imp: {sorted(MRIO_BASE.IND_BASE.index.get_level_values('REG_imp').unique().tolist())}")
print(f"  TRAD_COMM: {len(MRIO_BASE.IND_BASE.index.get_level_values('TRAD_COMM').unique())} sectors")
print(f"  PROD_COMM: {len(MRIO_BASE.IND_BASE.index.get_level_values('PROD_COMM').unique())} sectors")
print()

print("=" * 80)
print("CHECK: Is ROW in the data?")
print("=" * 80)
regions_in_data = MRIO_BASE.R['Region_acronyms'].tolist()
if 'ROW' in regions_in_data:
    print("YES - ROW is in R_list")
else:
    print("NO - ROW is NOT in R_list")
    print("This might be the issue!")
print()

print("=" * 80)
print("INITIALIZE IO AND CHECK")
print("=" * 80)
IO_model = IO(MRIO_BASE)
print(f"IO_model.R_list: {IO_model.R_list}")
print(f"IO_model.P_list length: {len(IO_model.P_list)}")
print(f"IO_model.DIMS: {IO_model.DIMS}")
