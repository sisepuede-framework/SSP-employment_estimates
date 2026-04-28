"""
Check Employment_country mapping in HH_CONS_COU
"""
import sys
import os
import pandas as pd
sys.path.insert(0, '.')
os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

from SourceCode.exog_vars_SSP import exog_vars

MRIO_BASE = exog_vars()

print("="*80)
print("EMPLOYMENT_COUNTRY MAPPING")
print("="*80)
print()

print("HH_CONS_COU full table:")
print("-"*80)
print(MRIO_BASE.HH_CONS_COU[['Country_Code', 'GLORIA_Country', 'Employment_country', 'Investment_country']])
print()

print("="*80)
print("INTERPRETATION")
print("="*80)
print()
print("Employment_country: Which GLORIA country's employment coefficients to use")
print("for each aggregated country.")
print()
print("User's hypothesis: Each of the 8 countries (BGR, BLZ, EGY, LBY, MAR, MEX, UGA)")
print("should use their own employment coefficients.")
print("ROW uses China's coefficients as a proxy.")
print()

# Check EMPL_COEF columns to see which countries are available
print("Available employment countries in EMPL_COEF:")
print("-"*80)
empl_coef_countries = list(MRIO_BASE.EMPL_COEF.columns[2:])  # Skip first 2 columns
print(f"Total: {len(empl_coef_countries)} countries")
print()
print("First 20:", empl_coef_countries[:20])
print("...")
print()

# Check if our 7 countries + China are in the list
our_countries = ['Bulgaria', 'Belize', 'Egypt', 'Libya', 'Morocco', 'Mexico', 'Uganda', 'China']
print("Checking for our countries:")
for country in our_countries:
    if country in empl_coef_countries:
        print(f"  [OK] {country} found")
    else:
        print(f"  [MISSING] {country} not found")
print()
