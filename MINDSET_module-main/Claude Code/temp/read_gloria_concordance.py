import pandas as pd
import sys

file_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Claude.xlsx"

print("Reading file...")
print(f"Path: {file_path}")

try:
    df = pd.read_excel(file_path)

    print("\n" + "="*80)
    print("FILE STRUCTURE")
    print("="*80)
    print(f"Shape: {df.shape} (rows x columns)")

    print("\n" + "="*80)
    print("COLUMN NAMES")
    print("="*80)
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    print("\n" + "="*80)
    print("FIRST 10 ROWS")
    print("="*80)
    print(df.head(10))

    print("\n" + "="*80)
    print("ROW 2 (should show sector names in wide format)")
    print("="*80)
    print(df.iloc[1, :])

except Exception as e:
    print(f"Error reading file: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
