"""
Deep diagnostic: Track exactly what happens in employment.py build_empl_coef()
"""
import sys
import os
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("DEEP DIAGNOSTIC: EMPLOYMENT MERGE")
print("="*80)
print()

# Load MRIO data
from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()

print("STEP 1: What EMPL_COEF looks like BEFORE employment.py processes it")
print("-"*80)
print(f"Type: {type(MRIO_BASE.EMPL_COEF)}")
print(f"Shape: {MRIO_BASE.EMPL_COEF.shape}")
print(f"Columns: {list(MRIO_BASE.EMPL_COEF.columns)}")
print(f"\nFirst 5 rows:")
print(MRIO_BASE.EMPL_COEF.head())
print()

print("STEP 2: What HH_CONS_COU looks like")
print("-"*80)
print(f"Shape: {MRIO_BASE.HH_CONS_COU.shape}")
print(f"Columns: {list(MRIO_BASE.HH_CONS_COU.columns)}")
print(f"\nAll rows:")
print(MRIO_BASE.HH_CONS_COU)
print()

print("STEP 3: Manually replicate employment.py build_empl_coef()")
print("-"*80)

EMPL_COEF = MRIO_BASE.EMPL_COEF.copy()

print("3a. Set index to 'Unnamed: 0'")
EMPL_COEF = EMPL_COEF.set_index("Unnamed: 0")
print(f"   Shape: {EMPL_COEF.shape}, Index: {EMPL_COEF.index.name}")

print("3b. Drop 'Unnamed: 1' column")
EMPL_COEF = EMPL_COEF.drop(columns=["Unnamed: 1"])
print(f"   Shape: {EMPL_COEF.shape}")
print(f"   Columns: {list(EMPL_COEF.columns)}")

print("3c. Reset index")
EMPL_COEF = EMPL_COEF.reset_index()
print(f"   Shape: {EMPL_COEF.shape}")
print(f"   Columns: {list(EMPL_COEF.columns)}")

print("3d. Rename 'Unnamed: 0' to 'PROD_COMM'")
EMPL_COEF = EMPL_COEF.rename(columns={"Unnamed: 0": "PROD_COMM"})
print(f"   Columns: {list(EMPL_COEF.columns)}")

print("3e. Melt (id_vars='PROD_COMM', value_vars=remaining columns)")
value_cols = EMPL_COEF.columns[1:]
print(f"   Melting columns: {list(value_cols)}")
EMPL_COEF = EMPL_COEF.melt(id_vars='PROD_COMM', value_vars=value_cols)
print(f"   Shape after melt: {EMPL_COEF.shape}")
print(f"   Columns: {list(EMPL_COEF.columns)}")
print(f"   Unique values in 'variable' column: {EMPL_COEF['variable'].unique()}")

print("3f. Rename columns")
EMPL_COEF = EMPL_COEF.rename(columns={"variable": "GLORIA_Country", "value": "empl_coef"})
print(f"   Columns: {list(EMPL_COEF.columns)}")
print(f"   Unique GLORIA_Country values: {sorted(EMPL_COEF['GLORIA_Country'].unique())}")
print(f"\nFirst 10 rows of EMPL_COEF before merge:")
print(EMPL_COEF.head(10))

print("\n3g. Prepare HH_CONS_COU for merge")
merge_data = MRIO_BASE.HH_CONS_COU.loc[:,['Country_Code','Employment_country']].rename(columns={'Employment_country':'GLORIA_Country'})
print(f"   Merge data shape: {merge_data.shape}")
print(f"   Merge data columns: {list(merge_data.columns)}")
print(f"   Unique GLORIA_Country in merge data: {sorted(merge_data['GLORIA_Country'].unique())}")
print(f"\nMerge data:")
print(merge_data)

print("\n3h. Perform LEFT MERGE on GLORIA_Country")
print(f"   EMPL_COEF has {len(EMPL_COEF)} rows with GLORIA_Country values: {sorted(EMPL_COEF['GLORIA_Country'].unique())}")
print(f"   HH_CONS_COU has {len(merge_data)} rows with GLORIA_Country values: {sorted(merge_data['GLORIA_Country'].unique())}")

# Check for matches
empl_countries = set(EMPL_COEF['GLORIA_Country'].unique())
hh_countries = set(merge_data['GLORIA_Country'].unique())
matches = empl_countries & hh_countries
no_match_empl = empl_countries - hh_countries
no_match_hh = hh_countries - empl_countries

print(f"\n   Countries in BOTH: {sorted(matches)}")
print(f"   Countries ONLY in EMPL_COEF: {sorted(no_match_empl)}")
print(f"   Countries ONLY in HH_CONS_COU: {sorted(no_match_hh)}")

EMPL_COEF = EMPL_COEF.merge(merge_data, how='left', on=["GLORIA_Country"])
print(f"\n   After merge shape: {EMPL_COEF.shape}")
print(f"   Columns: {list(EMPL_COEF.columns)}")
print(f"\nFirst 10 rows after merge:")
print(EMPL_COEF.head(10))

print("\n3i. Rename Country_Code to REG_imp")
EMPL_COEF = EMPL_COEF.rename(columns={"Country_Code": "REG_imp"})
print(f"   Columns: {list(EMPL_COEF.columns)}")

print("\n3j. Select columns")
EMPL_COEF = EMPL_COEF.loc[:,["REG_imp","PROD_COMM","empl_coef"]]
print(f"   Shape: {EMPL_COEF.shape}")

print("\n3k. Drop rows where REG_imp is NaN")
before = len(EMPL_COEF)
EMPL_COEF = EMPL_COEF[~EMPL_COEF['REG_imp'].isna()].copy()
after = len(EMPL_COEF)
print(f"   Dropped {before - after} rows with NaN REG_imp")
print(f"   Final shape: {EMPL_COEF.shape}")
print(f"   Unique REG_imp: {sorted(EMPL_COEF['REG_imp'].unique()) if len(EMPL_COEF) > 0 else 'NONE'}")

print("\n" + "="*80)
print("DIAGNOSIS")
print("="*80)

if len(EMPL_COEF) == 0:
    print("\n❌ PROBLEM: Final EMPL_COEF is EMPTY")
    print("\nThis means the merge found NO MATCHES between:")
    print(f"  - EMPL_COEF GLORIA_Country values: {sorted(empl_countries)}")
    print(f"  - HH_CONS_COU Employment_country values: {sorted(hh_countries)}")
    print("\nPossible causes:")
    print("  1. Column names in EMPL_COEF don't match Employment_country in HH_CONS_COU")
    print("  2. HH_CONS_COU was filtered before employment mappings were added")
    print("  3. Employment_country update didn't work correctly")
else:
    print(f"\n✓ SUCCESS: EMPL_COEF has {len(EMPL_COEF)} rows")
    print(f"   Countries: {sorted(EMPL_COEF['REG_imp'].unique())}")
