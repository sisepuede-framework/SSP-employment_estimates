"""
SCENARIO FILE CREATOR - FULLY ANNOTATED FOR UNDERSTANDING

Purpose: Create properly formatted Excel files for MINDSET employment analysis
For: Research team who needs to understand what's happening at each step

This script does 3 main things:
1. Loads GLORIA database product and region lists (the 120 products × 162 regions)
2. Creates reference Excel files so you know what products/regions exist
3. Creates example scenario files that specify demand shocks

Think of scenarios like this:
- You have an Input-Output model: dX = L × dY (Leontief equation)
- The scenario file specifies dY (your demand shock)
- The employment script calculates dX (output change) and dE (employment change)
"""

# =============================================================================
# PART 1: IMPORT REQUIRED PACKAGES
# =============================================================================

# In R equivalent: library(tidyverse); library(readxl)
import pandas as pd    # Like dplyr + readr in R - data manipulation
import os             # Like base::setwd(), file.path() - file operations
import sys            # System operations - exit script if errors

print("="*60)
print("SCENARIO FILE CREATOR - ANNOTATED VERSION")
print("="*60)
print("\nThis script creates the input files you need to run")
print("employment impact analysis with MINDSET.")

# =============================================================================
# PART 2: SET WORKING DIRECTORY
# =============================================================================

print("\n" + "-"*60)
print("STEP 1: Setting up working directory")
print("-"*60)

"""
Why we need this:
- Python needs to know where to find files (like setwd() in R)
- We need to be in the MINDSET_module-main root directory
- From there, we can access GLORIA_template/, SourceCode/, etc.

R equivalent:
    setwd("C:/path/to/MINDSET_module-main")
"""

# Try to get script location (works when running complete file)
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script is located in: {script_dir}")
except NameError:
    # Running interactively (cell-by-cell in Positron)
    script_dir = os.getcwd()
    print(f"Running interactively from: {script_dir}")

# Navigate to MINDSET root directory
# We might be in Claude Code/temp/, need to go up to MINDSET_module-main/
if "temp" in script_dir or "Claude Code" in script_dir:
    # Go up 2 levels: temp/ → Claude Code/ → MINDSET_module-main/
    mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    print(f"Navigating up to MINDSET root...")
else:
    # Already in root
    mindset_root = script_dir

# Change to MINDSET root (like setwd() in R)
os.chdir(mindset_root)
print(f"✓ Working directory set to: {os.getcwd()}")

# Verify we're in the right place by checking for GLORIA_template folder
if not os.path.exists("GLORIA_template"):
    print("\n❌ ERROR: Can't find GLORIA_template folder!")
    print(f"Current directory: {os.getcwd()}")
    print("\nYou need to be in the MINDSET_module-main directory.")
    print("The structure should be:")
    print("  MINDSET_module-main/")
    print("    ├── GLORIA_template/")
    print("    ├── SourceCode/")
    print("    └── Claude Code/")
    sys.exit(1)

print("✓ Verified: GLORIA_template folder found")

# =============================================================================
# PART 3: LOAD GLORIA PRODUCT LIST
# =============================================================================

print("\n" + "-"*60)
print("STEP 2: Loading GLORIA product list (120 products)")
print("-"*60)

"""
Why we need this:
- GLORIA has 120 economic products/sectors (agriculture, manufacturing, services, etc.)
- We need to know what they are so you can specify demand shocks correctly
- Each product has a code (1-120) and a descriptive name

R equivalent:
    products <- read_excel("GLORIA_template/Variables/Variable_list_MINDSET.xlsx",
                          sheet = "P")
"""

try:
    # Read Excel file, sheet "P" contains product information
    products = pd.read_excel(
        'GLORIA_template/Variables/Variable_list_MINDSET.xlsx',
        sheet_name='P'  # "P" = Products sheet
    )

    print(f"✓ Successfully loaded {len(products)} products")

    # Show first few products as examples
    print("\nExample products:")
    print("  Code | Name")
    print("  " + "-"*50)
    for i in range(5):
        code = products.iloc[i]['Lfd_Nr']
        name = products.iloc[i]['Product_name']
        print(f"  {code:3d}  | {name}")
    print("  ...")
    print(f"  56   | Construction")
    print("  ...")
    print(f"  120  | Activities of households as employers")

except Exception as e:
    print(f"❌ ERROR loading products: {e}")
    print("Make sure GLORIA_template/Variables/Variable_list_MINDSET.xlsx exists")
    sys.exit(1)

# =============================================================================
# PART 4: LOAD GLORIA REGION LIST
# =============================================================================

print("\n" + "-"*60)
print("STEP 3: Loading GLORIA region list (162 regions)")
print("-"*60)

