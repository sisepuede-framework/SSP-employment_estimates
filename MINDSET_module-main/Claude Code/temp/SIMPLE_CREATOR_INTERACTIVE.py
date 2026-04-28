"""
SIMPLE SCENARIO CREATOR - INTERACTIVE VERSION

This version works when running line-by-line in Positron!
For R users: You can run this like you run R code (line by line)

How to use:
1. Run each cell/section one at a time (Ctrl+Enter)
2. Or run all at once (Ctrl+Shift+Enter)
"""

import pandas as pd
import os
import sys

print("="*60)
print("SIMPLE SCENARIO CREATOR - INTERACTIVE VERSION")
print("="*60)

# =============================================================================
# Step 1: Setup paths (works in interactive mode!)
# =============================================================================

print("\n1. Setting up working directory...")

# Try to get script directory, but handle interactive mode
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Running interactively (like in IPython/Positron cell-by-cell)
    # Use current working directory and navigate to MINDSET root
    script_dir = os.getcwd()
    print("   (Running in interactive mode)")

# Navigate to MINDSET root
# If we're in Claude Code/temp, go up 2 levels
if script_dir.endswith("temp") or script_dir.endswith("Claude Code"):
    mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
elif script_dir.endswith("Claude Code"):
    mindset_root = os.path.abspath(os.path.join(script_dir, ".."))
else:
    # Assume we're already in MINDSET root
    mindset_root = script_dir

os.chdir(mindset_root)
print(f"   ✓ Working directory: {os.getcwd()}")

# Check if we're in the right place
if not os.path.exists("GLORIA_template"):
    print("\n   ⚠️  WARNING: Can't find GLORIA_template folder!")
    print("   You might not be in the MINDSET_module-main directory")
    print(f"   Current directory: {os.getcwd()}")
    print("\n   Try this: Change to MINDSET_module-main folder first")
    sys.exit(1)

# =============================================================================
# Step 2: Load GLORIA product list
# =============================================================================

print("\n2. Loading GLORIA product list...")
try:
    products = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx',
                            sheet_name='P')
    print("Available columns:", products.columns.tolist())                    
    print(f"   ✓ Found {len(products)} products")
except Exception as e:
    print(f"   ✗ Error: {e}")
    print("   Make sure you're in the MINDSET_module-main directory")
    sys.exit(1)

# =============================================================================
# Step 3: Load GLORIA region list
# =============================================================================

print("\n3. Loading GLORIA region list...")
try:
    regions = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx',
                           sheet_name='R')
    print(f"   ✓ Found {len(regions)} regions")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# =============================================================================
# Step 4: Create output directory if needed
# =============================================================================

print("\n4. Preparing output directory...")
output_dir = "Claude Code/temp"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"   ✓ Created: {output_dir}")
else:
    print(f"   ✓ Directory exists: {output_dir}")

# =============================================================================
# Step 5: Save reference lists
# =============================================================================

print("\n5. Creating reference lists...")

# Products list (simplified for reference)
products_simple = products[['Lfd_Nr', 'Sector_names']].copy()
products_file = f"{output_dir}/GLORIA_Products_Reference.xlsx"
products_simple.to_excel(products_file, index=False)
print(f"   ✓ Created: {products_file}")

# Regions list
print("Region columns:", regions.columns.tolist())
regions_simple = regions[['Region_acronyms', 'Region_names']].copy()
regions_file = f"{output_dir}/GLORIA_Regions_Reference.xlsx"
regions_simple.to_excel(regions_file, index=False)
print(f"   ✓ Created: {regions_file}")

# =============================================================================
# Step 6: Create simple scenario template
# =============================================================================

print("\n6. Creating scenario template...")

# Simple template with examples (like a data.frame in R)
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

# =============================================================================
# Step 7: Create test scenario with all 120 products
# =============================================================================

print("\n7. Creating test scenario (all 120 products)...")

# In R: data.frame(product=1:120, value=rep(1e6, 120))
all_products = pd.DataFrame({
    'Producing country ISO*': ['USA'] * 120,
    'Consuming country ISO*': ['USA'] * 120,
    'Product code*': [str(i) for i in range(1, 121)],
    'FD code*': ['FD_4'] * 120,
    'Value*': [1000000] * 120,  # $1M each
    'Type*': ['abs-b'] * 120
})

# Create Scenarios directory if it doesn't exist
scenarios_dir = "GLORIA_template/Scenarios"
if not os.path.exists(scenarios_dir):
    os.makedirs(scenarios_dir)
    print(f"   ✓ Created directory: {scenarios_dir}")

test_file = f"{scenarios_dir}/Test_AllProducts_1M_USA.xlsx"
all_products.to_excel(test_file, index=False, sheet_name='Final demand')
print(f"   ✓ Created: {test_file}")
print(f"      This tests $1M in each of 120 products")

# =============================================================================
# Step 8: Create simple construction example
# =============================================================================

print("\n8. Creating construction example...")

# Simple single-row scenario
construction = pd.DataFrame({
    'Producing country ISO*': ['USA'],
    'Consuming country ISO*': ['USA'],
    'Product code*': ['56'],
    'FD code*': ['FD_4'],
    'Value*': [100000000],
    'Type*': ['abs-b']
})

construction_file = f"{scenarios_dir}/Test_Construction_100M_USA.xlsx"
construction.to_excel(construction_file, index=False, sheet_name='Final demand')
print(f"   ✓ Created: {construction_file}")
print(f"      $100M construction investment")

# =============================================================================
# Summary
# =============================================================================

print("\n" + "="*60)
print("SUCCESS! Files created:")
print("="*60)

print(f"\nReference files (in {output_dir}):")
print(f"  1. GLORIA_Products_Reference.xlsx")
print(f"     - All 120 GLORIA products with names")
print(f"  2. GLORIA_Regions_Reference.xlsx")
print(f"     - All 162 regions/countries")
print(f"  3. SCENARIO_TEMPLATE_SIMPLE.xlsx")
print(f"     - Template with 3 example rows")

print(f"\nReady-to-run scenarios (in {scenarios_dir}):")
print(f"  4. Test_AllProducts_1M_USA.xlsx")
print(f"     - Tests $1M in EACH of 120 products")
print(f"     - Perfect for your dissertation!")
print(f"  5. Test_Construction_100M_USA.xlsx")
print(f"     - Simple $100M construction test")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)

print("\n1. To run the construction test:")
print("   • Open: RunMINDSET_EmploymentOnly.py")
print("   • Line 103: scenario_name = 'Test_Construction_100M_USA'")
print("   • Press: Ctrl+Shift+Enter")

print("\n2. To analyze all 120 products:")
print("   • Line 103: scenario_name = 'Test_AllProducts_1M_USA'")
print("   • Press: Ctrl+Shift+Enter")
print("   • Results will show employment for ALL products!")

print("\n3. Open reference files to see:")
print("   • Product codes and names (1-120)")
print("   • Country codes (USA, CHN, etc.)")

print("\n" + "="*60)
print("All done! Ready to run employment analysis! 🎉")
print("="*60)
