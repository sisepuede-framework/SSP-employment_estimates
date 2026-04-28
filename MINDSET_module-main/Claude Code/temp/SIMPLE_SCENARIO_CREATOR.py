"""
SIMPLE SCENARIO FILE CREATOR

For R users: This is like creating a data.frame and saving it to Excel.
Much simpler version - just creates the essential template.

How to run in Positron:
1. Open this file
2. Press Ctrl+Shift+Enter (or click Run)
3. Check the output messages
"""

import pandas as pd
import os
import sys

print("="*60)
print("SIMPLE SCENARIO CREATOR")
print("="*60)

# Step 1: Setup paths (like setwd() in R)
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
os.chdir(mindset_root)

print(f"\n1. Working directory: {os.getcwd()}")

# Step 2: Load GLORIA product list
print("\n2. Loading GLORIA product list...")
try:
    products = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx',
                            sheet_name='P')
    print(f"   ✓ Found {len(products)} products")
except Exception as e:
    print(f"   ✗ Error: {e}")
    print("   Make sure you're in the MINDSET_module-main directory")
    sys.exit(1)

# Step 3: Load GLORIA region list
print("\n3. Loading GLORIA region list...")
try:
    regions = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx',
                           sheet_name='R')
    print(f"   ✓ Found {len(regions)} regions")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Step 4: Save reference lists
print("\n4. Creating reference lists...")
output_dir = "Claude Code/temp"

# Products list
products_simple = products[['Lfd_Nr', 'Product_name', 'Product_code']].copy()
products_simple.to_excel(f"{output_dir}/GLORIA_Products_Reference.xlsx", index=False)
print(f"   ✓ Created: {output_dir}/GLORIA_Products_Reference.xlsx")

# Regions list
regions_simple = regions[['Region_acronyms', 'Region_names']].copy()
regions_simple.to_excel(f"{output_dir}/GLORIA_Regions_Reference.xlsx", index=False)
print(f"   ✓ Created: {output_dir}/GLORIA_Regions_Reference.xlsx")

# Step 5: Create simple scenario template
print("\n5. Creating scenario template...")

# This is like creating a data.frame in R
template_data = pd.DataFrame({
    'Producing country ISO*': ['USA', 'USA', 'CHN'],
    'Consuming country ISO*': ['USA', 'USA', 'CHN'],
    'Product code*': ['56', '1-10', '1'],
    'FD code*': ['FD_4', 'FD_4', 'FD_4'],
    'Value*': [100000000, 10000000, 5000000],
    'Type*': ['abs-b', 'abs-b', 'abs-b'],
    'Notes': ['$100M to Construction in USA',
              '$10M to products 1-10 in USA',
              '$5M to product 1 in China']
})

# Save the template
template_file = f"{output_dir}/SCENARIO_TEMPLATE_SIMPLE.xlsx"
template_data.to_excel(template_file, index=False, sheet_name='Final demand')
print(f"   ✓ Created: {template_file}")

# Step 6: Create a test scenario with all products
print("\n6. Creating test scenario (all 120 products)...")

# This is like: expand.grid(product=1:120) in R
all_products = pd.DataFrame({
    'Producing country ISO*': ['USA'] * 120,
    'Consuming country ISO*': ['USA'] * 120,
    'Product code*': [str(i) for i in range(1, 121)],
    'FD code*': ['FD_4'] * 120,
    'Value*': [1000000] * 120,  # $1M each
    'Type*': ['abs-b'] * 120
})

test_file = "GLORIA_template/Scenarios/Test_AllProducts_1M_USA.xlsx"
all_products.to_excel(test_file, index=False, sheet_name='Final demand')
print(f"   ✓ Created: {test_file}")
print(f"      This tests $1M in each of 120 products")

# Step 7: Create a simple construction example
print("\n7. Creating construction example...")

construction = pd.DataFrame({
    'Producing country ISO*': ['USA'],
    'Consuming country ISO*': ['USA'],
    'Product code*': ['56'],
    'FD code*': ['FD_4'],
    'Value*': [100000000],
    'Type*': ['abs-b']
})

construction_file = "GLORIA_template/Scenarios/Test_Construction_100M_USA.xlsx"
construction.to_excel(construction_file, index=False, sheet_name='Final demand')
print(f"   ✓ Created: {construction_file}")
print(f"      $100M construction investment")

print("\n" + "="*60)
print("SUCCESS! Files created:")
print("="*60)
print(f"\nReference files (in Claude Code/temp):")
print(f"  1. GLORIA_Products_Reference.xlsx - All 120 products")
print(f"  2. GLORIA_Regions_Reference.xlsx - All 162 regions")
print(f"  3. SCENARIO_TEMPLATE_SIMPLE.xlsx - Template with examples")

print(f"\nReady-to-run scenarios (in GLORIA_template/Scenarios):")
print(f"  4. Test_AllProducts_1M_USA.xlsx - Test all 120 products")
print(f"  5. Test_Construction_100M_USA.xlsx - Simple construction test")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("\n1. To run the construction example:")
print("   • Open RunMINDSET_EmploymentOnly.py")
print("   • Line 103: scenario_name = 'Test_Construction_100M_USA'")
print("   • Press Ctrl+Shift+Enter")

print("\n2. To run the all-products test:")
print("   • Line 103: scenario_name = 'Test_AllProducts_1M_USA'")
print("   • This will give you employment for ALL 120 products!")

print("\n3. To create your own scenario:")
print("   • Open SCENARIO_TEMPLATE_SIMPLE.xlsx")
print("   • Edit the data (like editing a data.frame in R)")
print("   • Save as: GLORIA_template/Scenarios/YourScenarioName.xlsx")
print("   • Make sure sheet name is 'Final demand'")

print("\n" + "="*60)
