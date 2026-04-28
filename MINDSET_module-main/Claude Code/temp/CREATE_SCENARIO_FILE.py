"""
CREATE SCENARIO FILE - Manual Helper Script

This script creates a basic scenario file structure.
You can then open it in Excel and add your specific investments.

For R users: This is like creating an Excel template in R using writexl or openxlsx
"""

import pandas as pd
import os

# Output location
output_file = "GLORIA_template/Scenarios/Infrastructure_Investment.xlsx"

print("="*60)
print("SCENARIO FILE CREATOR")
print("="*60)

# Create the scenario directory if it doesn't exist
os.makedirs("GLORIA_template/Scenarios", exist_ok=True)

# ============================================================================
# Sheet 1: Investment by (REQUIRED)
# ============================================================================

# Create empty rows for header (rows 1-14)
header_info = pd.DataFrame({
    'Info': [
        'MINDSET Scenario File',
        '',
        'Instructions:',
        '1. Fill in data starting at row 16',
        '2. Country ISO: 3-letter country code (USA, CHN, BRA, etc.)',
        '3. Sector investing code: Number 1-120 (see Product reference)',
        '4. Value: Investment amount in USD',
        '5. Type: Usually "abs-b" (absolute proportional to base)',
        '',
        'You can specify ranges: 1-10 or ALL',
        'You can specify multiple countries: USA,CHN,BRA',
        '',
        'Example below shows $100M in Construction (sector 56) in USA',
        ''
    ]
})

# Column headers (row 15)
column_headers = pd.DataFrame({
    'Country ISO*': ['USA'],
    'Sector investing code*': [56],
    'Value*': [100000000],
    'Type*': ['abs-b']
})

# Save to Excel with multiple sheets
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Write header info (rows 1-14)
    header_info.to_excel(writer, sheet_name='Investment by',
                         index=False, header=False, startrow=0)

    # Write data (starting row 15 - but Excel is 1-indexed, pandas is 0-indexed)
    # So startrow=14 puts it at Excel row 15
    column_headers.to_excel(writer, sheet_name='Investment by',
                           index=False, startrow=14)

print(f"\n✓ Created: {output_file}")
print(f"\nNEXT STEPS:")
print(f"1. Open the file in Excel")
print(f"2. Go to 'Investment by' sheet")
print(f"3. Edit/add rows starting at row 16")
print(f"4. Specify your countries, sectors, and investment amounts")
print(f"5. Save the file")
print(f"6. Run: RunMINDSET_EmploymentOnly.py")

print("\n" + "="*60)
print("EXAMPLE DATA TO ADD:")
print("="*60)
print("\nFor testing all 120 products:")
print("  Country | Sector | Value    | Type")
print("  USA     | 1      | 1000000  | abs-b")
print("  USA     | 2      | 1000000  | abs-b")
print("  ...")
print("  USA     | 120    | 1000000  | abs-b")

print("\nFor single sector test:")
print("  Country | Sector | Value      | Type")
print("  USA     | 56     | 100000000  | abs-b")

print("\nFor cross-country comparison:")
print("  Country | Sector | Value      | Type")
print("  USA     | 56     | 100000000  | abs-b")
print("  CHN     | 56     | 100000000  | abs-b")
print("  BRA     | 56     | 100000000  | abs-b")

print("\n" + "="*60)
print("REFERENCE FILES:")
print("="*60)
print("Product codes (1-120):")
print("  Claude Code/temp/GLORIA_Products_Reference.xlsx")
print("\nCountry codes:")
print("  Claude Code/temp/GLORIA_Regions_Reference.xlsx")

print("\n" + "="*60)
