import pandas as pd

file_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP - Employment Module\Data\GLORIA - Eora26 concordance - Claude.xlsx"

# Read with row 0 as header
df = pd.read_excel(file_path, header=0)

print("="*80)
print("UNDERSTANDING THE STRUCTURE")
print("="*80)
print(f"\nShape: {df.shape}")
print(f"\nColumn names (these should be the Eora26 sectors):")
for i, col in enumerate(df.columns):
    print(f"  Column {i}: '{col}'")

print("\n" + "="*80)
print("GLORIA PRODUCTS (Column A / first column)")
print("="*80)
print(df.iloc[:, 0].head(20))

print("\n" + "="*80)
print("SAMPLE OF CURRENT DATA (first 10 rows, first 10 columns)")
print("="*80)
print(df.iloc[:10, :10])

print("\n" + "="*80)
print("DATA TYPES")
print("="*80)
print(df.dtypes.head(10))

print("\n" + "="*80)
print("CHECK: Are there any 1s or 0s already filled?")
print("="*80)
print("Unique values in column 2:", df.iloc[:, 1].unique()[:10])
print("Unique values in column 3:", df.iloc[:, 2].unique()[:10])
