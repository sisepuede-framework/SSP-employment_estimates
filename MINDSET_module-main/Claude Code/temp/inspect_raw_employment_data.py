"""
Inspect raw employment and mapping data to understand why only ROW appears
"""
import pandas as pd
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("LOADING RAW DATA")
print("="*80)

# Load the employment data directly
empl_path = "GLORIA_db/v57/2019/parsed_db_original/empl_data.pkl"
empl_data = pd.read_pickle(empl_path)

print(f"\nEmployment data (empl_data.pkl):")
print(f"Shape: {empl_data.shape}")
print(f"Columns: {list(empl_data.columns)}")
print(f"\nFirst 10 rows:")
print(empl_data.head(10))
print(f"\nUnique REG_imp values: {len(empl_data['REG_imp'].unique())}")
print(f"First 20 regions: {sorted(empl_data['REG_imp'].unique())[:20]}")

# Now load what exog_vars loads as EMPL_COEF
from SourceCode.exog_vars_SSP import exog_vars

print("\n" + "="*80)
print("LOADING THROUGH EXOG_VARS (as EMPL_COEF)")
print("="*80)

MRIO_BASE = exog_vars()

print(f"\nEMPL_COEF loaded by exog_vars:")
print(f"Type: {type(MRIO_BASE.EMPL_COEF)}")
print(f"Shape: {MRIO_BASE.EMPL_COEF.shape}")
print(f"Columns: {list(MRIO_BASE.EMPL_COEF.columns)}")
print(f"\nFirst 10 rows:")
print(MRIO_BASE.EMPL_COEF.head(10))

# Check if EMPL_COEF is the same as empl_data
if MRIO_BASE.EMPL_COEF.equals(empl_data):
    print("\n✓ EMPL_COEF is identical to empl_data.pkl")
else:
    print("\n✗ EMPL_COEF is DIFFERENT from empl_data.pkl")
    print("  (Variable_list may point to a different file)")

print("\n" + "="*80)
print("CHECKING HH_CONS_COU MAPPING")
print("="*80)

print(f"\nHH_CONS_COU:")
print(f"Shape: {MRIO_BASE.HH_CONS_COU.shape}")
print(f"Columns: {list(MRIO_BASE.HH_CONS_COU.columns)}")
print(f"\nFirst 20 rows:")
print(MRIO_BASE.HH_CONS_COU.head(20))

# Check our 7 countries
print("\n" + "="*80)
print("MAPPINGS FOR OUR 7 COUNTRIES")
print("="*80)

selected_countries = ['BGR', 'BLZ', 'EGY', 'LBY', 'MAR', 'MEX', 'UGA']

for country in selected_countries:
    matches = MRIO_BASE.HH_CONS_COU[MRIO_BASE.HH_CONS_COU['Country_Code'] == country]
    if len(matches) > 0:
        empl_country = matches['Employment_country'].iloc[0]
        print(f"{country} → Employment_country: '{empl_country}'")
    else:
        print(f"{country} → NO MAPPING FOUND")

print("\n" + "="*80)
print("UNIQUE EMPLOYMENT COUNTRIES")
print("="*80)

unique_empl_countries = MRIO_BASE.HH_CONS_COU['Employment_country'].unique()
print(f"\nTotal unique Employment_country values: {len(unique_empl_countries)}")
print(f"\nAll Employment_country values:")
for ec in sorted(unique_empl_countries):
    count = len(MRIO_BASE.HH_CONS_COU[MRIO_BASE.HH_CONS_COU['Employment_country'] == ec])
    print(f"  '{ec}': {count} GLORIA countries map to this")
