"""
Check what regions and sectors are actually in IND_BASE
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars

print("Loading MRIO data...")
MRIO_BASE = exog_vars()

print()
print("=" * 80)
print("WHAT'S IN THE PARSED DATA?")
print("=" * 80)
print()

print("R_list (regions from parsed files):")
print(f"  {MRIO_BASE.R['Region_acronyms'].tolist()}")
print(f"  Total: {len(MRIO_BASE.R['Region_acronyms'].tolist())} regions")
print()

print("P_list (sectors):")
print(f"  Total: {len(MRIO_BASE.P['Lfd_Nr'].tolist())} sectors")
print()

print("=" * 80)
print("WHAT'S IN IND_BASE?")
print("=" * 80)
print()

print(f"IND_BASE shape: {MRIO_BASE.IND_BASE.shape}")
print(f"IND_BASE index levels: {MRIO_BASE.IND_BASE.index.names}")
print()

# Check unique regions in each index level
reg_exp = sorted(MRIO_BASE.IND_BASE.index.get_level_values('REG_exp').unique().tolist())
reg_imp = sorted(MRIO_BASE.IND_BASE.index.get_level_values('REG_imp').unique().tolist())
trad_comm = sorted(MRIO_BASE.IND_BASE.index.get_level_values('TRAD_COMM').unique().tolist())
prod_comm = sorted(MRIO_BASE.IND_BASE.index.get_level_values('PROD_COMM').unique().tolist())

print(f"Unique REG_exp in IND_BASE: {reg_exp}")
print(f"  Total: {len(reg_exp)} regions")
print()

print(f"Unique REG_imp in IND_BASE: {reg_imp}")
print(f"  Total: {len(reg_imp)} regions")
print()

print(f"Unique TRAD_COMM: {len(trad_comm)} sectors")
print(f"Unique PROD_COMM: {len(prod_comm)} sectors")
print()

print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()

r_list_set = set(MRIO_BASE.R['Region_acronyms'].tolist())
reg_exp_set = set(reg_exp)
reg_imp_set = set(reg_imp)

if reg_exp_set == r_list_set and reg_imp_set == r_list_set:
    print("✓ IND_BASE contains ONLY the 8 regions from R_list")
    print("  This is good - the data is properly filtered")
else:
    print("✗ IND_BASE contains MORE regions than R_list!")
    print(f"  R_list has {len(r_list_set)} regions: {sorted(r_list_set)}")
    print(f"  REG_exp has {len(reg_exp_set)} regions")
    print(f"  REG_imp has {len(reg_imp_set)} regions")
    print()
    print("  Extra regions in REG_exp:", sorted(reg_exp_set - r_list_set))
    print("  Extra regions in REG_imp:", sorted(reg_imp_set - r_list_set))
    print()
    print("  This explains why A_BASE is too large!")
    print("  The parsed_db_original data was NOT properly aggregated to 8 regions")
