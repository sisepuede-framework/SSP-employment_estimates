"""
Check what collapse_MRIO_SSP.py created for HH_CONS_COU (Countries_USDAtoGLORIA.xlsx)
"""
import pandas as pd

# Check the updated file
hh_cons_cou_path = "GLORIA_template/modelinputdata/Countries_USDAtoGLORIA.xlsx"
hh_cons_cou = pd.read_excel(hh_cons_cou_path)

print("="*80)
print("Countries_USDAtoGLORIA.xlsx (created by collapse_MRIO_SSP.py)")
print("="*80)
print(f"Shape: {hh_cons_cou.shape}")
print(f"Columns: {list(hh_cons_cou.columns)}")
print(f"\nAll rows:")
print(hh_cons_cou)

print("\n" + "="*80)
print("ROW Employment_country mapping:")
print("="*80)
row_entry = hh_cons_cou[hh_cons_cou['Country_Code'] == 'ROW']
if len(row_entry) > 0:
    print(row_entry)
    empl_country = row_entry['Employment_country'].values[0]
    print(f"\nROW → Employment_country = '{empl_country}'")

    # Check if this country exists in Empl_coefficient.csv
    print(f"\nChecking if '{empl_country}' exists in Empl_coefficient.csv...")
    empl_coef = pd.read_csv("GLORIA_template/Employment/Empl_coefficient.csv")
    if empl_country in empl_coef.columns:
        print(f"✓ '{empl_country}' column EXISTS in Empl_coefficient.csv")
    else:
        print(f"✗ '{empl_country}' column DOES NOT exist in Empl_coefficient.csv")
        print(f"  Available columns (first 10): {list(empl_coef.columns[:10])}")
else:
    print("✗ ROW not found in Countries_USDAtoGLORIA.xlsx")
