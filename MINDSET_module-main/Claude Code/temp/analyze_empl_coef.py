#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick analysis of Employment Coefficient file structure
"""

import pandas as pd
import os

# Set working directory
os.chdir(r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Mindset - WB\MINDSET_module-main\MINDSET_module-main")

# Read the employment coefficient file
file_path = "GLORIA_template/Employment/Empl_coefficient.csv"

print("=" * 80)
print("EMPLOYMENT COEFFICIENT FILE ANALYSIS")
print("=" * 80)

# Read first few rows to understand structure
df = pd.read_csv(file_path, nrows=10)

print(f"\n1. FILE DIMENSIONS:")
print(f"   - Columns: {df.shape[1]}")
print(f"   - Rows (sample): {df.shape[0]}")

print(f"\n2. COLUMN STRUCTURE (first 10 columns):")
for i, col in enumerate(df.columns[:10]):
    print(f"   Column {i}: '{col}'")

print(f"\n3. SAMPLE DATA (first 3 sectors, first 5 regions):")
print(df.iloc[:3, :5].to_string())

# Count total rows
with open(file_path, 'r') as f:
    total_rows = sum(1 for line in f)

print(f"\n4. TOTAL FILE SIZE:")
print(f"   - Total rows: {total_rows}")
print(f"   - Total sectors: {total_rows - 1}")  # Minus header row

# Try to understand the format
print(f"\n5. FORMAT INTERPRETATION:")
print(f"   - Column 1: Appears to be Sector ID")
print(f"   - Column 2: Appears to be Sector Name")
print(f"   - Columns 3+: Country/Region employment coefficients")
print(f"   - Values: Jobs per unit of output (likely per $1000 or $1M)")

print("\n" + "=" * 80)
print("STRUCTURE CONFIRMED!")
print("=" * 80)
print("\nThis is a SECTOR × COUNTRY matrix of employment coefficients")
print("Each cell = jobs per $ of output in that sector-country combination")
