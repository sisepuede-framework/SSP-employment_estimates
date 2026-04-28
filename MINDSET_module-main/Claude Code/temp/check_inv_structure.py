"""
Check INV_BASE structure in both original and SSP aggregated data
"""
import pickle
import sys
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("ORIGINAL INV_BASE (parsed_db_original)")
print("="*80)
try:
    inv_orig = pickle.load(open('GLORIA_db/v57/2019/parsed_db_original/inv.pkl','rb'))
    print(f"Columns: {list(inv_orig.columns)}")
    print(f"Shape: {inv_orig.shape}")
    print(f"\nFirst 3 rows:")
    print(inv_orig.head(3))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("SSP AGGREGATED INV_BASE (SSP folder)")
print("="*80)
try:
    inv_ssp = pickle.load(open('GLORIA_db/v57/2019/SSP/inv.pkl','rb'))
    print(f"Columns: {list(inv_ssp.columns)}")
    print(f"Shape: {inv_ssp.shape}")
    print(f"\nFirst 3 rows:")
    print(inv_ssp.head(3))
except Exception as e:
    print(f"Error: {e}")
