"""
Check how INV_BASE is supposed to be structured and used
"""
import pickle
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("1. Check Variable_list for INV variables")
print("="*80)
var_list = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx', 'variables')
inv_vars = var_list[var_list['Variable name (new)'].str.contains('INV', na=False, case=False)]
print(inv_vars[['Variable name (new)', 'Location', 'Type']])

print("\n" + "="*80)
print("2. Load SSP INV_BASE and check structure")
print("="*80)
inv_base = pickle.load(open('GLORIA_db/v57/2019/SSP/inv.pkl', 'rb'))
print(f"Type: {type(inv_base)}")
print(f"Index: {inv_base.index.names}")
print(f"Columns: {list(inv_base.columns)}")
print(f"Shape: {inv_base.shape}")

print("\n" + "="*80)
print("3. Test if groupby works")
print("="*80)
try:
    # This is what InputOutput.py line 252 tries to do
    result = inv_base.groupby(['REG_exp','TRAD_COMM']).agg({'INV':'sum'}).reset_index()
    print(f"✓ Groupby works!")
    print(f"Result shape: {result.shape}")
    print(f"Result columns: {list(result.columns)}")
except Exception as e:
    print(f"✗ Groupby failed: {e}")
    print("\nTrying with reset_index first...")
    try:
        inv_flat = inv_base.reset_index()
        print(f"After reset_index, columns: {list(inv_flat.columns)}")
        result = inv_flat.groupby(['REG_exp','TRAD_COMM']).agg({'INV':'sum'}).reset_index()
        print(f"✓ Groupby works after reset_index!")
        print(f"Result shape: {result.shape}")
        print(f"Result columns: {list(result.columns)}")
    except Exception as e2:
        print(f"✗ Still failed: {e2}")

print("\n" + "="*80)
print("4. Compare with parsed_db_original structure (if possible)")
print("="*80)
try:
    # Try loading with different pandas version compatibility
    import warnings
    warnings.filterwarnings('ignore')
    inv_orig = pd.read_pickle('GLORIA_db/v57/2019/parsed_db_original/inv.pkl')
    print(f"Original - Type: {type(inv_orig)}")
    print(f"Original - Index: {inv_orig.index.names}")
    print(f"Original - Columns: {list(inv_orig.columns)}")
    print(f"Original - Shape: {inv_orig.shape}")
except Exception as e:
    print(f"Could not load original: {e}")
