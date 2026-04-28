"""
Check the ORIGINAL files MINDSET was designed to load
"""
import pandas as pd

print("="*80)
print("ORIGINAL HH_CONS_COU FILE")
print("="*80)

hh_cons_cou_path = "GLORIA_template/modelinputdata/Countries_USDAtoGLORIA.xlsx"
hh_cons_cou = pd.read_excel(hh_cons_cou_path)

print(f"Shape: {hh_cons_cou.shape}")
print(f"Columns: {list(hh_cons_cou.columns)}")
print(f"\nFirst 10 rows:")
print(hh_cons_cou.head(10))

# Check for ROW
print(f"\nRows containing 'ROW':")
row_entries = hh_cons_cou[hh_cons_cou.apply(lambda row: row.astype(str).str.contains('ROW', case=False).any(), axis=1)]
print(row_entries)

print("\n" + "="*80)
print("ORIGINAL EMPL_COEF FILE")
print("="*80)

empl_coef_path = "GLORIA_template/Employment/Empl_coefficient.csv"
empl_coef = pd.read_csv(empl_coef_path)

print(f"Shape: {empl_coef.shape}")
print(f"Columns (first 10): {list(empl_coef.columns[:10])}")
print(f"Total columns: {len(empl_coef.columns)}")
print(f"\nFirst 5 rows, first 10 columns:")
print(empl_coef.iloc[:5, :10])

# Check if ROW is in columns
if 'ROW' in empl_coef.columns:
    print("\n✓ ROW column exists in EMPL_COEF")
else:
    print("\n✗ ROW column does NOT exist in EMPL_COEF")
    # Check for "Rest of" columns
    rest_cols = [col for col in empl_coef.columns if 'Rest of' in col or 'rest of' in col.lower()]
    if rest_cols:
        print(f"   Found 'Rest of' columns: {rest_cols}")
