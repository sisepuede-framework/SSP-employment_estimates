import pandas as pd
import numpy as np

# Load crosswalk
crosswalk_file = "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/GLORIA-Eora26 - Crosswalk.xlsx"
df = pd.read_excel(crosswalk_file, sheet_name="Eora26 - GLORIA")

print("=== CROSSWALK ANALYSIS ===\n")
print(f"Total rows (products): {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"\nColumn names: {df.columns.tolist()}\n")

# Get product column (first) and sector columns (rest)
product_col = df.columns[0]
sector_cols = df.columns[1:]

print(f"Product column: {product_col}")
print(f"Number of sector columns: {len(sector_cols)}\n")

# Count how many sectors each product is linked to
df['n_sectors'] = df[sector_cols].sum(axis=1)

print("Distribution of products by number of linked sectors:")
print(df['n_sectors'].value_counts().sort_index())
print()

# Show multi-sector products
multi_sector = df[df['n_sectors'] > 1]
print(f"\nProducts linked to multiple sectors ({len(multi_sector)} products):\n")

for idx, row in multi_sector.iterrows():
    product_name = row[product_col]
    n_sects = int(row['n_sectors'])
    linked_sectors = [col for col in sector_cols if row[col] == 1]

    print(f"  {product_name}")
    print(f"    → Linked to {n_sects} sectors: {', '.join(linked_sectors)}\n")

# Check for duplicates
print("\n=== DUPLICATE CHECK ===")
print(f"Unique product names: {df[product_col].nunique()}")
print(f"Total rows: {len(df)}")

if df[product_col].nunique() != len(df):
    print("\n⚠ WARNING: Duplicate product names!")
    dupes = df[df[product_col].duplicated()][product_col].tolist()
    print(f"Duplicates: {dupes}")
else:
    print("✓ No duplicate product names")

print("\n\nFirst 5 products:")
print(df[[product_col, 'n_sectors']].head())