"""
Why we need this:
- GLORIA has 162 regions (countries + Rest of World aggregates)
- Each region has an ISO code (USA, CHN, BRA, etc.)
- You need these codes to specify which country gets the demand shock

R equivalent:
    regions <- read_excel("GLORIA_template/Variables/Variable_list_MINDSET.xlsx",
                         sheet = "R")
"""

try:
    # Read Excel file, sheet "R" contains region information
    regions = pd.read_excel(
        'GLORIA_template/Variables/Variable_list_MINDSET.xlsx',
        sheet_name='R'  # "R" = Regions sheet
    )

    print(f"✓ Successfully loaded {len(regions)} regions")

    # Show example regions
    print("\nExample regions:")
    print("  Code | Name")
    print("  " + "-"*50)
    major_regions = ['USA', 'CHN', 'DEU', 'BRA', 'IND', 'GBR', 'JPN']
    for code in major_regions:
        if code in regions['Region_acronyms'].values:
            name = regions[regions['Region_acronyms']==code]['Region_names'].values[0]
            print(f"  {code:4s} | {name}")
    print("  ... (162 total regions)")

except Exception as e:
    print(f"❌ ERROR loading regions: {e}")
    sys.exit(1)

# =============================================================================
# PART 5: UNDERSTAND THE DATA STRUCTURE
# =============================================================================

print("\n" + "-"*60)
print("STEP 4: Understanding the GLORIA structure")
print("-"*60)

"""
Key concept for your research team:

GLORIA is a Multi-Regional Input-Output (MRIO) database with:
- 120 products/sectors (agriculture, manufacturing, services, etc.)
- 162 regions (countries)
- Total dimensions: 120 × 162 = 19,440 sector-regions

Example sector-regions:
- USA-Construction (USA producing construction services)
- CHN-Manufacturing (China producing manufactured goods)
- BRA-Agriculture (Brazil producing agricultural products)

Your employment analysis calculates:
1. Output change (dX) for each of these 19,440 sector-regions
2. Employment change (dE) for each sector-region
3. Total employment = sum across all sector-regions
"""

total_sector_regions = len(products) * len(regions)
print(f"✓ GLORIA dimensions:")
print(f"  - {len(products)} products")
print(f"  - {len(regions)} regions")
print(f"  - {total_sector_regions:,} total sector-regions")
print(f"\nEach sector-region combination represents a unique producing industry")
print(f"in a specific country (e.g., USA-Construction, CHN-Manufacturing)")

# =============================================================================
# PART 6: CREATE OUTPUT DIRECTORY
# =============================================================================

print("\n" + "-"*60)
print("STEP 5: Creating output directory")
print("-"*60)

"""
Where we'll save the reference files
R equivalent:
    if (!dir.exists("Claude Code/temp")) {
        dir.create("Claude Code/temp", recursive=TRUE)
    }
"""

output_dir = "Claude Code/temp"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"✓ Created directory: {output_dir}")
else:
    print(f"✓ Directory already exists: {output_dir}")

# =============================================================================
# PART 7: CREATE PRODUCT REFERENCE FILE
# =============================================================================

print("\n" + "-"*60)
print("STEP 6: Creating product reference file")
print("-"*60)

"""
Purpose:
Create a simple Excel file listing all 120 products
This is your lookup table when creating scenarios

Contains:
- Lfd_Nr: Product code (1-120)
- Product_name: Descriptive name
- Product_code: Alternative code

Your research team can open this file to see:
"What code do I use for construction sector?" → 56
"What code for agriculture?" → 1-15
"""

# Select only the columns we need for reference
products_simple = products[['Lfd_Nr', 'Product_name', 'Product_code']].copy()

# Save to Excel
products_file = os.path.join(output_dir, "GLORIA_Products_Reference.xlsx")
products_simple.to_excel(products_file, index=False)

print(f"✓ Created: {products_file}")
print(f"  Contains {len(products_simple)} products")
print(f"  Use this file to look up product codes")
print(f"  Example: Open in Excel to see 'Product 56 = Construction'")

# =============================================================================
# PART 8: CREATE REGION REFERENCE FILE
# =============================================================================

print("\n" + "-"*60)
print("STEP 7: Creating region reference file")
print("-"*60)

"""
Purpose:
Create a simple Excel file listing all 162 regions
This is your lookup table for country codes

Contains:
- Region_acronyms: ISO code (USA, CHN, BRA, etc.)
- Region_names: Full country name

Your research team can open this file to see:
"What code for United States?" → USA
"What code for China?" → CHN
"""

# Select only columns we need
regions_simple = regions[['Region_acronyms', 'Region_names']].copy()

# Save to Excel
regions_file = os.path.join(output_dir, "GLORIA_Regions_Reference.xlsx")
regions_simple.to_excel(regions_file, index=False)

print(f"✓ Created: {regions_file}")
print(f"  Contains {len(regions_simple)} regions")
print(f"  Use this file to look up country codes")
print(f"  Example: Open in Excel to see 'USA = United States'")

