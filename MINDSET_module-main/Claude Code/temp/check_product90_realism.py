"""
Check if Product 90's employment and output are realistic for EGY vs MEX
"""
import sys
import os
import numpy as np
import pandas as pd
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.InputOutput import IO

print("="*80)
print("PRODUCT 90 REALISM CHECK")
print("="*80)
print()

# Load data
MRIO_BASE = exog_vars()
IO_model = IO(MRIO_BASE)
IO_model.initialize()

# Product 90 is "Renting of construction equipment with operator"
print("Product 90: Renting of construction equipment with operator")
print()

# Calculate employment baseline
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_total"] = (empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"] +
                              empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"])

country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}

print("="*80)
print("EGY vs MEX COMPARISON FOR PRODUCT 90")
print("="*80)
print()

for country in ['EGY', 'MEX']:
    idx = country_idx[country]
    prod_idx = idx * 120 + 89  # Product 90 is index 89 (0-based)

    # Get all country data
    start_idx = idx * 120
    end_idx = start_idx + 120

    # Product 90 data
    prod_empl = empl_base_df[
        (empl_base_df['REG_imp'] == country) &
        (empl_base_df['PROD_COMM'] == 90)
    ]['vol_total'].values[0]

    prod_output = IO_model.q_base[prod_idx]

    # Total country data
    total_empl = empl_base_df[empl_base_df['REG_imp'] == country]['vol_total'].sum()
    total_output = IO_model.q_base[start_idx:end_idx].sum()

    # Calculate shares
    empl_share = (prod_empl / total_empl * 100) if total_empl > 0 else 0
    output_share = (prod_output / total_output * 100) if total_output > 0 else 0
    intensity = (prod_empl / prod_output) if prod_output > 0 else 0

    print(f"{country}:")
    print(f"  Total country employment:    {total_empl:>15,.0f} workers")
    print(f"  Total country output:        {total_output:>15,.0f} kUSD")
    print(f"  Country intensity:           {total_empl/total_output:>15.4f} workers/kUSD")
    print()
    print(f"  Product 90 employment:       {prod_empl:>15,.0f} workers ({empl_share:.2f}% of country)")
    print(f"  Product 90 output:           {prod_output:>15,.0f} kUSD ({output_share:.2f}% of country)")
    print(f"  Product 90 intensity:        {intensity:>15.4f} workers/kUSD")
    print()

print("="*80)
print("ANALYSIS")
print("="*80)
print()

egy_prod_empl = empl_base_df[(empl_base_df['REG_imp'] == 'EGY') & (empl_base_df['PROD_COMM'] == 90)]['vol_total'].values[0]
mex_prod_empl = empl_base_df[(empl_base_df['REG_imp'] == 'MEX') & (empl_base_df['PROD_COMM'] == 90)]['vol_total'].values[0]
egy_prod_output = IO_model.q_base[country_idx['EGY'] * 120 + 89]
mex_prod_output = IO_model.q_base[country_idx['MEX'] * 120 + 89]

print(f"Employment ratio (MEX/EGY): {mex_prod_empl/egy_prod_empl:.2f}x")
print(f"Output ratio (MEX/EGY):     {mex_prod_output/egy_prod_output:.2f}x")
print()
print("If MEX has 6.5x more workers AND 48x more output, then MEX's Product 90")
print("is MUCH more capital-intensive (mechanized) than EGY's.")
print()
print("This is plausible IF:")
print("- MEX has highly mechanized construction equipment industry")
print("- EGY has labor-intensive construction equipment sector")
print()
print("HOWEVER, the 7.3x intensity difference seems extreme. This might indicate:")
print("1. Data quality issue in original GLORIA for Product 90")
print("2. Aggregation issue specific to this product")
print("3. Very different industrial structures (plausible but unusual)")
