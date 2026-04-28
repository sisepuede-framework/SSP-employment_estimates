import pandas as pd
import os

scenarios_dir = "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main/GLORIA_template/Scenarios"

# Read a few example scenario files
examples = [
    'Strategy_1004_MEX.xlsx',
    'Strategy_3010_BGR.xlsx',
    'Strategy_2002_EGY.xlsx'
]

for filename in examples:
    filepath = os.path.join(scenarios_dir, filename)
    if os.path.exists(filepath):
        print(f'\n{"="*80}')
        print(f'FILE: {filename}')
        print("="*80)

        try:
            # Read with header on first row (no skip)
            df = pd.read_excel(filepath, sheet_name='Final demand', header=0)

            print(f'Shape: {df.shape}')
            print(f'\nColumn names:')
            for i, col in enumerate(df.columns):
                print(f'  {i}: {col}')

            print(f'\nFirst 5 rows:')
            print(df.head(5))

            print(f'\nData types:')
            print(df.dtypes)

            # Check for Product code column
            product_col = None
            for col in df.columns:
                if 'Product' in col and 'code' in col:
                    product_col = col
                    break

            if product_col:
                print(f'\nUnique Product codes in column "{product_col}":')
                unique_products = sorted(df[product_col].dropna().unique())
                print(f'  Count: {len(unique_products)}')
                print(f'  Values: {unique_products}')

            # Check for value column
            value_col = None
            for col in df.columns:
                if 'Value' in col or 'value' in col:
                    value_col = col
                    break

            if value_col:
                print(f'\nTotal investment from column "{value_col}": {df[value_col].sum():,.0f}')

        except Exception as e:
            print(f'Error reading file: {e}')
    else:
        print(f'File not found: {filepath}')
