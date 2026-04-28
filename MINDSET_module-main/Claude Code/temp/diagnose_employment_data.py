"""
Diagnose employment data quality across countries
"""
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.utils import MRIO_df_to_vec

MRIO = exog_vars()

print("="*80)
print("DIAGNOSING EMPLOYMENT DATA BY COUNTRY")
print("="*80)
print()

# Calculate employment baseline by country
empl_base_df = MRIO.LABOR_BASE.copy()
empl_base_df["vol_total"] = (empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"] +
                              empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"])

# Calculate output baseline by country
output_df = MRIO.output.reset_index()

# Group by country
print("Employment and Output by Country:")
print("-"*80)
print(f"{'Country':<10} {'Employment':>15} {'Output (kUSD)':>15} {'Emp/Output':>12}")
print("-"*80)

for country in MRIO.COU_ID:
    country_empl = empl_base_df[empl_base_df['REG_imp'] == country]['vol_total'].sum()
    country_output = output_df[output_df['REG_imp'] == country]['output'].sum()

    emp_per_output = country_empl / country_output if country_output > 0 else 0

    print(f"{country:<10} {country_empl:>15,.0f} {country_output:>15,.0f} {emp_per_output:>12,.2f}")

print()
print("="*80)
print("EMPLOYMENT COEFFICIENTS BY COUNTRY")
print("="*80)
print()

# Check EMPL_COEF
if hasattr(MRIO, 'EMPL_COEF'):
    print("Sample EMPL_COEF for each country (first 5 sectors):")
    print("-"*80)

    for country in ['MEX', 'EGY', 'MAR', 'BGR']:
        country_coef = MRIO.EMPL_COEF[MRIO.EMPL_COEF.iloc[:, 0].str.contains(country, na=False)]
        if len(country_coef) > 0:
            print(f"\n{country}:")
            print(country_coef.head())
else:
    print("EMPL_COEF not found")

print()
print("="*80)
print("INTERPRETATION")
print("="*80)
print()
print("If Emp/Output ratio varies wildly across countries (e.g., 10x difference),")
print("this suggests data quality issues with the SSP aggregated employment data.")
