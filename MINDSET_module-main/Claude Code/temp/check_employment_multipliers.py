"""
Check the actual employment multipliers being calculated
"""
import sys
import os
import numpy as np
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO
from SourceCode.employment import empl
from SourceCode.utils import MRIO_df_to_vec

print("="*80)
print("CHECKING EMPLOYMENT MULTIPLIERS")
print("="*80)
print()

# Load data
MRIO_BASE = exog_vars()
IO_model = IO(MRIO_BASE)
IO_model.initialize()

# Calculate employment baseline from LABOR_BASE
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_low"] = empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"]
empl_base_df["vol_high"] = empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
empl_base_df["vol_total"] = empl_base_df["vol_low"] + empl_base_df["vol_high"]

empl_base = MRIO_df_to_vec(
    empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]],
    "REG_imp", "PROD_COMM", "vol_total",
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

# Build employment model
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)

# Get country indices
country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}

# Products being invested in
invested_products = [65, 66, 67, 68, 69, 70, 86, 89, 90, 91]

print("Employment Multipliers for invested products:")
print("="*80)
print(f"{'Product':<10} {'EGY Multiplier':>18} {'MEX Multiplier':>18} {'Ratio':>12}")
print("-"*80)

egy_mult_sum = 0
mex_mult_sum = 0

for prod in invested_products:
    egy_idx = country_idx['EGY'] * 120 + (prod - 1)
    mex_idx = country_idx['MEX'] * 120 + (prod - 1)

    egy_mult = Empl_model.empl_multiplier[egy_idx]
    mex_mult = Empl_model.empl_multiplier[mex_idx]

    ratio = egy_mult / mex_mult if mex_mult != 0 else float('inf')

    print(f"{prod:<10} {egy_mult:>18.6f} {mex_mult:>18.6f} {ratio:>12.2f}x")

    egy_mult_sum += egy_mult
    mex_mult_sum += mex_mult

print("-"*80)
avg_egy = egy_mult_sum / len(invested_products)
avg_mex = mex_mult_sum / len(invested_products)
avg_ratio = avg_egy / avg_mex if avg_mex != 0 else float('inf')
print(f"{'Average':<10} {avg_egy:>18.6f} {avg_mex:>18.6f} {avg_ratio:>12.2f}x")
print()

print("="*80)
print("BREAKDOWN BY COMPONENT")
print("="*80)
print()

# Check components for a sample product (Product 90)
prod = 90
egy_idx = country_idx['EGY'] * 120 + (prod - 1)
mex_idx = country_idx['MEX'] * 120 + (prod - 1)

print(f"Product {prod} breakdown:")
print("-"*80)

# Get empl_coef
egy_coef = Empl_model.EMPL_COEF[
    (Empl_model.EMPL_COEF['REG_imp'] == 'EGY') &
    (Empl_model.EMPL_COEF['PROD_COMM'] == prod)
]['empl_coef'].values[0]

mex_coef = Empl_model.EMPL_COEF[
    (Empl_model.EMPL_COEF['REG_imp'] == 'MEX') &
    (Empl_model.EMPL_COEF['PROD_COMM'] == prod)
]['empl_coef'].values[0]

print(f"Employment coefficient (empl_coef):")
print(f"  EGY: {egy_coef:.6f}")
print(f"  MEX: {mex_coef:.6f}")
print(f"  Ratio: {egy_coef/mex_coef:.2f}x")
print()

# Get empl_base for this product
egy_empl_base = empl_base[egy_idx]
mex_empl_base = empl_base[mex_idx]

print(f"Employment baseline (empl_base) for Product {prod}:")
print(f"  EGY: {egy_empl_base:,.0f} workers")
print(f"  MEX: {mex_empl_base:,.0f} workers")
print(f"  Ratio: {egy_empl_base/mex_empl_base:.2f}x" if mex_empl_base != 0 else "  Ratio: N/A")
print()

# Get q_base for this product
egy_q_base = IO_model.q_base[egy_idx]
mex_q_base = IO_model.q_base[mex_idx]

print(f"Baseline output (q_base) for Product {prod}:")
print(f"  EGY: ${egy_q_base:,.0f} kUSD")
print(f"  MEX: ${mex_q_base:,.0f} kUSD")
print(f"  Ratio: {egy_q_base/mex_q_base:.2f}x" if mex_q_base != 0 else "  Ratio: N/A")
print()

# Calculate intensity ratio
egy_intensity = egy_empl_base / egy_q_base if egy_q_base != 0 else 0
mex_intensity = mex_empl_base / mex_q_base if mex_q_base != 0 else 0

print(f"Employment intensity (empl_base/q_base):")
print(f"  EGY: {egy_intensity:.6f} workers/kUSD")
print(f"  MEX: {mex_intensity:.6f} workers/kUSD")
print(f"  Ratio: {egy_intensity/mex_intensity:.2f}x" if mex_intensity != 0 else "  Ratio: N/A")
print()

# Calculate multiplier manually
egy_mult_manual = egy_coef * egy_intensity
mex_mult_manual = mex_coef * mex_intensity

print(f"Employment multiplier (empl_coef × intensity):")
print(f"  EGY: {egy_mult_manual:.6f}")
print(f"  MEX: {mex_mult_manual:.6f}")
print(f"  Ratio: {egy_mult_manual/mex_mult_manual:.2f}x" if mex_mult_manual != 0 else "  Ratio: N/A")
print()

print("="*80)
