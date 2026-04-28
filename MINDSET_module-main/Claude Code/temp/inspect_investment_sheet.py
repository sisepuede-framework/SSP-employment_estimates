import pandas as pd
import sys

try:
    scenario_file = "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main/GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"

    print("="*80)
    print("READING: Strategy_1004_MEX.xlsx")
    print("="*80)

    # Get all sheet names first
    xl = pd.ExcelFile(scenario_file)
    print(f"\nAvailable sheets: {xl.sheet_names}")

    # Try to read "Investment by" sheet
    sheet_name = None
    for name in xl.sheet_names:
        if 'invest' in name.lower():
            sheet_name = name
            break

    if sheet_name:
        print(f"\n{'='*80}")
        print(f"SHEET: '{sheet_name}'")
        print('='*80)

        df = pd.read_excel(scenario_file, sheet_name=sheet_name)

        print(f"\nShape: {df.shape}")
        print(f"\nColumns ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")

        print(f"\nFirst 20 rows:")
        print(df.head(20).to_string())

        # Find columns with actual data
        print(f"\n\nLooking for data columns...")
        for col in df.columns:
            non_null = df[col].notna().sum()
            if non_null > 0:
                print(f"\n'{col}': {non_null} non-null values")
                if non_null < 50:  # Show unique values if not too many
                    unique_vals = df[col].dropna().unique()
                    print(f"  Unique values: {unique_vals[:20]}")

    else:
        print("\n✗ No 'Investment by' sheet found")
        print("Trying 'Final demand' instead...")

        df = pd.read_excel(scenario_file, sheet_name='Final demand')
        print(f"\nShape: {df.shape}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst 20 rows:")
        print(df.head(20).to_string())

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
