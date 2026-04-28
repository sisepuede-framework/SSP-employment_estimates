"""
Examine the New template.xlsx file that user based their Strategy files on.
This will show us if MINDSET's template uses products or sectors in the 'Sector investing code*' column.
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("EXAMINING: New template.xlsx")
print("="*80)
print()

template_file = "GLORIA_template/Scenarios/New template.xlsx"

if not os.path.exists(template_file):
    print(f"ERROR: File not found: {template_file}")
    exit(1)

xl = pd.ExcelFile(template_file)
print(f"Sheets in file: {xl.sheet_names}")
print()

if 'Investment by' in xl.sheet_names:
    print("="*80)
    print("INVESTMENT BY SHEET")
    print("="*80)
    print()

    inv = pd.read_excel(template_file, 'Investment by')
    print(f"Shape: {inv.shape}")
    print(f"Columns: {list(inv.columns)}")
    print()

    # Show all rows
    print("All rows in template:")
    print("-"*80)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(inv)
    print()

    # Analyze the codes
    if 'Sector investing code*' in inv.columns:
        codes = inv['Sector investing code*'].dropna()
        print("="*80)
        print("ANALYSIS OF 'Sector investing code*' COLUMN")
        print("="*80)
        print()
        print(f"Unique codes: {sorted(codes.unique())}")
        print()

        # Check if codes are numeric (products 1-120) or text (sector names)
        try:
            numeric_codes = pd.to_numeric(codes, errors='coerce')
            if numeric_codes.notna().all():
                print("✓ Codes are NUMERIC")
                print(f"  Range: {numeric_codes.min():.0f} to {numeric_codes.max():.0f}")
                print()
                if numeric_codes.min() >= 1 and numeric_codes.max() <= 120:
                    print("→ These appear to be PRODUCT codes (1-120 range)")
                else:
                    print("→ Numeric but outside product range")
        except:
            print("✗ Codes are NON-NUMERIC (likely sector names or 'ALL')")
else:
    print("'Investment by' sheet not found")

print()
print("="*80)
print("CONCLUSION")
print("="*80)
print()
print("Does the template show products or sectors in 'Sector investing code*'?")
