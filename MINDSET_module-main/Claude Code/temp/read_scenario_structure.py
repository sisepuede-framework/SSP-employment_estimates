import pandas as pd
import sys

try:
    # Read one example scenario file
    scenario_file = "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main/GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"

    print("="*80)
    print("READING: Strategy_1004_MEX.xlsx")
    print("="*80)

    # Read the Final demand sheet
    df = pd.read_excel(scenario_file, sheet_name='Final demand')

    print(f"\nTotal rows in file: {len(df)}")
    print(f"\nColumns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")

    # Find data rows (look for non-null Product code)
    product_col = None
    value_col = None
    producing_col = None
    consuming_col = None

    for col in df.columns:
        if 'Product' in str(col) and 'code' in str(col):
            product_col = col
        if 'Value' in str(col) and '*' in str(col):
            value_col = col
        if 'Producing' in str(col) and 'ISO' in str(col):
            producing_col = col
        if 'Consuming' in str(col) and 'ISO' in str(col):
            consuming_col = col

    print(f"\nIdentified columns:")
    print(f"  Product code: {product_col}")
    print(f"  Value: {value_col}")
    print(f"  Producing country: {producing_col}")
    print(f"  Consuming country: {consuming_col}")

    if product_col and value_col:
        # Filter to rows with actual data
        data_rows = df[df[product_col].notna()].copy()

        print(f"\nData rows (with Product code): {len(data_rows)}")

        unique_products = sorted(data_rows[product_col].dropna().unique())
        print(f"\nUnique products: {len(unique_products)}")
        print(f"Product range: {min(unique_products) if unique_products else 'N/A'} to {max(unique_products) if unique_products else 'N/A'}")

        total_investment = data_rows[value_col].sum()
        print(f"\nTotal investment: ${total_investment:,.2f}")

        print(f"\nFirst 10 data rows:")
        cols_to_show = [c for c in [producing_col, consuming_col, product_col, value_col] if c]
        print(data_rows[cols_to_show].head(10).to_string(index=False))

        print(f"\nLast 5 data rows:")
        print(data_rows[cols_to_show].tail(5).to_string(index=False))

        # Check if all 120 products are present
        if len(unique_products) == 120:
            print(f"\n✓ All 120 GLORIA products are present in this scenario file")
        else:
            print(f"\n⚠ Only {len(unique_products)} products found (expected 120)")
    else:
        print("\n✗ Couldn't find Product code or Value columns")
        print("\nFirst 5 rows of dataframe:")
        print(df.head())

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