# =============================================================================
# PART 9: CREATE SIMPLE SCENARIO TEMPLATE
# =============================================================================

print("\n" + "-"*60)
print("STEP 8: Creating scenario template with examples")
print("-"*60)

"""
Purpose:
Create an example scenario file that shows the correct format

A scenario file specifies your demand shock (dY in the IO model)
It's like creating this data.frame in R:

    scenario_data <- data.frame(
        producing_country = c("USA", "USA", "CHN"),
        consuming_country = c("USA", "USA", "CHN"),
        product = c(56, "1-10", 1),
        category = c("FD_4", "FD_4", "FD_4"),
        amount = c(1e8, 1e7, 5e6),
        type = c("abs-b", "abs-b", "abs-b")
    )

This becomes the input to your employment model.
"""

# Create example scenario data
# This is like creating a data.frame in R
template_data = pd.DataFrame({
    # Which country produces the good
    'Producing country ISO*': ['USA', 'USA', 'CHN'],

    # Which country consumes/buys the good
    'Consuming country ISO*': ['USA', 'USA', 'CHN'],

    # Which product (1-120, or ranges like "1-10", or "ALL")
    'Product code*': ['56', '1-10', '1'],

    # Final demand category (FD_4 = investment, FD_1 = household)
    'FD code*': ['FD_4', 'FD_4', 'FD_4'],

    # Amount in USD
    'Value*': [100000000, 10000000, 5000000],

    # Type: abs-b = absolute amount, rel-b = relative to baseline
    'Type*': ['abs-b', 'abs-b', 'abs-b'],

    # Optional notes (for documentation)
    'Notes': [
        '$100M to Construction in USA',
        '$10M spread across products 1-10 in USA',
        '$5M to product 1 in China'
    ]
})

print("\nTemplate contains 3 example rows:")
print(template_data.to_string(index=False))

# Save to Excel
template_file = os.path.join(output_dir, "SCENARIO_TEMPLATE_SIMPLE.xlsx")
template_data.to_excel(template_file, index=False, sheet_name='Final demand')

print(f"\n✓ Created: {template_file}")
print(f"  Edit this file to create your own scenarios")
print(f"  Must have sheet named 'Final demand'")
print(f"  Column names must match exactly (with *)")

# =============================================================================
# PART 10: CREATE TEST SCENARIO - ALL PRODUCTS
# =============================================================================

print("\n" + "-"*60)
print("STEP 9: Creating test scenario (all 120 products)")
print("-"*60)

"""
Purpose:
Create a ready-to-run scenario that tests ALL 120 products at once

This is perfect for your dissertation:
- Invest $1M in each of the 120 products
- Run the employment model ONCE
- Get employment multipliers for all 120 products
- Compare which sectors create most jobs per dollar invested

In R equivalent:
    all_products <- data.frame(
        producing_country = rep("USA", 120),
        consuming_country = rep("USA", 120),
        product = 1:120,
        category = rep("FD_4", 120),
        amount = rep(1000000, 120),
        type = rep("abs-b", 120)
    )
"""

# Create scenario with all 120 products
all_products = pd.DataFrame({
    'Producing country ISO*': ['USA'] * 120,
    'Consuming country ISO*': ['USA'] * 120,
    'Product code*': [str(i) for i in range(1, 121)],  # "1", "2", ..., "120"
    'FD code*': ['FD_4'] * 120,
    'Value*': [1000000] * 120,  # $1M each
    'Type*': ['abs-b'] * 120
})

print(f"Created scenario with {len(all_products)} rows")
print(f"Total investment: ${all_products['Value*'].sum():,.0f}")
print(f"Investment per product: ${all_products['Value*'].iloc[0]:,.0f}")

# Create Scenarios directory if needed
scenarios_dir = "GLORIA_template/Scenarios"
if not os.path.exists(scenarios_dir):
    os.makedirs(scenarios_dir)
    print(f"✓ Created directory: {scenarios_dir}")

# Save scenario file
test_file = os.path.join(scenarios_dir, "Test_AllProducts_1M_USA.xlsx")
all_products.to_excel(test_file, index=False, sheet_name='Final demand')

print(f"\n✓ Created: {test_file}")
print(f"  This scenario invests $1M in EACH of 120 products")
print(f"  Run this to get employment multipliers for all products")
print(f"  Perfect for comparing sectors!")

# =============================================================================
# PART 11: CREATE SIMPLE CONSTRUCTION EXAMPLE
# =============================================================================

print("\n" + "-"*60)
print("STEP 10: Creating simple construction test")
print("-"*60)

"""
Purpose:
Create a simple single-sector test scenario

This is a basic test:
- $100M investment in construction (product 56)
- In the United States
- Quick test to verify everything works

In R:
    construction <- data.frame(
        producing_country = "USA",
        consuming_country = "USA",
        product = 56,
        category = "FD_4",
        amount = 100000000,
        type = "abs-b"
    )
"""

