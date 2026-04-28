import pandas as pd

scenario_file = '../../GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx'

print("=" * 80)
print("CHECKING SCENARIO FILE STRUCTURE")
print("=" * 80)
print()

# Read with skiprows=14 as scenario.py does
print("Reading 'Investment by' sheet with skiprows=14...")
df = pd.read_excel(scenario_file, sheet_name='Investment by', skiprows=14)

print(f"\nColumns found: {list(df.columns)}")
print(f"\nNumber of columns: {len(df.columns)}")
print(f"Number of rows: {len(df)}")
print("\nFirst 5 rows:")
print(df.head())
print()

# Check if the expected columns exist
expected = ['Country ISO*', 'Sector investing code*', 'Value*', 'Type*']
print(f"Expected columns: {expected}")
print()
for col in expected:
    if col in df.columns:
        print(f"  ✓ Found: '{col}'")
    else:
        print(f"  ✗ Missing: '{col}'")
        # Check for similar names
        similar = [c for c in df.columns if col.replace('*', '').strip().lower() in str(c).lower()]
        if similar:
            print(f"    Similar columns found: {similar}")
