import pandas as pd

scenario_file = '../../GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx'

print("=" * 80)
print("CHECKING NON-ZERO INVESTMENT VALUES")
print("=" * 80)
print()

# Read Investment by sheet
df = pd.read_excel(scenario_file, sheet_name='Investment by')

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print()

# Check Value* column
if 'Value*' in df.columns:
    # Count non-zero values
    non_zero_count = (df['Value*'] != 0).sum()
    zero_count = (df['Value*'] == 0).sum()

    print(f"Non-zero values: {non_zero_count}")
    print(f"Zero values: {zero_count}")
    print()

    # Show non-zero entries
    if non_zero_count > 0:
        print("NON-ZERO ENTRIES:")
        print("-" * 80)
        non_zero_df = df[df['Value*'] != 0]
        for idx, row in non_zero_df.iterrows():
            print(f"Row {idx}: Country={row['Country ISO*']}, "
                  f"Sector={row['Sector investing code*']}, "
                  f"Value=${row['Value*']:,.2f}, "
                  f"Type={row['Type*']}")
    else:
        print("WARNING: No non-zero values found!")
        print("Showing first 10 rows:")
        print(df[['Country ISO*', 'Sector investing code*', 'Value*', 'Type*']].head(10))
else:
    print("ERROR: 'Value*' column not found!")