# Single-row scenario
construction = pd.DataFrame({
    'Producing country ISO*': ['USA'],
    'Consuming country ISO*': ['USA'],
    'Product code*': ['56'],  # Construction
    'FD code*': ['FD_4'],     # Investment
    'Value*': [100000000],    # $100M
    'Type*': ['abs-b']        # Absolute amount
})

print("Construction scenario:")
print(construction.to_string(index=False))

# Save
construction_file = os.path.join(scenarios_dir, "Test_Construction_100M_USA.xlsx")
construction.to_excel(construction_file, index=False, sheet_name='Final demand')

print(f"\n✓ Created: {construction_file}")
print(f"  Simple test: $100M infrastructure investment")
print(f"  Use this to verify the employment script works")

# =============================================================================
# PART 12: SUMMARY AND NEXT STEPS
# =============================================================================

print("\n" + "="*60)
print("SUCCESS! ALL FILES CREATED")
print("="*60)

print("\n📁 FILES CREATED:")
print("\n1. REFERENCE FILES (in Claude Code/temp/):")
print(f"   ✓ GLORIA_Products_Reference.xlsx ({len(products)} products)")
print(f"   ✓ GLORIA_Regions_Reference.xlsx ({len(regions)} regions)")
print(f"   ✓ SCENARIO_TEMPLATE_SIMPLE.xlsx (editable template)")

print("\n2. READY-TO-RUN SCENARIOS (in GLORIA_template/Scenarios/):")
print(f"   ✓ Test_Construction_100M_USA.xlsx")
print(f"      → Simple test with 1 product")
print(f"   ✓ Test_AllProducts_1M_USA.xlsx")
print(f"      → Tests all 120 products at once")
print(f"      → Perfect for your dissertation!")

print("\n" + "="*60)
print("WHAT THESE FILES DO:")
print("="*60)

print("\n📊 UNDERSTANDING THE WORKFLOW:")
print("""
Your employment analysis follows this process:

1. SCENARIO FILE (what you just created)
   ↓
   Specifies: Which products get demand shock (dY)

2. EMPLOYMENT SCRIPT (RunMINDSET_EmploymentOnly.py)
   ↓
   Calculates:
   - Output change (dX = L × dY) using Leontief inverse
   - Employment change (dE = e × dX) using employment coefficients

3. RESULTS FILE (Excel output)
   ↓
   Shows:
   - Jobs created by region
   - Jobs created by sector
   - Employment multiplier (jobs per $1M invested)
""")

print("\n" + "="*60)
print("NEXT STEPS - RUNNING THE ANALYSIS:")
print("="*60)

print("\n1️⃣  TEST RUN (verify everything works):")
print("   • Open: RunMINDSET_EmploymentOnly.py")
print("   • Line 103: scenario_name = 'Test_Construction_100M_USA'")
print("   • Press: Ctrl+Shift+Enter")
print("   • Wait: 5-10 minutes")
print("   • Check: GLORIA_results/Results_Test_Construction_100M_USA_EmploymentOnly.xlsx")

print("\n2️⃣  FULL ANALYSIS (all 120 products):")
print("   • Line 103: scenario_name = 'Test_AllProducts_1M_USA'")
print("   • Press: Ctrl+Shift+Enter")
print("   • Result: Employment multipliers for ALL 120 products!")

print("\n3️⃣  CUSTOM ANALYSIS (your own scenarios):")
print("   • Open: SCENARIO_TEMPLATE_SIMPLE.xlsx")
print("   • Edit to specify your own demand shocks")
print("   • Save as: GLORIA_template/Scenarios/YourScenarioName.xlsx")
print("   • Run with: scenario_name = 'YourScenarioName'")

print("\n" + "="*60)
print("FOR YOUR RESEARCH TEAM:")
print("="*60)

print("""
Key points to explain:

1. GLORIA DATABASE:
   - 120 products × 162 regions = 19,440 sector-regions
   - Contains input-output relationships between all sectors
   - Employment coefficients for each sector-region

2. SCENARIO FILES:
   - Excel files that specify demand shocks (dY)
   - Each row = one demand shock specification
   - Can specify single products or multiple products
   - Can use ranges (1-10) or lists (1,5,10) or ALL

3. EMPLOYMENT MODEL:
   - Based on Leontief input-output framework
   - Calculates direct + indirect + induced effects
   - Output: Jobs created per dollar invested

4. RESULTS:
   - Excel files with multiple sheets
   - Employment by region, by sector, detailed breakdown
   - Employment multiplier (jobs per $1M)
""")

print("\n" + "="*60)
print("All done! Ready to run employment analysis! 🎉")
print("="*60)
