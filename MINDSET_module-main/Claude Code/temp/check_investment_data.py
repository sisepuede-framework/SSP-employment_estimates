import pandas as pd

scenario_file = '../../GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx'

print("=" * 80)
print("CHECKING INVESTMENT DATA IN SCENARIO FILE")
print("=" * 80)
print()

# Read Investment by sheet WITHOUT skiprows
print("Reading 'Investment by' sheet (no skiprows)...")
try:
    df = pd.read_excel(scenario_file, sheet_name='Investment by')

    print(f"\nColumns: {list(df.columns)}")
    print(f"Shape: {df.shape}")
    print("\nAll data:")
    print(df)
    print()

    # Check if required columns exist
    if 'Country ISO*' in df.columns:
        print(f"✓ 'Country ISO*' column found")
        print(f"  Values: {df['Country ISO*'].tolist()}")
    else:
        print(f"✗ 'Country ISO*' column NOT found")

    if 'Sector investing code*' in df.columns:
        print(f"✓ 'Sector investing code*' column found")
        print(f"  Values: {df['Sector investing code*'].tolist()}")
    else:
        print(f"✗ 'Sector investing code*' column NOT found")

    if 'Value*' in df.columns:
        print(f"✓ 'Value*' column found")
        print(f"  Values: {df['Value*'].tolist()}")
    else:
        print(f"✗ 'Value*' column NOT found")

except Exception as e:
    print(f"Error reading file: {e}")
    import traceback
    traceback.print_exc()
