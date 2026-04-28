"""
Test if pandas groupby works on MultiIndex DataFrames
"""
import pickle
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Testing groupby on MultiIndex DataFrames")
print("="*80)

# Load INV_BASE
inv_base = pickle.load(open('GLORIA_db/v57/2019/SSP/inv.pkl', 'rb'))

print("\nINV_BASE structure:")
print(f"  Index names: {inv_base.index.names}")
print(f"  Columns: {list(inv_base.columns)}")
print(f"  Shape: {inv_base.shape}")
print(f"\nFirst 3 rows:")
print(inv_base.head(3))

print("\n" + "-"*80)
print("Test 1: Direct groupby (what InputOutput.py does)")
print("-"*80)
try:
    result = inv_base.groupby(['REG_exp','TRAD_COMM']).agg({'INV':'sum'}).reset_index()
    print("✓ SUCCESS!")
    print(f"  Result shape: {result.shape}")
    print(f"  Result columns: {list(result.columns)}")
    print(f"\nFirst 3 rows:")
    print(result.head(3))
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print("\n" + "-"*80)
print("Test 2: Load HH_BASE and try same operation")
print("-"*80)
hh_base = pickle.load(open('GLORIA_db/v57/2019/SSP/HH.pkl', 'rb'))
print(f"HH_BASE index names: {hh_base.index.names}")
print(f"HH_BASE columns: {list(hh_base.columns)}")

try:
    result = hh_base.groupby(['REG_exp','TRAD_COMM']).agg({'VIPA':'sum'}).reset_index()
    print("✓ SUCCESS!")
    print(f"  Result shape: {result.shape}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
