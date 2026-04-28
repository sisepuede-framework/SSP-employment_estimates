import pandas as pd
import numpy as np
import sys
import os

# Add MINDSET to path
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.utils import resolve_comma, resolve_hyphen, resolve_all

# Load MRIO data
print("Loading MRIO data...")
MRIO_BASE = exog_vars()
print(f"Loaded. Countries: {len(MRIO_BASE.COU_ID)}, Sectors: {len(MRIO_BASE.SEC_ID)}\n")

# Read investment data
scenario_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
print(f"Reading: {scenario_file}")
print()

# Step 1: Read Excel
inv_exog = pd.read_excel(scenario_file, sheet_name='Investment by')
inv_exog = inv_exog[['Country ISO*','Sector investing code*','Value*','Type*']]
inv_exog.columns = ['REG_imp','PROD_COMM','Value','Type']

print("AFTER READING EXCEL:")
print(f"  Rows: {len(inv_exog)}")
print(f"  Non-zero values: {(inv_exog['Value'] != 0).sum()}")
print(f"  NaN in PROD_COMM: {inv_exog['PROD_COMM'].isna().sum()}")
print()

# Step 2: Add line numbers
inv_exog['Line'] = np.arange(len(inv_exog)).tolist()

# Step 3: Resolve comma in REG_imp
print("STEP: resolve_comma(REG_imp)...")
inv_exog = resolve_comma(inv_exog, "REG_imp")
print(f"  Rows after: {len(inv_exog)}")
print(f"  Non-zero values: {(inv_exog['Value'] != 0).sum()}")
print()

# Step 4: Resolve "ALL" in REG_imp
print("STEP: resolve_all(REG_imp)...")
inv_exog = resolve_all(inv_exog, "REG_imp", MRIO_BASE.COU_ID)
print(f"  Rows after: {len(inv_exog)}")
print(f"  Non-zero values: {(inv_exog['Value'] != 0).sum()}")
print()

# Step 5: Resolve comma in PROD_COMM
print("STEP: resolve_comma(PROD_COMM)...")
inv_exog = resolve_comma(inv_exog, "PROD_COMM")
print(f"  Rows after: {len(inv_exog)}")
print(f"  Non-zero values: {(inv_exog['Value'] != 0).sum()}")
print()

# Step 6: Resolve hyphen in PROD_COMM
print("STEP: resolve_hyphen(PROD_COMM)...")
inv_exog = resolve_hyphen(inv_exog, "PROD_COMM")
print(f"  Rows after: {len(inv_exog)}")
print(f"  Non-zero values: {(inv_exog['Value'] != 0).sum()}")
print()

# Step 7: Resolve "ALL" in PROD_COMM
print("STEP: resolve_all(PROD_COMM)...")
inv_exog = resolve_all(inv_exog, "PROD_COMM", [x for x in np.arange(1,121)])
print(f"  Rows after: {len(inv_exog)}")
print(f"  Non-zero values: {(inv_exog['Value'] != 0).sum()}")
print()

# Final result
print("=" * 80)
print("FINAL RESULT:")
print("=" * 80)
if len(inv_exog) == 0 or inv_exog['Value'].sum() == 0:
    print("ERROR: No investment data!")
else:
    print(f"SUCCESS: {len(inv_exog)} rows, ${inv_exog['Value'].sum():,.2f} total investment")
    print()
    print("Non-zero entries:")
    non_zero = inv_exog[inv_exog['Value'] != 0]
    for idx, row in non_zero.head(10).iterrows():
        print(f"  {row['REG_imp']} - Sector {row['PROD_COMM']}: ${row['Value']:,.2f}")
