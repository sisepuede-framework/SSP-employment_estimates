"""
Create a TRUE identity INV_CONV matrix for SSP aggregated data in CSV format

This replaces the complex investment conversion patterns with:
  Sector N → 100% Product N, 0% all others

This allows "Investment by" sheet to work when you put product codes
in "Sector investing code*" column.
"""
import pandas as pd
import numpy as np
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("Creating Identity INV_CONV Matrix (CSV format)")
print("="*80)
print()

# Create 120x120 identity matrix
inv_conv_identity = pd.DataFrame(np.eye(120),
                                  index=range(1, 121),
                                  columns=range(1, 121))

# Add first column with sector IDs (matching original format)
inv_conv_identity.insert(0, 'Unnamed: 0', range(1, 121))

# Convert column names to strings (matching original format)
inv_conv_identity.columns = ['Unnamed: 0'] + [str(i) for i in range(1, 121)]

print("Identity matrix created:")
print(f"  Shape: {inv_conv_identity.shape}")
print(f"  Diagonal values: all 1.0")
print(f"  Off-diagonal values: all 0.0")
print()

# Show first 5x5 block
print("First 5x5 block:")
print(inv_conv_identity.iloc[:5, :6])
print()

# Save to SSP folder as CSV
output_path = "GLORIA_db/v57/2019/SSP/INV_CONV.csv"
inv_conv_identity.to_csv(output_path, index=False)

print(f"✓ Saved to: {output_path}")
print()

# Verify what we saved
print("Verification - reading back:")
verify = pd.read_csv(output_path)
print(f"  Shape: {verify.shape}")
print(f"  Diagonal sample: {verify.iloc[0, 1]}, {verify.iloc[54, 55]}, {verify.iloc[119, 120]}")
print(f"  First 3x3 block:")
print(verify.iloc[:3, :4])
print()

print("="*80)
print("NEXT STEP")
print("="*80)
print()
print("Update Variable_list_MINDSET_SSP.xlsx to point to this new file:")
print()
print("Variable name: INV_CONV")
print(f"Path: {output_path}")
print("Type: DataFrame")
print()
print("After updating Variable_list, run TEST_FIXED_INV_CONV.py to verify.")
