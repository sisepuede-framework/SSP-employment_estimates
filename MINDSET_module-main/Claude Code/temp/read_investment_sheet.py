import pandas as pd
import sys

try:
    scenario_file = "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main/GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"

    print("="*80)
    print("READING: Strategy_1004_MEX.xlsx - 'Investment by' sheet")
    print("="*80)

    # Read Investment by sheet (skip first 14 rows as per MINDSET code)
    df = pd.read_excel(scenario_file, sheet_name='Investment by', skiprows=14)

    print(f"\nShape: {df.shape}")
    print(f"\nColumn names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. '{col}'")

    # Filter to data rows using the expected columns
    data_cols = ['Country ISO*', 'Sector investing code*', 'Value*', 'Type*']

    # Check if columns exist
    missing = [c for c in data_cols if c not in df.columns]
    if missing:
        print(f"\n⚠ Missing columns: {missing}")
        print("\nShowing all data:")
        print(df.head(20))
    else:
        data = df[data_cols].dropna(subset=['Sector investing code*'])

        print(f"\nData rows (with Sector investing code): {len(data)}")

        if len(data) > 0:
            print(f"\nFirst 15 rows:")
            print(data.head(15).to_string(index=False))

            print(f"\nLast 5 rows:")
            print(data.tail(5).to_string(index=False))

            print(f"\nUnique 'Sector investing code*' values:")
            unique_sectors = sorted(data['Sector investing code*'].dropna().unique())
            print(f"  Count: {len(unique_sectors)}")
            if unique_sectors:
                print(f"  Range: {int(min(unique_sectors))} to {int(max(unique_sectors))}")
                if len(unique_sectors) <= 30:
                    print(f"  Values: {[int(x) for x in unique_sectors]}")

            print(f"\nTotal investment: ${data['Value*'].sum():,.2f}")

            print(f"\nCountry values:")
            print(data['Country ISO*'].value_counts())
        else:
            print("\n⚠ No data rows found")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
