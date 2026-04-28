import pandas as pd
import os

file_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data\GLORIA-Eora26 - Crosswalk.xlsx"

print(f"Checking file: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    # Get sheet names first
    xl_file = pd.ExcelFile(file_path)
    print(f"\nSheet names: {xl_file.sheet_names}")

    # Read the specific tab
    df = pd.read_excel(file_path, sheet_name='Eora26 - GLORIA')

    print("\n" + "="*80)
    print("FILE STRUCTURE")
    print("="*80)
    print(f"Shape: {df.shape} (rows × columns)")

    print("\n" + "="*80)
    print("COLUMN NAMES")
    print("="*80)
    for i, col in enumerate(df.columns):
        print(f"  Column {i}: '{col}'")

    print("\n" + "="*80)
    print("FIRST 20 ROWS")
    print("="*80)
    print(df.head(20))

    print("\n" + "="*80)
    print("LAST 5 ROWS")
    print("="*80)
    print(df.tail(5))

    print("\n" + "="*80)
    print("DATA TYPES")
    print("="*80)
    print(df.dtypes)

    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(df.describe())

    print("\n" + "="*80)
    print("CHECK: Are there 1s and 0s?")
    print("="*80)
    numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32']).columns.tolist()
    print(f"Numeric columns: {len(numeric_cols)}")
    if len(numeric_cols) > 0:
        print(f"First few numeric columns: {numeric_cols[:5]}")
        for col in numeric_cols[:3]:
            print(f"\n{col}:")
            print(f"  Unique values: {df[col].unique()}")
            print(f"  Value counts:")
            print(df[col].value_counts())

else:
    print(f"\nFile not found!")
    directory = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data"
    if os.path.exists(directory):
        print(f"Files in {directory}:")
        for f in os.listdir(directory):
            if 'GLORIA' in f or 'Eora' in f or 'xlsx' in f:
                print(f"  - {f}")
