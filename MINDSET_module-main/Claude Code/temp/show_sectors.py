import pandas as pd

file_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Claude.xlsx"

# Read the file
df = pd.read_excel(file_path, header=0)

print("="*80)
print("EORA26 SECTORS (from row 0 / header row)")
print("="*80)
print("\nSector names from B2:Z2 (columns 1-25):")
for i in range(1, 26):
    sector_name = df.iloc[0, i]
    print(f"  Column {chr(66+i-1)}{2} (pandas col {i}): {sector_name}")

print("\n" + "="*80)
print("GLORIA PRODUCTS (120 products)")
print("="*80)
print("\nFirst 30 products:")
for i in range(1, 31):
    product_name = df.iloc[i, 0]
    print(f"  Row {i+1}: {product_name}")

print(f"\n... (showing 30 of 120 products)")

print("\n" + "="*80)
print("CURRENT STATE OF MATRIX")
print("="*80)
print("\nSample values (row 1-5, columns 1-5):")
print(df.iloc[1:6, 1:6])

print("\n" + "="*80)
print("TASK UNDERSTANDING")
print("="*80)
print("""
The task is to create a concordance matrix where:
- Rows = 120 GLORIA products (rows 2-121 in Excel, or indices 1-120 in pandas)
- Columns = 25 Eora26 sectors (columns B-Z in Excel, or indices 1-25 in pandas)
- Values = 1 if GLORIA product maps to Eora sector, 0 otherwise

Currently the matrix has text values or NaN. We need to fill it with 1s and 0s
based on the logical mapping between GLORIA products and Eora26 sectors.
""")
